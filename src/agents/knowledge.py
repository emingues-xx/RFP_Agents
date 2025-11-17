"""Agente Conhecimento - Gera respostas baseadas em conhecimento."""
from typing import List, Dict, Any, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from src.workflows.schema import GeneratedResponse
from src.utils.metrics import (
    knowledge_queries_total,
    knowledge_retrieval_duration_seconds,
    knowledge_response_quality
)
import json
import time
import logging

logger = logging.getLogger(__name__)


class KnowledgeAgent:
    """Agente Conhecimento para geração de respostas."""
    
    def __init__(
        self,
        llm: BaseChatModel,
        vector_store: Optional[VectorStore] = None
    ):
        """Inicializar Agente Conhecimento."""
        self.llm = llm
        self.vector_store = vector_store
        self._setup_system_prompt()
        logger.info("KnowledgeAgent inicializado")
    
    def _setup_system_prompt(self) -> None:
        """Configurar prompt do sistema."""
        self.system_prompt = """Você é um Agente Conhecimento especializado em gerar respostas precisas baseadas em documentos técnicos.
Sua função é:
1. Consultar base de conhecimento via RAG
2. Gerar respostas com citações de origem
3. Identificar parâmetros variáveis (SLAs, versões, escopos)
4. Identificar campos que exigem input humano (ex: preços, datas específicas)

Sempre responda em formato JSON estruturado."""
    
    def retrieve_documents(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 5
    ) -> List[Document]:
        """Recuperar documentos relevantes."""
        start_time = time.time()
        
        if not self.vector_store:
            logger.warning("Vector store não configurado, retornando lista vazia")
            knowledge_retrieval_duration_seconds.observe(time.time() - start_time)
            return []
        
        try:
            # Aplicar filtro por categoria se especificado
            search_kwargs = {"k": top_k}
            if category:
                search_kwargs["filter"] = {"category": category}
            
            docs = self.vector_store.similarity_search(
                query,
                k=top_k,
                **search_kwargs
            )
            
            duration = time.time() - start_time
            knowledge_retrieval_duration_seconds.observe(duration)
            
            logger.info(f"Recuperados {len(docs)} documentos para query: {query[:50]}...")
            return docs
            
        except Exception as e:
            duration = time.time() - start_time
            knowledge_retrieval_duration_seconds.observe(duration)
            
            logger.error(f"Erro ao recuperar documentos: {e}")
            knowledge_queries_total.labels(
                category=category or "unknown",
                status="error"
            ).inc()
            return []
    
    def generate_response(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        qid: Optional[str] = None
    ) -> GeneratedResponse:
        """Gerar resposta para pergunta."""
        logger.info(f"Gerando resposta para pergunta: {question[:50]}...")
        
        start_time = time.time()
        
        try:
            # Recuperar documentos relevantes
            category = context.get("category") if context else None
            docs = self.retrieve_documents(question, category=category)
            
            # Construir contexto dos documentos
            if docs:
                context_text = "\n\n".join([
                    f"[Documento {i+1}]: {doc.page_content[:500]}\nFonte: {doc.metadata.get('source', 'unknown')}"
                    for i, doc in enumerate(docs)
                ])
            else:
                context_text = "Nenhum documento relevante encontrado na base de conhecimento."
                logger.warning("Nenhum documento recuperado para a query")
            
            # Construir prompt
            context_info = ""
            if context:
                context_info = f"""
Cliente: {context.get('client', 'N/A')}
Produto: {context.get('product', 'N/A')}
Prazos: {context.get('deadlines', 'N/A')}"""
            
            prompt = f"""Com base nos seguintes documentos da base de conhecimento, responda à pergunta:

Documentos:
{context_text}

Pergunta: {question}
{context_info}

Gere uma resposta que:
1. Seja precisa e baseada nos documentos fornecidos
2. Inclua citações das fontes (use [1], [2], etc. para referenciar os documentos)
3. Identifique parâmetros variáveis que podem precisar ser ajustados (SLAs, versões, escopos, etc.)
4. Indique claramente se algum campo requer input humano (ex: preços, datas específicas, informações do cliente)

Responda APENAS com um JSON válido, sem texto adicional:
{{
    "response_text": "Resposta completa com citações [1], [2], etc.",
    "confidence_score": 0.0-1.0,
    "citations": ["fonte1", "fonte2"],
    "requires_human_input": false,
    "human_input_fields": []
}}"""
            
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Extrair JSON
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
                
                generated_response = GeneratedResponse(
                    qid=qid or "unknown",
                    response_text=result.get("response_text", ""),
                    confidence_score=result.get("confidence_score", 0.0),
                    citations=result.get("citations", []),
                    requires_human_input=result.get("requires_human_input", False),
                    human_input_fields=result.get("human_input_fields", [])
                )
                
                # Métricas
                duration = time.time() - start_time
                knowledge_queries_total.labels(
                    category=category or "unknown",
                    status="success"
                ).inc()
                knowledge_response_quality.observe(generated_response.confidence_score)
                
                logger.info(f"Resposta gerada com confiança {generated_response.confidence_score:.2f}")
                return generated_response
            else:
                raise ValueError("JSON não encontrado na resposta")
                
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao fazer parse do JSON: {e}")
            logger.debug(f"Resposta recebida: {content[:500]}")
            
            knowledge_queries_total.labels(
                category=category or "unknown",
                status="error"
            ).inc()
            
            return GeneratedResponse(
                qid=qid or "unknown",
                response_text="Erro ao gerar resposta: formato JSON inválido",
                confidence_score=0.0
            )
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            
            knowledge_queries_total.labels(
                category=category or "unknown",
                status="error"
            ).inc()
            
            return GeneratedResponse(
                qid=qid or "unknown",
                response_text=f"Erro ao gerar resposta: {str(e)}",
                confidence_score=0.0
            )
    
    def generate_responses(
        self,
        questions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[GeneratedResponse]:
        """Gerar respostas para múltiplas perguntas."""
        logger.info(f"Gerando respostas para {len(questions)} perguntas")
        
        responses = []
        for q_data in questions:
            question = q_data.get("question_text", "")
            qid = q_data.get("qid", "")
            category = q_data.get("category")
            
            # Adicionar categoria ao contexto se disponível
            q_context = context.copy() if context else {}
            if category:
                q_context["category"] = category
            
            response = self.generate_response(
                question=question,
                context=q_context,
                qid=qid
            )
            responses.append(response)
        
        logger.info(f"Geradas {len(responses)} respostas")
        return responses
    
    def retrieve_from_multiple_bases(
        self,
        query: str,
        categories: Optional[List[str]] = None
    ) -> Dict[str, List[Document]]:
        """Recuperar de múltiplas bases de conhecimento."""
        categories = categories or ["técnico", "segurança", "compliance", "jurídico"]
        results = {}
        
        logger.info(f"Recuperando de {len(categories)} bases: {categories}")
        
        for category in categories:
            docs = self.retrieve_documents(query, category=category)
            results[category] = docs
        
        return results
    
    def consult_historical_rfps(
        self,
        question: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Consultar RFPs históricas com perguntas similares."""
        logger.info(f"Consultando RFPs históricas para: {question[:50]}...")
        
        # TODO: Implementar busca no vector store de RFPs históricas
        # Por enquanto, retornar estrutura básica
        # Quando o vector store de RFPs estiver disponível, usar:
        # historical_store = VectorStoreManager(collection_name="rfp_history")
        # docs = historical_store.similarity_search(question, k=top_k)
        
        return []

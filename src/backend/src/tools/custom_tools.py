"""Custom tools para agentes."""
from langchain_core.tools import tool
from typing import Optional
import logging
import json

logger = logging.getLogger(__name__)

# Importar métricas
from src.utils.metrics import tool_usage_total


def _track_tool_usage(tool_name: str, status: str = "success"):
    """Rastrear uso de tool."""
    tool_usage_total.labels(tool_name=tool_name, status=status).inc()


@tool
def extract_text_tool(file_path: str, file_type: Optional[str] = None) -> str:
    """Extrair texto de arquivo (PDF, DOCX, Excel, CSV).
    
    Args:
        file_path: Caminho do arquivo
        file_type: Tipo do arquivo (opcional, detecta automaticamente)
    
    Returns:
        Texto extraído do arquivo
    """
    try:
        from src.agents.parser import ParserAgent
        from src.utils.llm_factory import LLMFactory
        
        # Criar LLM temporário (não será usado para extração, mas é obrigatório)
        factory = LLMFactory()
        llm = factory.get_default_llm()
        parser = ParserAgent(llm=llm)
        
        # Detectar tipo de arquivo se não fornecido
        if not file_type:
            from pathlib import Path
            extension = Path(file_path).suffix.lower()
            if extension == ".pdf":
                file_type = "pdf"
            elif extension in [".docx", ".doc"]:
                file_type = "docx"
            elif extension in [".xlsx", ".xls"]:
                file_type = "excel"
            elif extension == ".csv":
                file_type = "csv"
        
        # Extrair texto
        if file_type == "pdf" or file_path.endswith(".pdf"):
            text = parser.extract_from_pdf(file_path)
        elif file_type == "docx" or file_path.endswith((".docx", ".doc")):
            text = parser.extract_from_docx(file_path)
        elif file_type == "excel" or file_path.endswith((".xlsx", ".xls")):
            text = parser.extract_from_excel(file_path)
        elif file_type == "csv" or file_path.endswith(".csv"):
            text = parser.extract_from_csv(file_path)
        else:
            text = parser.extract_from_file(file_path)
        
        _track_tool_usage("extract_text_tool", "success")
        logger.info(f"Texto extraído de {file_path}: {len(text)} caracteres")
        return text
        
    except Exception as e:
        _track_tool_usage("extract_text_tool", "error")
        logger.error(f"Erro ao extrair texto: {e}")
        return f"Erro ao extrair texto: {str(e)}"


@tool
def ocr_tool(image_path: str, language: str = "por") -> str:
    """Aplicar OCR em imagem para extrair texto.
    
    Args:
        image_path: Caminho da imagem
        language: Idioma (por padrão: português)
    
    Returns:
        Texto extraído da imagem
    """
    try:
        from PIL import Image
        import pytesseract
        
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=language)
        
        _track_tool_usage("ocr_tool", "success")
        logger.info(f"OCR aplicado em {image_path}: {len(text)} caracteres")
        return text
        
    except ImportError:
        _track_tool_usage("ocr_tool", "error")
        error_msg = "OCR não disponível (PIL/pytesseract não instalado)"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        _track_tool_usage("ocr_tool", "error")
        logger.error(f"Erro no OCR: {e}")
        return f"Erro no OCR: {str(e)}"


@tool
def rag_query_tool(
    query: str,
    category: Optional[str] = None,
    top_k: int = 5
) -> str:
    """Consultar base de conhecimento via RAG.
    
    Args:
        query: Query de busca
        category: Categoria (técnico, segurança, compliance, jurídico)
        top_k: Número de documentos a retornar
    
    Returns:
        Resumo dos documentos encontrados com citações
    """
    try:
        from src.rag.vector_store import VectorStoreManager
        
        vector_store = VectorStoreManager()
        filter_dict = {"category": category} if category else None
        docs = vector_store.similarity_search(
            query,
            k=top_k,
            filter=filter_dict
        )
        
        if not docs:
            _track_tool_usage("rag_query_tool", "success")
            return "Nenhum documento encontrado."
        
        result = f"Encontrados {len(docs)} documentos relevantes:\n\n"
        for i, doc in enumerate(docs, 1):
            content_preview = doc.page_content[:200]
            if len(doc.page_content) > 200:
                content_preview += "..."
            result += f"[{i}] {content_preview}\n"
            result += f"Fonte: {doc.metadata.get('source', 'unknown')}\n"
            if doc.metadata.get('category'):
                result += f"Categoria: {doc.metadata.get('category')}\n"
            result += "\n"
        
        _track_tool_usage("rag_query_tool", "success")
        return result
        
    except Exception as e:
        _track_tool_usage("rag_query_tool", "error")
        logger.error(f"Erro na consulta RAG: {e}")
        return f"Erro na consulta RAG: {str(e)}"


@tool
def compliance_validation_tool(response_text: str) -> str:
    """Validar compliance de resposta.
    
    Args:
        response_text: Texto da resposta a validar
    
    Returns:
        Resultado da validação em formato JSON
    """
    try:
        from src.agents.verifier import VerifierAgent
        from src.utils.llm_factory import LLMFactory
        from src.workflows.schema import GeneratedResponse
        
        # Criar LLM para verifier
        factory = LLMFactory()
        llm = factory.get_default_llm()
        verifier = VerifierAgent(llm=llm)
        
        # Criar resposta temporária para validação
        response = GeneratedResponse(
            qid="validation",
            response_text=response_text,
            confidence_score=0.0
        )
        
        verified = verifier.verify("", response)
        
        result = {
            "has_prohibited_terms": verified.has_prohibited_terms,
            "has_gaps": verified.has_gaps,
            "needs_review": verified.needs_review,
            "confidence_score": verified.confidence_score,
            "is_consistent": verified.is_consistent,
            "validation_errors": verified.validation_errors
        }
        
        _track_tool_usage("compliance_validation_tool", "success")
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        _track_tool_usage("compliance_validation_tool", "error")
        logger.error(f"Erro na validação: {e}")
        return json.dumps({"error": str(e)}, indent=2)


@tool
def map_similar_questions_tool(question: str, top_k: int = 5) -> str:
    """Mapear pergunta para perguntas similares no histórico.
    
    Args:
        question: Pergunta a mapear
        top_k: Número de perguntas similares a retornar
    
    Returns:
        Lista de perguntas similares com scores
    """
    try:
        from src.rag.vector_store import VectorStoreManager
        
        vector_store = VectorStoreManager()
        
        # Buscar em coleção de perguntas históricas
        # Usar filtro para buscar apenas perguntas
        docs = vector_store.similarity_search(
            question,
            k=top_k,
            filter={"type": "question"}
        )
        
        if not docs:
            _track_tool_usage("map_similar_questions_tool", "success")
            return "Nenhuma pergunta similar encontrada."
        
        result = f"Encontradas {len(docs)} perguntas similares:\n\n"
        for i, doc in enumerate(docs, 1):
            result += f"[{i}] {doc.page_content}\n"
            # Tentar obter score se disponível (pode não estar nos metadados)
            score = doc.metadata.get('score', 'N/A')
            if score != 'N/A':
                result += f"Score: {score:.4f}\n"
            else:
                result += f"Fonte: {doc.metadata.get('source', 'unknown')}\n"
            result += "\n"
        
        _track_tool_usage("map_similar_questions_tool", "success")
        return result
        
    except Exception as e:
        _track_tool_usage("map_similar_questions_tool", "error")
        logger.error(f"Erro no mapeamento: {e}")
        return f"Erro no mapeamento: {str(e)}"

# Tarefa 3.2: Agente Conhecimento & Redação

## Objetivo
Implementar o Agente Conhecimento que consulta base de conhecimento via RAG e gera respostas contextualizadas com citações.

## Prioridade
Alta

## Estimativa
5 dias

## Responsável
Backend

---

## Instruções de Implementação

### 1. Criar Classe Base do Agente Conhecimento

#### Criar `src/agents/knowledge.py`:
```python
"""Agente Conhecimento - Gera respostas baseadas em conhecimento."""
from typing import List, Dict, Any, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.vectorstores import VectorStore
from src.workflows.schema import GeneratedResponse
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
    
    def _setup_system_prompt(self) -> None:
        """Configurar prompt do sistema."""
        self.system_prompt = """Você é um Agente Conhecimento especializado em gerar respostas precisas baseadas em documentos técnicos.
Sua função é:
1. Consultar base de conhecimento via RAG
2. Gerar respostas com citações de origem
3. Identificar parâmetros variáveis
4. Identificar campos que exigem input humano"""
```

### 2. Implementar Integração com RAG

#### Adicionar métodos de retrieval:
```python
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document

def retrieve_documents(
    self,
    query: str,
    category: Optional[str] = None,
    top_k: int = 5
) -> List[Document]:
    """Recuperar documentos relevantes."""
    if not self.vector_store:
        logger.warning("Vector store não configurado")
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
        
        logger.info(f"Recuperados {len(docs)} documentos para query: {query[:50]}...")
        return docs
    except Exception as e:
        logger.error(f"Erro ao recuperar documentos: {e}")
        return []
```

### 3. Implementar Geração de Respostas

#### Adicionar método de geração:
```python
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import json

def generate_response(
    self,
    question: str,
    context: Optional[Dict[str, Any]] = None,
    qid: Optional[str] = None
) -> GeneratedResponse:
    """Gerar resposta para pergunta."""
    # Recuperar documentos relevantes
    docs = self.retrieve_documents(question)
    
    # Construir contexto dos documentos
    context_text = "\n\n".join([
        f"[Documento {i+1}]: {doc.page_content}\nFonte: {doc.metadata.get('source', 'unknown')}"
        for i, doc in enumerate(docs)
    ])
    
    # Construir prompt
    prompt = f"""Com base nos seguintes documentos, responda à pergunta:

Documentos:
{context_text}

Pergunta: {question}

Contexto adicional: {context or {}}

Gere uma resposta que:
1. Seja precisa e baseada nos documentos
2. Inclua citações das fontes (use [1], [2], etc.)
3. Identifique parâmetros variáveis (SLAs, versões, etc.)
4. Indique se algum campo requer input humano

Responda em JSON:
{{
    "response_text": "...",
    "confidence_score": 0.0-1.0,
    "citations": ["fonte1", "fonte2"],
    "requires_human_input": false,
    "human_input_fields": []
}}"""
    
    messages = [
        SystemMessage(content=self.system_prompt),
        HumanMessage(content=prompt)
    ]
    
    try:
        response = self.llm.invoke(messages)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Extrair JSON
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = content[json_start:json_end]
            result = json.loads(json_str)
            
            return GeneratedResponse(
                qid=qid or "unknown",
                response_text=result.get("response_text", ""),
                confidence_score=result.get("confidence_score", 0.0),
                citations=result.get("citations", []),
                requires_human_input=result.get("requires_human_input", False),
                human_input_fields=result.get("human_input_fields", [])
            )
        else:
            raise ValueError("JSON não encontrado na resposta")
    except Exception as e:
        logger.error(f"Erro ao gerar resposta: {e}")
        return GeneratedResponse(
            qid=qid or "unknown",
            response_text="Erro ao gerar resposta",
            confidence_score=0.0
        )
```

### 4. Implementar Suporte a Múltiplas Bases

#### Adicionar método:
```python
def retrieve_from_multiple_bases(
    self,
    query: str,
    categories: List[str] = None
) -> Dict[str, List[Document]]:
    """Recuperar de múltiplas bases de conhecimento."""
    categories = categories or ["técnico", "segurança", "compliance", "jurídico"]
    results = {}
    
    for category in categories:
        docs = self.retrieve_documents(query, category=category)
        results[category] = docs
    
    return results
```

### 5. Implementar Consulta a RFPs Históricas

#### Adicionar método:
```python
def consult_historical_rfps(
    self,
    question: str,
    top_k: int = 3
) -> List[Dict[str, Any]]:
    """Consultar RFPs históricas com perguntas similares."""
    # TODO: Implementar busca no vector store de RFPs históricas
    # Por enquanto, retornar estrutura básica
    return []
```

### 6. Integrar com LangChain Agent

#### Criar tool:
```python
from langchain_core.tools import tool

@tool
def knowledge_query_tool(question: str, category: str = None) -> str:
    """Consultar base de conhecimento e gerar resposta."""
    # Implementar chamada ao KnowledgeAgent
    pass
```

### 7. Adicionar Métricas

#### Atualizar métricas:
```python
# Métricas de Knowledge
knowledge_queries_total = Counter(
    'knowledge_queries_total',
    'Total de queries de conhecimento',
    ['category', 'status']
)

knowledge_retrieval_duration_seconds = Histogram(
    'knowledge_retrieval_duration_seconds',
    'Duração de retrieval em segundos'
)

knowledge_response_quality = Histogram(
    'knowledge_response_quality',
    'Score de qualidade das respostas',
    buckets=(0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0)
)
```

### 8. Criar Testes

#### Criar `tests/unit/test_knowledge.py`:
```python
"""Testes para Agente Conhecimento."""
import pytest
from src.agents.knowledge import KnowledgeAgent
from unittest.mock import Mock, MagicMock

@pytest.fixture
def knowledge_agent():
    llm = Mock()
    vector_store = MagicMock()
    return KnowledgeAgent(llm=llm, vector_store=vector_store)

def test_generate_response(knowledge_agent):
    """Testar geração de resposta."""
    pass

def test_retrieve_documents(knowledge_agent):
    """Testar retrieval."""
    pass
```

---

## Checklist de Validação

- [ ] Classe base do Agente Conhecimento criada
- [ ] Integração com RAG implementada
- [ ] Geração de respostas com citações funcionando
- [ ] Suporte a múltiplas bases de conhecimento
- [ ] Consulta a RFPs históricas implementada
- [ ] Integração com LangChain Agent
- [ ] Métricas adicionadas
- [ ] Testes unitários criados e passando
- [ ] Documentação criada

---

## Comandos de Teste

```bash
# Testar geração de resposta
python -m pytest tests/unit/test_knowledge.py::test_generate_response

# Testar retrieval
python -m pytest tests/unit/test_knowledge.py::test_retrieve_documents
```


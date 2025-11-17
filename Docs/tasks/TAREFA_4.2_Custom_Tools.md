# Tarefa 4.2: Custom Tools Básicas

## Objetivo
Implementar custom tools para processamento de documentos, OCR, consulta RAG, validação de compliance e mapeamento de perguntas similares.

## Prioridade
Alta

## Estimativa
4 dias

## Responsável
Backend

---

## Instruções de Implementação

### 1. Criar Estrutura Base para Custom Tools

#### Atualizar `src/tools/custom_tools.py`:
```python
"""Custom tools para agentes."""
from langchain_core.tools import tool
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)
```

### 2. Tool de Extração de Texto

#### Adicionar tool:
```python
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
        from unittest.mock import Mock
        
        parser = ParserAgent(llm=Mock())  # Não precisa LLM para extração
        
        if file_type == "pdf" or file_path.endswith(".pdf"):
            return parser.extract_from_pdf(file_path)
        elif file_type == "docx" or file_path.endswith(".docx"):
            return parser.extract_from_docx(file_path)
        elif file_type == "excel" or file_path.endswith((".xlsx", ".xls")):
            return parser.extract_from_excel(file_path)
        elif file_type == "csv" or file_path.endswith(".csv"):
            return parser.extract_from_csv(file_path)
        else:
            return parser.extract_from_file(file_path)
    except Exception as e:
        logger.error(f"Erro ao extrair texto: {e}")
        return f"Erro ao extrair texto: {str(e)}"
```

### 3. Tool de OCR

#### Adicionar tool:
```python
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
        
        logger.info(f"OCR aplicado em {image_path}: {len(text)} caracteres")
        return text
    except Exception as e:
        logger.error(f"Erro no OCR: {e}")
        return f"Erro no OCR: {str(e)}"
```

### 4. Tool de Consulta RAG

#### Adicionar tool:
```python
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
        docs = vector_store.similarity_search(
            query,
            k=top_k,
            filter={"category": category} if category else None
        )
        
        if not docs:
            return "Nenhum documento encontrado."
        
        result = f"Encontrados {len(docs)} documentos relevantes:\n\n"
        for i, doc in enumerate(docs, 1):
            result += f"[{i}] {doc.page_content[:200]}...\n"
            result += f"Fonte: {doc.metadata.get('source', 'unknown')}\n\n"
        
        return result
    except Exception as e:
        logger.error(f"Erro na consulta RAG: {e}")
        return f"Erro na consulta RAG: {str(e)}"
```

### 5. Tool de Validação de Compliance

#### Adicionar tool:
```python
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
        from unittest.mock import Mock
        from src.workflows.schema import GeneratedResponse
        
        verifier = VerifierAgent(llm=Mock())
        
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
            "confidence_score": verified.confidence_score
        }
        
        import json
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Erro na validação: {e}")
        return f"Erro na validação: {str(e)}"
```

### 6. Tool de Mapeamento de Perguntas Similares

#### Adicionar tool:
```python
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
        docs = vector_store.similarity_search(
            question,
            k=top_k,
            filter={"type": "question"}
        )
        
        if not docs:
            return "Nenhuma pergunta similar encontrada."
        
        result = f"Encontradas {len(docs)} perguntas similares:\n\n"
        for i, doc in enumerate(docs, 1):
            result += f"[{i}] {doc.page_content}\n"
            result += f"Score: {doc.metadata.get('score', 'N/A')}\n\n"
        
        return result
    except Exception as e:
        logger.error(f"Erro no mapeamento: {e}")
        return f"Erro no mapeamento: {str(e)}"
```

### 7. Registrar Todas as Tools no LangChain

#### Criar `src/tools/__init__.py`:
```python
"""Tools do sistema."""
from src.tools.custom_tools import (
    extract_text_tool,
    ocr_tool,
    rag_query_tool,
    compliance_validation_tool,
    map_similar_questions_tool
)

__all__ = [
    "extract_text_tool",
    "ocr_tool",
    "rag_query_tool",
    "compliance_validation_tool",
    "map_similar_questions_tool"
]

# Lista de todas as tools
ALL_TOOLS = [
    extract_text_tool,
    ocr_tool,
    rag_query_tool,
    compliance_validation_tool,
    map_similar_questions_tool
]
```

### 8. Documentar Cada Tool

#### Criar `docs/tools/custom_tools.md`:
```markdown
# Custom Tools

## extract_text_tool
Extrai texto de arquivos (PDF, DOCX, Excel, CSV).

## ocr_tool
Aplica OCR em imagens para extrair texto.

## rag_query_tool
Consulta base de conhecimento via RAG.

## compliance_validation_tool
Valida compliance de respostas.

## map_similar_questions_tool
Mapeia perguntas para similares no histórico.
```

### 9. Criar Testes

#### Criar `tests/unit/test_tools.py`:
```python
"""Testes para custom tools."""
import pytest
from src.tools.custom_tools import (
    extract_text_tool,
    rag_query_tool
)

def test_extract_text_tool():
    """Testar extração de texto."""
    # Criar arquivo de teste
    pass

def test_rag_query_tool():
    """Testar consulta RAG."""
    result = rag_query_tool.invoke({"query": "SLA"})
    assert result is not None
```

### 10. Adicionar Métricas de Uso

#### Atualizar `src/utils/metrics.py`:
```python
# Métricas de Tools
tool_usage_total = Counter(
    'tool_usage_total',
    'Total de uso de tools',
    ['tool_name', 'status']
)
```

---

## Checklist de Validação

- [ ] Estrutura base para custom tools criada
- [ ] Tool de extração de texto implementada
- [ ] Tool de OCR implementada
- [ ] Tool de consulta RAG implementada
- [ ] Tool de validação de compliance implementada
- [ ] Tool de mapeamento de perguntas similares implementada
- [ ] Todas as tools registradas no LangChain
- [ ] Documentação de cada tool criada
- [ ] Testes para cada tool criados
- [ ] Métricas de uso adicionadas

---

## Comandos de Teste

```bash
# Testar tools
python -m pytest tests/unit/test_tools.py

# Testar tool específica
python -m pytest tests/unit/test_tools.py::test_extract_text_tool
```


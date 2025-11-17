# Tarefa 3.1: Agente Parser & Mapeador de Questionários

## Objetivo
Implementar o Agente Parser que extrai e normaliza perguntas de diferentes formatos de entrada (PDF, DOCX, planilhas) e mapeia para perguntas históricas.

## Prioridade
Alta

## Estimativa
5 dias

## Responsável
Backend

---

## Instruções de Implementação

### 1. Criar Classe Base do Agente Parser

#### Criar `src/agents/parser.py`:
```python
"""Agente Parser - Extrai e normaliza perguntas de questionários."""
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain_core.language_models import BaseChatModel
from src.workflows.schema import ParsedQuestion
import logging

logger = logging.getLogger(__name__)


class ParserAgent:
    """Agente Parser para extração e normalização de perguntas."""
    
    def __init__(self, llm: BaseChatModel):
        """Inicializar Agente Parser."""
        self.llm = llm
        self._setup_system_prompt()
    
    def _setup_system_prompt(self) -> None:
        """Configurar prompt do sistema."""
        self.system_prompt = """Você é um Agente Parser especializado em extrair e normalizar perguntas de questionários.
Sua função é:
1. Extrair perguntas de diferentes formatos
2. Normalizar em formato canônico
3. Identificar categoria e requisitos
4. Mapear para perguntas similares do histórico"""
    
    def extract_from_file(self, file_path: str) -> str:
        """Extrair texto de arquivo."""
        # Implementar extração baseada em extensão
        pass
    
    def normalize_questions(self, raw_text: str) -> List[ParsedQuestion]:
        """Normalizar perguntas em formato canônico."""
        # Implementar normalização
        pass
    
    def map_to_historical(self, questions: List[ParsedQuestion]) -> List[Dict[str, Any]]:
        """Mapear perguntas para histórico."""
        # Implementar mapeamento
        pass
```

### 2. Implementar Extração de PDF

#### Adicionar métodos em `parser.py`:
```python
import PyPDF2
import pdfplumber
from PIL import Image
import pytesseract

def extract_from_pdf(self, file_path: str, use_ocr: bool = False) -> str:
    """Extrair texto de PDF."""
    text_content = []
    
    try:
        # Tentar extração direta primeiro
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        
        # Se texto vazio e OCR habilitado, usar OCR
        if not text_content and use_ocr:
            text_content = self._extract_with_ocr(file_path)
        
        return "\n".join(text_content)
    except Exception as e:
        logger.error(f"Erro ao extrair PDF: {e}")
        raise

def _extract_with_ocr(self, file_path: str) -> List[str]:
    """Extrair texto usando OCR."""
    # Implementar OCR com Tesseract
    pass
```

### 3. Implementar Extração de DOCX

#### Adicionar método:
```python
from docx import Document

def extract_from_docx(self, file_path: str) -> str:
    """Extrair texto de DOCX."""
    try:
        doc = Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        logger.error(f"Erro ao extrair DOCX: {e}")
        raise
```

### 4. Implementar Extração de Planilhas

#### Adicionar métodos:
```python
import pandas as pd
import openpyxl

def extract_from_excel(self, file_path: str) -> str:
    """Extrair texto de Excel."""
    try:
        df = pd.read_excel(file_path, sheet_name=None)
        text_parts = []
        for sheet_name, sheet_df in df.items():
            text_parts.append(f"Sheet: {sheet_name}")
            text_parts.append(sheet_df.to_string())
        return "\n".join(text_parts)
    except Exception as e:
        logger.error(f"Erro ao extrair Excel: {e}")
        raise

def extract_from_csv(self, file_path: str) -> str:
    """Extrair texto de CSV."""
    try:
        df = pd.read_csv(file_path)
        return df.to_string()
    except Exception as e:
        logger.error(f"Erro ao extrair CSV: {e}")
        raise
```

### 5. Implementar Normalização em Formato Canônico

#### Adicionar método de normalização:
```python
from langchain_core.messages import HumanMessage, SystemMessage
import json
import re

def normalize_questions(self, raw_text: str) -> List[ParsedQuestion]:
    """Normalizar perguntas em formato canônico."""
    prompt = f"""Extraia e normalize as seguintes perguntas em formato JSON:
- QID: Identificador único (ex: Q001, Q002)
- category: Categoria (técnico, segurança, compliance, jurídico, comercial)
- question_text: Texto da pergunta normalizado
- requirements: Lista de requisitos mencionados
- expected_format: Formato esperado (texto, número, sim/não, lista, etc.)

Texto: {raw_text}

Responda em JSON array:
[{{"qid": "Q001", "category": "...", "question_text": "...", "requirements": [...], "expected_format": "..."}}]"""
    
    messages = [
        SystemMessage(content=self.system_prompt),
        HumanMessage(content=prompt)
    ]
    
    try:
        response = self.llm.invoke(messages)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Extrair JSON
        json_start = content.find('[')
        json_end = content.rfind(']') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = content[json_start:json_end]
            questions_data = json.loads(json_str)
            
            return [ParsedQuestion(**q) for q in questions_data]
        else:
            raise ValueError("JSON não encontrado na resposta")
    except Exception as e:
        logger.error(f"Erro ao normalizar perguntas: {e}")
        return []
```

### 6. Implementar Mapeamento para Perguntas Históricas

#### Adicionar método:
```python
def map_to_historical(
    self, 
    questions: List[ParsedQuestion],
    historical_questions: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """Mapear perguntas para histórico usando similaridade semântica."""
    # TODO: Implementar busca semântica no vector store
    # Por enquanto, retornar estrutura básica
    mapped = []
    for q in questions:
        mapped.append({
            "qid": q.qid,
            "question": q.question_text,
            "similar_questions": q.similar_questions,
            "mapping_confidence": 0.0  # Será calculado com vector search
        })
    return mapped
```

### 7. Integrar com LangChain como Tool

#### Criar `src/tools/parser_tool.py`:
```python
from langchain_core.tools import tool
from src.agents.parser import ParserAgent

@tool
def parse_questionnaire_tool(file_path: str, use_ocr: bool = False) -> str:
    """Extrair e normalizar perguntas de questionário."""
    # Implementar chamada ao ParserAgent
    pass
```

### 8. Adicionar Métricas

#### Atualizar `src/utils/metrics.py`:
```python
# Métricas de Parser
parser_extractions_total = Counter(
    'parser_extractions_total',
    'Total de extrações de documentos',
    ['file_type', 'status']
)

parser_extraction_duration_seconds = Histogram(
    'parser_extraction_duration_seconds',
    'Duração de extração em segundos',
    ['file_type']
)
```

### 9. Criar Testes

#### Criar `tests/unit/test_parser.py`:
```python
"""Testes para Agente Parser."""
import pytest
from src.agents.parser import ParserAgent
from unittest.mock import Mock

@pytest.fixture
def parser_agent():
    llm = Mock()
    return ParserAgent(llm=llm)

def test_extract_from_pdf(parser_agent):
    """Testar extração de PDF."""
    # Criar PDF de teste
    pass

def test_normalize_questions(parser_agent):
    """Testar normalização."""
    pass
```

### 10. Documentar Formato Canônico

#### Criar `docs/agents/parser.md`:
```markdown
# Agente Parser

## Formato Canônico

### ParsedQuestion
- qid: Identificador único
- category: Categoria da pergunta
- question_text: Texto normalizado
- requirements: Lista de requisitos
- expected_format: Formato esperado
```

---

## Checklist de Validação

- [ ] Classe base do Agente Parser criada
- [ ] Extração de PDF implementada (com e sem OCR)
- [ ] Extração de DOCX implementada
- [ ] Extração de Excel/CSV implementada
- [ ] Normalização em formato canônico funcionando
- [ ] Mapeamento para histórico implementado
- [ ] Integração com LangChain como tool
- [ ] Métricas adicionadas
- [ ] Testes unitários criados e passando
- [ ] Testes de integração criados
- [ ] Documentação criada

---

## Comandos de Teste

```bash
# Testar extração de PDF
python -m pytest tests/unit/test_parser.py::test_extract_from_pdf

# Testar normalização
python -m pytest tests/unit/test_parser.py::test_normalize_questions

# Testar integração completa
python -m pytest tests/integration/test_parser_integration.py
```


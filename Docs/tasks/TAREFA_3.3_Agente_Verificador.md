# Tarefa 3.3: Agente Verificador (QA/Compliance)

## Objetivo
Implementar o Agente Verificador que valida qualidade, consistência e compliance das respostas geradas.

## Prioridade
Alta

## Estimativa
5 dias

## Responsável
Backend

---

## Instruções de Implementação

### 1. Criar Classe Base do Agente Verificador

#### Criar `src/agents/verifier.py`:
```python
"""Agente Verificador - Valida qualidade e compliance."""
from typing import List, Dict, Any, Optional
from langchain_core.language_models import BaseChatModel
from src.workflows.schema import VerifiedResponse, GeneratedResponse
import logging
import re

logger = logging.getLogger(__name__)


class VerifierAgent:
    """Agente Verificador para validação de respostas."""
    
    def __init__(self, llm: BaseChatModel):
        """Inicializar Agente Verificador."""
        self.llm = llm
        self.prohibited_terms = self._load_prohibited_terms()
        self._setup_system_prompt()
    
    def _load_prohibited_terms(self) -> List[str]:
        """Carregar lista de termos proibidos."""
        # TODO: Carregar de arquivo de configuração
        return [
            "garantimos 100%",
            "sem exceções",
            "sempre",
            "nunca falha"
        ]
    
    def _setup_system_prompt(self) -> None:
        """Configurar prompt do sistema."""
        self.system_prompt = """Você é um Agente Verificador especializado em validar qualidade e compliance de respostas.
Sua função é:
1. Verificar consistência entre respostas
2. Detectar termos proibidos
3. Identificar lacunas
4. Validar limites contratuais
5. Calcular score de confiança"""
```

### 2. Implementar Verificação de Consistência

#### Adicionar método:
```python
def check_consistency(
    self,
    responses: List[GeneratedResponse]
) -> Dict[str, Any]:
    """Verificar consistência entre respostas relacionadas."""
    inconsistencies = []
    
    # Agrupar por categoria
    by_category = {}
    for resp in responses:
        category = resp.qid.split('_')[0] if '_' in resp.qid else 'general'
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(resp)
    
    # Verificar contradições
    for category, category_responses in by_category.items():
        if len(category_responses) > 1:
            # Comparar respostas da mesma categoria
            for i, resp1 in enumerate(category_responses):
                for resp2 in category_responses[i+1:]:
                    if self._are_contradictory(resp1, resp2):
                        inconsistencies.append({
                            "qid1": resp1.qid,
                            "qid2": resp2.qid,
                            "issue": "Contradição detectada"
                        })
    
    return {
        "is_consistent": len(inconsistencies) == 0,
        "inconsistencies": inconsistencies
    }

def _are_contradictory(self, resp1: GeneratedResponse, resp2: GeneratedResponse) -> bool:
    """Verificar se duas respostas são contraditórias."""
    # Usar LLM para verificar contradição
    prompt = f"""As seguintes respostas são contraditórias?

Resposta 1: {resp1.response_text}
Resposta 2: {resp2.response_text}

Responda apenas: SIM ou NÃO"""
    
    # Implementar verificação via LLM
    return False  # Placeholder
```

### 3. Implementar Detecção de Termos Proibidos

#### Adicionar método:
```python
def detect_prohibited_terms(self, response_text: str) -> List[str]:
    """Detectar termos proibidos na resposta."""
    detected = []
    text_lower = response_text.lower()
    
    for term in self.prohibited_terms:
        if term.lower() in text_lower:
            detected.append(term)
    
    return detected
```

### 4. Implementar Detecção de Lacunas

#### Adicionar método:
```python
def detect_gaps(
    self,
    question: str,
    response: GeneratedResponse
) -> List[str]:
    """Detectar lacunas na resposta."""
    gaps = []
    
    # Verificar se resposta está vazia ou muito curta
    if not response.response_text or len(response.response_text.strip()) < 10:
        gaps.append("Resposta muito curta ou vazia")
    
    # Verificar campos obrigatórios mencionados na pergunta
    required_keywords = ["SLA", "garantia", "suporte", "preço"]
    question_lower = question.lower()
    response_lower = response.response_text.lower()
    
    for keyword in required_keywords:
        if keyword in question_lower and keyword not in response_lower:
            gaps.append(f"Falta mencionar: {keyword}")
    
    return gaps
```

### 5. Implementar Validação de Limites Contratuais

#### Adicionar método:
```python
def validate_contractual_limits(
    self,
    response_text: str
) -> Dict[str, Any]:
    """Validar aderência a limites contratuais."""
    # TODO: Implementar validação baseada em regras configuráveis
    return {
        "is_valid": True,
        "violations": []
    }
```

### 6. Implementar Verificação de Formatação

#### Adicionar método:
```python
def verify_formatting(
    self,
    response_text: str,
    expected_format: str
) -> bool:
    """Verificar se resposta está no formato esperado."""
    if expected_format == "sim/não":
        return response_text.lower().strip() in ["sim", "não", "yes", "no"]
    elif expected_format == "número":
        return bool(re.search(r'\d+', response_text))
    elif expected_format == "lista":
        return "\n" in response_text or "-" in response_text or "," in response_text
    else:
        return True  # Formato texto aceita qualquer coisa
```

### 7. Implementar Cálculo de Score de Confiança

#### Adicionar método:
```python
def calculate_confidence_score(
    self,
    response: GeneratedResponse,
    verification_results: Dict[str, Any]
) -> float:
    """Calcular score de confiança (0-100%)."""
    score = response.confidence_score * 100
    
    # Reduzir score baseado em problemas encontrados
    if verification_results.get("has_prohibited_terms"):
        score -= 20
    
    if verification_results.get("has_gaps"):
        score -= 15 * len(verification_results["gaps"])
    
    if not verification_results.get("is_consistent"):
        score -= 10
    
    if verification_results.get("formatting_errors"):
        score -= 5
    
    return max(0.0, min(100.0, score))
```

### 8. Implementar Verificação Completa

#### Adicionar método principal:
```python
def verify(
    self,
    question: str,
    response: GeneratedResponse,
    all_responses: Optional[List[GeneratedResponse]] = None
) -> VerifiedResponse:
    """Verificar resposta completa."""
    all_responses = all_responses or [response]
    
    # Verificar consistência
    consistency = self.check_consistency(all_responses)
    
    # Detectar termos proibidos
    prohibited = self.detect_prohibited_terms(response.response_text)
    
    # Detectar lacunas
    gaps = self.detect_gaps(question, response)
    
    # Validar limites contratuais
    contractual = self.validate_contractual_limits(response.response_text)
    
    # Verificar formatação (se especificado)
    formatting_ok = True  # TODO: Obter expected_format da pergunta
    
    # Calcular score
    verification_results = {
        "is_consistent": consistency["is_consistent"],
        "has_prohibited_terms": len(prohibited) > 0,
        "prohibited_terms": prohibited,
        "has_gaps": len(gaps) > 0,
        "gaps": gaps,
        "contractual_valid": contractual["is_valid"],
        "formatting_ok": formatting_ok
    }
    
    confidence_score = self.calculate_confidence_score(response, verification_results)
    
    # Determinar se precisa revisão
    needs_review = (
        not consistency["is_consistent"] or
        len(prohibited) > 0 or
        len(gaps) > 0 or
        not contractual["is_valid"] or
        confidence_score < 70.0
    )
    
    return VerifiedResponse(
        qid=response.qid,
        response_text=response.response_text,
        confidence_score=confidence_score / 100.0,
        is_consistent=consistency["is_consistent"],
        has_prohibited_terms=len(prohibited) > 0,
        has_gaps=len(gaps) > 0,
        validation_errors=consistency["inconsistencies"] + gaps,
        needs_review=needs_review
    )
```

### 9. Integrar com LangChain como Tool

#### Criar tool:
```python
from langchain_core.tools import tool

@tool
def verify_response_tool(question: str, response: str) -> str:
    """Verificar qualidade e compliance de resposta."""
    # Implementar chamada ao VerifierAgent
    pass
```

### 10. Adicionar Métricas

#### Atualizar métricas:
```python
# Métricas de Verifier
verifier_validations_total = Counter(
    'verifier_validations_total',
    'Total de validações',
    ['status']
)

verifier_detections_total = Counter(
    'verifier_detections_total',
    'Total de problemas detectados',
    ['type']  # prohibited_terms, gaps, inconsistencies
)
```

### 11. Criar Testes

#### Criar `tests/unit/test_verifier.py`:
```python
"""Testes para Agente Verificador."""
import pytest
from src.agents.verifier import VerifierAgent
from src.workflows.schema import GeneratedResponse
from unittest.mock import Mock

@pytest.fixture
def verifier_agent():
    llm = Mock()
    return VerifierAgent(llm=llm)

def test_detect_prohibited_terms(verifier_agent):
    """Testar detecção de termos proibidos."""
    response = GeneratedResponse(
        qid="Q001",
        response_text="Garantimos 100% de disponibilidade",
        confidence_score=0.9
    )
    terms = verifier_agent.detect_prohibited_terms(response.response_text)
    assert len(terms) > 0

def test_verify(verifier_agent):
    """Testar verificação completa."""
    pass
```

---

## Checklist de Validação

- [ ] Classe base do Agente Verificador criada
- [ ] Verificação de consistência implementada
- [ ] Detecção de termos proibidos funcionando
- [ ] Detecção de lacunas implementada
- [ ] Validação de limites contratuais implementada
- [ ] Verificação de formatação implementada
- [ ] Cálculo de score de confiança funcionando
- [ ] Sinalização para revisão implementada
- [ ] Integração com LangChain como tool
- [ ] Métricas adicionadas
- [ ] Testes unitários criados e passando
- [ ] Documentação criada

---

## Comandos de Teste

```bash
# Testar detecção de termos proibidos
python -m pytest tests/unit/test_verifier.py::test_detect_prohibited_terms

# Testar verificação completa
python -m pytest tests/unit/test_verifier.py::test_verify
```


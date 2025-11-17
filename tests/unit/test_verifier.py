"""Testes para Agente Verificador."""
import pytest
from src.agents.verifier import VerifierAgent
from src.workflows.schema import GeneratedResponse, VerifiedResponse
from unittest.mock import Mock, MagicMock
from langchain_core.messages import AIMessage


@pytest.fixture
def mock_llm():
    """Mock do LLM."""
    llm = Mock()
    
    def mock_invoke(messages):
        # Simular resposta de verificação de contradição
        content = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
        if "contraditórias" in content.lower() or "contradictory" in content.lower():
            return AIMessage(content="NÃO")
        return AIMessage(content="SIM")
    
    llm.invoke = Mock(side_effect=mock_invoke)
    return llm


@pytest.fixture
def verifier_agent(mock_llm):
    """Fixture para VerifierAgent."""
    return VerifierAgent(llm=mock_llm)


def test_detect_prohibited_terms(verifier_agent):
    """Testar detecção de termos proibidos."""
    response_text = "Garantimos 100% de disponibilidade sem exceções"
    terms = verifier_agent.detect_prohibited_terms(response_text)
    assert len(terms) > 0
    assert "garantimos 100%" in terms or any("100%" in term for term in terms)


def test_detect_prohibited_terms_none(verifier_agent):
    """Testar quando não há termos proibidos."""
    response_text = "O SLA do produto é de 99.9% de disponibilidade"
    terms = verifier_agent.detect_prohibited_terms(response_text)
    assert len(terms) == 0


def test_detect_gaps_short_response(verifier_agent):
    """Testar detecção de lacunas em resposta curta."""
    question = "Qual é o SLA do produto?"
    response = GeneratedResponse(
        qid="Q001",
        response_text="99.9%",
        confidence_score=0.9
    )
    gaps = verifier_agent.detect_gaps(question, response)
    assert len(gaps) > 0


def test_detect_gaps_missing_keyword(verifier_agent):
    """Testar detecção de lacunas quando falta keyword."""
    question = "Qual é o SLA do produto?"
    response = GeneratedResponse(
        qid="Q001",
        response_text="O produto tem alta disponibilidade",
        confidence_score=0.9
    )
    gaps = verifier_agent.detect_gaps(question, response)
    # Deve detectar que falta mencionar SLA
    assert any("sla" in gap.lower() for gap in gaps)


def test_detect_gaps_complete(verifier_agent):
    """Testar quando não há lacunas."""
    question = "Qual é o SLA do produto?"
    response = GeneratedResponse(
        qid="Q001",
        response_text="O SLA do produto é de 99.9% de disponibilidade",
        confidence_score=0.9
    )
    gaps = verifier_agent.detect_gaps(question, response)
    # Não deve ter lacunas relacionadas a SLA
    assert not any("sla" in gap.lower() for gap in gaps)


def test_validate_contractual_limits(verifier_agent):
    """Testar validação de limites contratuais."""
    response_text = "Garantimos 100% de disponibilidade sempre"
    result = verifier_agent.validate_contractual_limits(response_text)
    assert not result["is_valid"] or len(result["violations"]) > 0


def test_validate_contractual_limits_valid(verifier_agent):
    """Testar quando limites contratuais são válidos."""
    response_text = "O SLA do produto é de 99.9% de disponibilidade"
    result = verifier_agent.validate_contractual_limits(response_text)
    assert result["is_valid"]


def test_verify_formatting_yes_no(verifier_agent):
    """Testar verificação de formatação sim/não."""
    result = verifier_agent.verify_formatting("Sim", "sim/não")
    assert result["is_valid"]
    
    result = verifier_agent.verify_formatting("Talvez", "sim/não")
    assert not result["is_valid"]


def test_verify_formatting_number(verifier_agent):
    """Testar verificação de formatação número."""
    result = verifier_agent.verify_formatting("99.9%", "número")
    assert result["is_valid"]
    
    result = verifier_agent.verify_formatting("Alta disponibilidade", "número")
    assert not result["is_valid"]


def test_verify_formatting_list(verifier_agent):
    """Testar verificação de formatação lista."""
    result = verifier_agent.verify_formatting("Item 1\nItem 2\nItem 3", "lista")
    assert result["is_valid"]
    
    result = verifier_agent.verify_formatting("Texto simples", "lista")
    assert not result["is_valid"]


def test_check_consistency(verifier_agent, mock_llm):
    """Testar verificação de consistência."""
    responses = [
        GeneratedResponse(
            qid="Q001",
            response_text="O SLA é de 99.9%",
            confidence_score=0.9
        ),
        GeneratedResponse(
            qid="Q002",
            response_text="O SLA é de 99.9%",
            confidence_score=0.9
        )
    ]
    
    result = verifier_agent.check_consistency(responses)
    assert isinstance(result, dict)
    assert "is_consistent" in result
    assert "inconsistencies" in result


def test_calculate_confidence_score(verifier_agent):
    """Testar cálculo de score de confiança."""
    response = GeneratedResponse(
        qid="Q001",
        response_text="Resposta válida",
        confidence_score=0.9
    )
    
    # Score sem problemas
    verification_results = {
        "is_consistent": True,
        "has_prohibited_terms": False,
        "has_gaps": False,
        "contractual_valid": True,
        "formatting_ok": True
    }
    
    score = verifier_agent.calculate_confidence_score(response, verification_results)
    assert 80.0 <= score <= 100.0
    
    # Score com problemas
    verification_results["has_prohibited_terms"] = True
    verification_results["has_gaps"] = True
    verification_results["gaps"] = ["Falta mencionar: SLA"]
    
    score = verifier_agent.calculate_confidence_score(response, verification_results)
    assert score < 80.0


def test_verify_complete(verifier_agent):
    """Testar verificação completa."""
    question = "Qual é o SLA do produto?"
    response = GeneratedResponse(
        qid="Q001",
        response_text="O SLA do produto é de 99.9% de disponibilidade",
        confidence_score=0.9
    )
    
    verified = verifier_agent.verify(question, response)
    
    assert isinstance(verified, VerifiedResponse)
    assert verified.qid == "Q001"
    assert verified.response_text == response.response_text
    assert 0.0 <= verified.confidence_score <= 1.0
    assert isinstance(verified.is_consistent, bool)
    assert isinstance(verified.has_prohibited_terms, bool)
    assert isinstance(verified.has_gaps, bool)
    assert isinstance(verified.needs_review, bool)


def test_verify_with_prohibited_terms(verifier_agent):
    """Testar verificação com termos proibidos."""
    question = "Qual é o SLA?"
    response = GeneratedResponse(
        qid="Q001",
        response_text="Garantimos 100% de disponibilidade sempre",
        confidence_score=0.9
    )
    
    verified = verifier_agent.verify(question, response)
    
    assert verified.has_prohibited_terms
    assert verified.needs_review


def test_verify_batch(verifier_agent):
    """Testar verificação em lote."""
    questions_and_responses = [
        {
            "question": "Qual é o SLA?",
            "response": GeneratedResponse(
                qid="Q001",
                response_text="O SLA é de 99.9%",
                confidence_score=0.9
            )
        },
        {
            "question": "Qual é o preço?",
            "response": GeneratedResponse(
                qid="Q002",
                response_text="O preço é R$ 1000/mês",
                confidence_score=0.8
            )
        }
    ]
    
    verified_responses = verifier_agent.verify_batch(questions_and_responses)
    
    assert len(verified_responses) == 2
    assert all(isinstance(v, VerifiedResponse) for v in verified_responses)
    assert verified_responses[0].qid == "Q001"
    assert verified_responses[1].qid == "Q002"


def test_verifier_agent_initialization(verifier_agent):
    """Testar inicialização do VerifierAgent."""
    assert verifier_agent.llm is not None
    assert verifier_agent.system_prompt is not None
    assert len(verifier_agent.prohibited_terms) > 0
    assert "Verificador" in verifier_agent.system_prompt


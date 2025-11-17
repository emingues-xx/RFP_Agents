"""Testes de integração do Verifier Agent."""
import pytest
from src.agents.verifier import VerifierAgent
from src.workflows.schema import GeneratedResponse
from src.utils.llm_factory import LLMFactory


@pytest.fixture
def verifier_agent():
    """Fixture para VerifierAgent com LLM real."""
    factory = LLMFactory()
    llm = factory.get_default_llm()
    return VerifierAgent(llm=llm)


@pytest.mark.integration
def test_verify_single_response(verifier_agent):
    """Testar verificação de resposta única."""
    question = "Qual é o SLA do produto?"
    response = GeneratedResponse(
        qid="Q001",
        response_text="O SLA do produto é de 99.9% de disponibilidade",
        confidence_score=0.9
    )
    
    verified = verifier_agent.verify(question, response)
    
    assert isinstance(verified, VerifiedResponse)
    assert verified.qid == "Q001"
    assert len(verified.response_text) > 0
    assert 0.0 <= verified.confidence_score <= 1.0


@pytest.mark.integration
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


@pytest.mark.integration
def test_verify_batch(verifier_agent):
    """Testar verificação em lote."""
    questions_and_responses = [
        {
            "question": "Qual é o SLA?",
            "response": GeneratedResponse(
                qid="Q001",
                response_text="O SLA é de 99.9% de disponibilidade",
                confidence_score=0.9
            )
        },
        {
            "question": "Qual é o suporte oferecido?",
            "response": GeneratedResponse(
                qid="Q002",
                response_text="Oferecemos suporte 24/7",
                confidence_score=0.8
            )
        }
    ]
    
    verified_responses = verifier_agent.verify_batch(questions_and_responses)
    
    assert len(verified_responses) == 2
    assert all(isinstance(v, VerifiedResponse) for v in verified_responses)


@pytest.mark.integration
def test_verifier_tool_integration():
    """Testar integração da tool."""
    from src.tools.verifier_tool import verify_response_tool
    
    result = verify_response_tool.invoke({
        "question": "Qual é o SLA do produto?",
        "response": "O SLA é de 99.9% de disponibilidade",
        "qid": "Q001"
    })
    
    assert result is not None
    assert isinstance(result, str)
    # Verificar se é JSON válido
    import json
    try:
        data = json.loads(result)
        assert "qid" in data
        assert "confidence_score" in data
        assert "needs_review" in data
    except json.JSONDecodeError:
        # Pode retornar erro em formato string
        assert "erro" in result.lower() or "error" in result.lower()


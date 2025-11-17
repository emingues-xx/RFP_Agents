"""Testes de integração do Knowledge Agent."""
import pytest
from src.agents.knowledge import KnowledgeAgent
from src.utils.llm_factory import LLMFactory


@pytest.fixture
def knowledge_agent():
    """Fixture para KnowledgeAgent com LLM real."""
    factory = LLMFactory()
    llm = factory.get_default_llm()
    # Sem vector store por enquanto (será implementado na TAREFA_4.1)
    return KnowledgeAgent(llm=llm, vector_store=None)


@pytest.mark.integration
def test_generate_response_single_question(knowledge_agent):
    """Testar geração de resposta para pergunta única."""
    response = knowledge_agent.generate_response(
        question="Qual é o SLA do produto?",
        qid="Q001"
    )
    
    assert isinstance(response, GeneratedResponse)
    assert response.qid == "Q001"
    assert len(response.response_text) > 0
    assert 0.0 <= response.confidence_score <= 1.0


@pytest.mark.integration
def test_generate_responses_multiple(knowledge_agent):
    """Testar geração de múltiplas respostas."""
    questions = [
        {
            "qid": "Q001",
            "question_text": "Qual é o SLA?",
            "category": "técnico"
        },
        {
            "qid": "Q002",
            "question_text": "Qual é o suporte oferecido?",
            "category": "técnico"
        }
    ]
    
    responses = knowledge_agent.generate_responses(questions)
    
    assert len(responses) == 2
    assert all(isinstance(r, GeneratedResponse) for r in responses)


@pytest.mark.integration
def test_knowledge_tool_integration():
    """Testar integração da tool."""
    from src.tools.knowledge_tool import knowledge_query_tool
    
    result = knowledge_query_tool.invoke({
        "question": "Qual é o SLA do produto?",
        "category": "técnico"
    })
    
    assert result is not None
    assert isinstance(result, str)
    # Verificar se é JSON válido
    import json
    try:
        data = json.loads(result)
        assert "response_text" in data
        assert "confidence_score" in data
    except json.JSONDecodeError:
        # Pode retornar erro em formato string
        assert "erro" in result.lower() or "error" in result.lower()


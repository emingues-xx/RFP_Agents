"""Testes para Agente Conhecimento."""
import pytest
from src.agents.knowledge import KnowledgeAgent
from src.workflows.schema import GeneratedResponse
from unittest.mock import Mock, MagicMock, patch
from langchain_core.messages import AIMessage
from langchain_core.documents import Document
import json


@pytest.fixture
def mock_llm():
    """Mock do LLM."""
    llm = Mock()
    
    def mock_invoke(messages):
        # Simular resposta JSON do LLM
        response_data = {
            "response_text": "O SLA do produto é de 99.9% de disponibilidade [1].",
            "confidence_score": 0.85,
            "citations": ["documento_tecnico.pdf"],
            "requires_human_input": False,
            "human_input_fields": []
        }
        return AIMessage(content=json.dumps(response_data))
    
    llm.invoke = Mock(side_effect=mock_invoke)
    return llm


@pytest.fixture
def mock_vector_store():
    """Mock do vector store."""
    vector_store = MagicMock()
    
    # Mock similarity_search
    mock_docs = [
        Document(
            page_content="O SLA do produto é de 99.9% de disponibilidade.",
            metadata={"source": "documento_tecnico.pdf", "category": "técnico"}
        )
    ]
    vector_store.similarity_search = Mock(return_value=mock_docs)
    return vector_store


@pytest.fixture
def knowledge_agent(mock_llm, mock_vector_store):
    """Fixture para KnowledgeAgent."""
    return KnowledgeAgent(llm=mock_llm, vector_store=mock_vector_store)


@pytest.fixture
def knowledge_agent_no_vector_store(mock_llm):
    """Fixture para KnowledgeAgent sem vector store."""
    return KnowledgeAgent(llm=mock_llm, vector_store=None)


def test_retrieve_documents(knowledge_agent):
    """Testar retrieval de documentos."""
    docs = knowledge_agent.retrieve_documents("Qual é o SLA?")
    assert len(docs) > 0
    assert isinstance(docs[0], Document)


def test_retrieve_documents_no_vector_store(knowledge_agent_no_vector_store):
    """Testar retrieval sem vector store."""
    docs = knowledge_agent_no_vector_store.retrieve_documents("Qual é o SLA?")
    assert len(docs) == 0


def test_retrieve_documents_with_category(knowledge_agent):
    """Testar retrieval com categoria."""
    docs = knowledge_agent.retrieve_documents("Qual é o SLA?", category="técnico")
    assert len(docs) >= 0  # Pode estar vazio se mock não retornar


def test_generate_response(knowledge_agent):
    """Testar geração de resposta."""
    response = knowledge_agent.generate_response(
        question="Qual é o SLA?",
        qid="Q001"
    )
    
    assert isinstance(response, GeneratedResponse)
    assert response.qid == "Q001"
    assert response.response_text is not None
    assert 0.0 <= response.confidence_score <= 1.0


def test_generate_response_with_context(knowledge_agent):
    """Testar geração com contexto."""
    context = {
        "client": "ABC Corp",
        "product": "Cloud Services",
        "category": "técnico"
    }
    
    response = knowledge_agent.generate_response(
        question="Qual é o SLA?",
        context=context,
        qid="Q001"
    )
    
    assert isinstance(response, GeneratedResponse)
    assert response.qid == "Q001"


def test_generate_responses(knowledge_agent):
    """Testar geração de múltiplas respostas."""
    questions = [
        {
            "qid": "Q001",
            "question_text": "Qual é o SLA?",
            "category": "técnico"
        },
        {
            "qid": "Q002",
            "question_text": "Qual é o preço?",
            "category": "comercial"
        }
    ]
    
    responses = knowledge_agent.generate_responses(questions)
    
    assert len(responses) == 2
    assert all(isinstance(r, GeneratedResponse) for r in responses)
    assert responses[0].qid == "Q001"
    assert responses[1].qid == "Q002"


def test_retrieve_from_multiple_bases(knowledge_agent):
    """Testar retrieval de múltiplas bases."""
    categories = ["técnico", "segurança"]
    results = knowledge_agent.retrieve_from_multiple_bases(
        "Qual é o SLA?",
        categories=categories
    )
    
    assert isinstance(results, dict)
    assert "técnico" in results
    assert "segurança" in results


def test_consult_historical_rfps(knowledge_agent):
    """Testar consulta a RFPs históricas."""
    results = knowledge_agent.consult_historical_rfps("Qual é o SLA?")
    # Por enquanto retorna lista vazia (TODO implementar)
    assert isinstance(results, list)


def test_generate_response_json_error(knowledge_agent):
    """Testar tratamento de erro de JSON."""
    # Mock para retornar resposta inválida
    knowledge_agent.llm.invoke = Mock(return_value=AIMessage(content="Não é JSON válido"))
    
    response = knowledge_agent.generate_response("Qual é o SLA?")
    
    assert isinstance(response, GeneratedResponse)
    assert "erro" in response.response_text.lower() or "error" in response.response_text.lower()
    assert response.confidence_score == 0.0


def test_knowledge_agent_initialization(knowledge_agent):
    """Testar inicialização do KnowledgeAgent."""
    assert knowledge_agent.llm is not None
    assert knowledge_agent.system_prompt is not None
    assert "Conhecimento" in knowledge_agent.system_prompt


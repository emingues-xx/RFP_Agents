"""Testes para Agente Orquestrador."""
import pytest
from src.agents.orchestrator import OrchestratorAgent, InputType, Context
from unittest.mock import Mock, MagicMock
from langchain_core.messages import AIMessage


@pytest.fixture
def mock_llm():
    """Mock do LLM."""
    llm = Mock()
    
    # Mock para identify_input_type
    def mock_invoke_identify(messages):
        return AIMessage(content='{"type": "single_question", "confidence": 0.9, "metadata": {}}')
    
    # Mock para collect_context
    def mock_invoke_context(messages):
        return AIMessage(content='{"client": "ABC Corp", "product": "Cloud Services", "deadlines": "30 dias", "additional_info": {}}')
    
    # Default: identificar tipo
    llm.invoke = Mock(side_effect=mock_invoke_identify)
    return llm


@pytest.fixture
def orchestrator(mock_llm):
    """Fixture para Orchestrator."""
    return OrchestratorAgent(
        llm=mock_llm,
        session_id="test-session-123"
    )


def test_identify_single_question(orchestrator):
    """Testar identificação de pergunta única."""
    input_text = "Qual é o SLA do produto?"
    result = orchestrator.identify_input_type(input_text)
    assert result.type in ["single_question", "questionnaire", "unknown"]
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.metadata, dict)


def test_identify_questionnaire(orchestrator):
    """Testar identificação de questionário."""
    # Mock para retornar questionnaire
    orchestrator.llm.invoke = Mock(return_value=AIMessage(
        content='{"type": "questionnaire", "confidence": 0.85, "metadata": {"question_count": 3}}'
    ))
    
    input_text = "Pergunta 1: ...\nPergunta 2: ...\nPergunta 3: ..."
    result = orchestrator.identify_input_type(input_text)
    assert result.type in ["single_question", "questionnaire", "unknown"]


def test_identify_input_type_enhanced_with_file(orchestrator):
    """Testar identificação melhorada com arquivo."""
    result = orchestrator.identify_input_type_enhanced(
        input_text="...",
        file_path="/path/to/file.pdf"
    )
    assert result.type == "questionnaire"
    assert result.confidence == 0.9
    assert result.metadata["source"] == "file"


def test_identify_input_type_enhanced_multiple_questions(orchestrator):
    """Testar identificação melhorada com múltiplas perguntas."""
    input_text = "Pergunta 1?\nPergunta 2?\nPergunta 3?\nPergunta 4?\nPergunta 5?\nPergunta 6?"
    result = orchestrator.identify_input_type_enhanced(input_text)
    assert result.type == "questionnaire"
    assert result.confidence == 0.8


def test_collect_context(orchestrator):
    """Testar coleta de contexto."""
    # Mock para retornar contexto
    orchestrator.llm.invoke = Mock(return_value=AIMessage(
        content='{"client": "ABC Corp", "product": "Cloud Services", "deadlines": "30 dias", "additional_info": {}}'
    ))
    
    input_text = "Cliente: ABC Corp, Produto: Cloud Services, Prazo: 30 dias"
    context = orchestrator.collect_context(input_text)
    assert isinstance(context, Context)
    assert context.client == "ABC Corp"
    assert context.product == "Cloud Services"


def test_collect_context_interactive_complete(orchestrator):
    """Testar coleta de contexto interativa com contexto completo."""
    # Mock para retornar contexto completo
    orchestrator.llm.invoke = Mock(return_value=AIMessage(
        content='{"client": "ABC Corp", "product": "Cloud Services", "deadlines": "30 dias", "additional_info": {}}'
    ))
    
    context = orchestrator.collect_context_interactive("Cliente: ABC Corp, Produto: Cloud Services")
    assert not context.additional_info.get("needs_clarification", False)


def test_collect_context_interactive_incomplete(orchestrator):
    """Testar coleta de contexto interativa com contexto incompleto."""
    # Mock para retornar contexto incompleto
    orchestrator.llm.invoke = Mock(return_value=AIMessage(
        content='{"client": null, "product": null, "deadlines": null, "additional_info": {}}'
    ))
    
    context = orchestrator.collect_context_interactive("Produto: Cloud Services")
    assert context.additional_info.get("needs_clarification", False)
    assert len(context.additional_info.get("questions", [])) > 0


def test_coordinate_agents_single_question(orchestrator):
    """Testar coordenação para pergunta única."""
    input_type = InputType(type="single_question", confidence=0.9)
    context = Context()
    plan = orchestrator.coordinate_agents(input_type, context, "Test question")
    assert "next_steps" in plan
    assert len(plan["next_steps"]) > 0
    assert plan["next_steps"][0]["agent"] == "knowledge"


def test_coordinate_agents_questionnaire(orchestrator):
    """Testar coordenação para questionário."""
    input_type = InputType(type="questionnaire", confidence=0.9)
    context = Context()
    plan = orchestrator.coordinate_agents(input_type, context, "Test questionnaire")
    assert "next_steps" in plan
    assert len(plan["next_steps"]) == 3
    assert plan["next_steps"][0]["agent"] == "parser"
    assert plan["next_steps"][1]["agent"] == "knowledge"
    assert plan["next_steps"][2]["agent"] == "verifier"


def test_manage_workflow_state(orchestrator):
    """Testar gerenciamento de estado."""
    state = {"data": "test"}
    updated_state = orchestrator.manage_workflow_state(state)
    assert "orchestrator" in updated_state
    assert updated_state["orchestrator"]["version"] == "1.0"
    assert updated_state["orchestrator"]["session_id"] == "test-session-123"


def test_get_conversation_history_no_memory(orchestrator):
    """Testar obtenção de histórico sem memória."""
    history = orchestrator.get_conversation_history()
    assert isinstance(history, list)
    assert len(history) == 0


def test_add_to_memory_no_memory_manager(orchestrator):
    """Testar adição à memória sem memory manager."""
    # Não deve gerar erro
    orchestrator.add_to_memory("input", "output")


def test_identify_input_type_json_error_handling(orchestrator):
    """Testar tratamento de erro de JSON."""
    # Mock para retornar resposta inválida
    orchestrator.llm.invoke = Mock(return_value=AIMessage(content="Não é JSON válido"))
    
    result = orchestrator.identify_input_type("test")
    assert result.type == "unknown"
    assert result.confidence == 0.0


def test_collect_context_json_error_handling(orchestrator):
    """Testar tratamento de erro de JSON no contexto."""
    # Mock para retornar resposta inválida
    orchestrator.llm.invoke = Mock(return_value=AIMessage(content="Não é JSON válido"))
    
    context = orchestrator.collect_context("test")
    assert isinstance(context, Context)
    assert "error" in context.additional_info


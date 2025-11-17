"""Testes de integração do workflow."""
import pytest
from src.workflows.workflow import RFPWorkflow
from langgraph.checkpoint.memory import MemorySaver


@pytest.fixture
def workflow():
    """Fixture para workflow."""
    checkpoint = MemorySaver()
    return RFPWorkflow(checkpoint_saver=checkpoint)


def test_workflow_entry(workflow):
    """Testar entrada do workflow."""
    result = workflow.run(
        input_text="Qual é o SLA?",
        session_id="test-session-1"
    )
    assert result is not None
    assert "current_step" in result
    assert result["current_step"] == "completed"
    assert "workflow_id" in result
    assert result["workflow_id"] == "wf-test-session-1"


def test_workflow_single_question(workflow):
    """Testar workflow com pergunta única."""
    result = workflow.run(
        input_text="Qual é o tempo de resposta do sistema?",
        session_id="test-session-2"
    )
    assert result["input_type"] in ["single_question", "questionnaire", "unknown"]
    assert "context" in result
    assert isinstance(result["context"], dict)


def test_workflow_questionnaire(workflow):
    """Testar workflow com questionário."""
    input_text = """
    Pergunta 1: Qual é o SLA?
    Pergunta 2: Qual é o suporte oferecido?
    Pergunta 3: Qual é o preço?
    """
    result = workflow.run(
        input_text=input_text,
        session_id="test-session-3"
    )
    assert result["input_type"] in ["single_question", "questionnaire", "unknown"]
    assert "coordination_plan" in result


def test_workflow_state_structure(workflow):
    """Testar estrutura do estado do workflow."""
    result = workflow.run(
        input_text="Test question",
        session_id="test-session-4"
    )
    
    # Verificar campos obrigatórios
    assert "input_text" in result
    assert "session_id" in result
    assert "workflow_id" in result
    assert "current_step" in result
    assert "errors" in result
    assert isinstance(result["errors"], list)


def test_workflow_with_errors(workflow):
    """Testar workflow com input inválido."""
    # Input vazio pode causar erro
    result = workflow.run(
        input_text="",
        session_id="test-session-5"
    )
    # Deve ter processado mesmo com input vazio
    assert result is not None
    assert "current_step" in result


def test_workflow_coordination_plan(workflow):
    """Testar se coordination_plan é criado."""
    result = workflow.run(
        input_text="Qual é o SLA do produto?",
        session_id="test-session-6"
    )
    assert "coordination_plan" in result
    if result["coordination_plan"]:
        assert "next_steps" in result["coordination_plan"]


def test_workflow_different_sessions(workflow):
    """Testar múltiplas sessões."""
    result1 = workflow.run(
        input_text="Question 1",
        session_id="session-a"
    )
    result2 = workflow.run(
        input_text="Question 2",
        session_id="session-b"
    )
    
    assert result1["session_id"] == "session-a"
    assert result2["session_id"] == "session-b"
    assert result1["workflow_id"] != result2["workflow_id"]


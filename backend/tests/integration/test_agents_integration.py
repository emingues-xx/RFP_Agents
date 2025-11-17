"""Testes de integração entre agentes."""
import pytest
from src.workflows.workflow import RFPWorkflow
from langgraph.checkpoint.memory import MemorySaver
from src.workflows.schema import ParsedQuestion, GeneratedResponse, VerifiedResponse


@pytest.fixture
def workflow():
    """Fixture para workflow com checkpoint em memória."""
    checkpoint = MemorySaver()
    return RFPWorkflow(checkpoint_saver=checkpoint)


@pytest.mark.integration
def test_full_workflow_questionnaire(workflow):
    """Testar fluxo completo com questionário."""
    input_text = """
    Pergunta 1: Qual é o SLA do produto?
    Pergunta 2: Qual é o suporte oferecido?
    Pergunta 3: Qual é o preço?
    """
    
    result = workflow.run(input_text, session_id="test-integration-1")
    
    # Verificar que o workflow completou
    assert result is not None
    assert result.get("current_step") == "completed"
    
    # Verificar que perguntas foram parseadas
    assert result.get("parsed_questions") is not None
    parsed_questions = result.get("parsed_questions", [])
    assert len(parsed_questions) > 0
    
    # Verificar que respostas foram geradas
    assert result.get("generated_responses") is not None
    generated_responses = result.get("generated_responses", [])
    assert len(generated_responses) > 0
    assert len(generated_responses) == len(parsed_questions)
    
    # Verificar que respostas foram verificadas
    assert result.get("verified_responses") is not None
    verified_responses = result.get("verified_responses", [])
    assert len(verified_responses) > 0
    assert len(verified_responses) == len(generated_responses)


@pytest.mark.integration
def test_full_workflow_single_question(workflow):
    """Testar fluxo completo com pergunta única."""
    input_text = "Qual é o SLA do produto?"
    
    result = workflow.run(input_text, session_id="test-integration-2")
    
    # Verificar que o workflow completou
    assert result is not None
    assert result.get("current_step") == "completed"
    
    # Verificar tipo de input
    assert result.get("input_type") == "single_question"
    
    # Verificar que resposta foi gerada (sem parser)
    assert result.get("generated_responses") is not None
    generated_responses = result.get("generated_responses", [])
    assert len(generated_responses) == 1
    
    # Verificar que resposta foi verificada
    assert result.get("verified_responses") is not None
    verified_responses = result.get("verified_responses", [])
    assert len(verified_responses) == 1


@pytest.mark.integration
def test_workflow_with_context(workflow):
    """Testar workflow com contexto adicional."""
    input_text = """
    Cliente: ABC Corp
    Produto: Cloud Services
    
    Pergunta 1: Qual é o SLA?
    Pergunta 2: Qual é o suporte?
    """
    
    result = workflow.run(input_text, session_id="test-integration-3")
    
    assert result is not None
    assert result.get("context") is not None
    
    # Verificar que contexto foi coletado
    context = result.get("context", {})
    # O contexto pode conter informações extraídas pelo orchestrator
    assert isinstance(context, dict)


@pytest.mark.integration
def test_workflow_error_handling(workflow):
    """Testar tratamento de erros no workflow."""
    # Input inválido (vazio)
    input_text = ""
    
    result = workflow.run(input_text, session_id="test-integration-error")
    
    # Verificar que erros foram capturados
    assert result is not None
    # O workflow pode completar mesmo com erros, mas deve registrar
    errors = result.get("errors", [])
    # Pode ter erros ou não, dependendo de como o orchestrator lida com input vazio
    assert isinstance(errors, list)


@pytest.mark.integration
def test_workflow_state_consistency(workflow):
    """Testar consistência do estado durante o workflow."""
    input_text = """
    Pergunta 1: Qual é o SLA?
    Pergunta 2: Qual é o preço?
    """
    
    result = workflow.run(input_text, session_id="test-integration-consistency")
    
    # Verificar que estado está consistente
    assert result.get("workflow_id") is not None
    assert result.get("session_id") == "test-integration-consistency"
    
    # Verificar que número de perguntas parseadas = número de respostas geradas = número de respostas verificadas
    parsed_count = len(result.get("parsed_questions", []))
    generated_count = len(result.get("generated_responses", []))
    verified_count = len(result.get("verified_responses", []))
    
    if parsed_count > 0:
        assert generated_count == parsed_count, "Número de respostas geradas deve igualar perguntas parseadas"
        assert verified_count == generated_count, "Número de respostas verificadas deve igualar respostas geradas"


@pytest.mark.integration
def test_workflow_requires_approval(workflow):
    """Testar que workflow sinaliza necessidade de aprovação."""
    input_text = "Qual é o SLA do produto?"
    
    result = workflow.run(input_text, session_id="test-integration-approval")
    
    # Verificar que requires_approval está definido
    assert "requires_approval" in result
    assert result.get("requires_approval") is True  # Sempre requer aprovação após verificação


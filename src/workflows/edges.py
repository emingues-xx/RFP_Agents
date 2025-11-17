"""Edges (rotas) do workflow LangGraph."""
from typing import Literal
from src.workflows.state import WorkflowState
import logging

logger = logging.getLogger(__name__)


def route_after_orchestrator(state: WorkflowState) -> Literal["single_question", "questionnaire", "error"]:
    """Roteamento após orquestrador."""
    input_type = state.get("input_type")
    
    if not input_type:
        logger.error("Tipo de input não identificado")
        return "error"
    
    if input_type == "single_question":
        return "single_question"
    elif input_type == "questionnaire":
        return "questionnaire"
    else:
        return "error"


def route_after_verification(state: WorkflowState) -> Literal["approval", "error"]:
    """Roteamento após verificação."""
    errors = state.get("errors", [])
    if errors:
        logger.error(f"Erros encontrados após verificação: {len(errors)}")
        return "error"
    
    # Verificar se há respostas verificadas que precisam de revisão
    verified_responses = state.get("verified_responses", [])
    needs_review = any(
        resp.get("needs_review", False) for resp in verified_responses
    )
    
    # Sempre requer aprovação
    state["requires_approval"] = True
    if needs_review:
        logger.info("Respostas verificadas requerem revisão humana")
    
    return "approval"


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
        return "error"
    
    # Sempre requer aprovação
    state["requires_approval"] = True
    return "approval"


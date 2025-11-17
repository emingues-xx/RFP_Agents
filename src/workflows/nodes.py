"""Nodes do workflow LangGraph."""
from typing import Dict, Any
from src.workflows.state import WorkflowState
from src.agents.orchestrator import OrchestratorAgent
import logging

logger = logging.getLogger(__name__)


def entry_node(state: WorkflowState) -> WorkflowState:
    """Node de entrada do workflow."""
    logger.info(f"Workflow iniciado: {state['workflow_id']}")
    state["current_step"] = "entry"
    return state


def orchestrator_node(state: WorkflowState, orchestrator: OrchestratorAgent) -> WorkflowState:
    """Node do Agente Orquestrador."""
    logger.info("Executando Agente Orquestrador")
    
    try:
        # Identificar tipo de input
        input_type = orchestrator.identify_input_type(state["input_text"])
        state["input_type"] = input_type.type
        
        # Coletar contexto
        context = orchestrator.collect_context(state["input_text"])
        state["context"] = context.model_dump()
        
        # Coordenar próximos passos
        coordination_plan = orchestrator.coordinate_agents(
            input_type,
            context,
            state["input_text"]
        )
        state["coordination_plan"] = coordination_plan
        
        state["current_step"] = "orchestrator_complete"
        logger.info(f"Orquestração completa: {state['input_type']}")
        
    except Exception as e:
        logger.error(f"Erro no Agente Orquestrador: {e}")
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Orchestrator error: {str(e)}")
        state["current_step"] = "error"
    
    return state


def exit_node(state: WorkflowState) -> WorkflowState:
    """Node de saída do workflow."""
    logger.info(f"Workflow finalizado: {state['workflow_id']}")
    state["current_step"] = "completed"
    return state


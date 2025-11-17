"""Node de HITL para aprovação humana."""
from typing import Dict, Any
from src.workflows.state import WorkflowState
from src.api.models.approval import ApprovalRequest, ApprovalStatus
from src.utils.notifications import NotificationService
from src.utils.metrics import (
    hitl_approvals_total,
    hitl_approval_duration_seconds
)
import time
import logging

logger = logging.getLogger(__name__)


def hitl_approval_node(state: WorkflowState) -> WorkflowState:
    """Node que pausa workflow para aprovação humana.
    
    Args:
        state: Estado atual do workflow
    
    Returns:
        Estado atualizado com informações de aprovação
    """
    logger.info("Workflow pausado para aprovação humana")
    
    # Verificar se já existe uma aprovação pendente
    existing_approval_id = state.get("approval_id")
    if existing_approval_id:
        # Verificar status da aprovação existente
        existing_approval = ApprovalRequest.get_by_id(existing_approval_id)
        if existing_approval and existing_approval.status == ApprovalStatus.PENDING:
            logger.info(f"Aprovação já existe e está pendente: {existing_approval_id}")
            state["approval_status"] = "pending"
            state["requires_approval"] = True
            state["current_step"] = "awaiting_approval"
            return state
    
    # Marcar que requer aprovação
    state["requires_approval"] = True
    state["approval_status"] = "pending"
    state["current_step"] = "awaiting_approval"
    
    # Criar registro de aprovação
    try:
        approval_request = ApprovalRequest.create_from_state(state)
        approval_id = approval_request.save()
        
        state["approval_id"] = approval_id
        
        # Métricas
        hitl_approvals_total.labels(status="pending").inc()
        
        # Notificar
        NotificationService.notify_approval_pending(
            approval_id=approval_id,
            workflow_id=state.get("workflow_id", "unknown")
        )
        
        logger.info(f"Aprovação criada: {approval_id} para workflow {state.get('workflow_id')}")
    except Exception as e:
        logger.error(f"Erro ao criar aprovação: {e}")
        # Continuar mesmo com erro, mas marcar como erro
        state["errors"] = state.get("errors", []) + [{
            "agent": "hitl",
            "error": f"Erro ao criar aprovação: {str(e)}",
            "type": type(e).__name__
        }]
    
    return state


def check_approval_status(state: WorkflowState) -> str:
    """Verificar status de aprovação e rotear.
    
    Args:
        state: Estado atual do workflow
    
    Returns:
        Próximo passo: "continue", "reject", ou "wait"
    """
    approval_id = state.get("approval_id")
    if not approval_id:
        logger.warning("Nenhum approval_id no estado, aguardando")
        return "wait"
    
    try:
        approval = ApprovalRequest.get_by_id(approval_id)
        if not approval:
            logger.warning(f"Aprovação {approval_id} não encontrada, aguardando")
            return "wait"
        
        # Atualizar estado com status da aprovação
        state["approval_status"] = approval.status.value
        
        # Calcular duração de espera
        if approval.updated_at and approval.created_at:
            duration = (approval.updated_at - approval.created_at).total_seconds()
            hitl_approval_duration_seconds.observe(duration)
        
        if approval.status == ApprovalStatus.APPROVED:
            logger.info(f"Aprovação {approval_id} aprovada, continuando workflow")
            hitl_approvals_total.labels(status="approved").inc()
            
            # Se foi editada, atualizar respostas no estado
            if approval.status == ApprovalStatus.EDITED or approval.responses:
                state["verified_responses"] = approval.responses
            
            return "continue"
        elif approval.status == ApprovalStatus.REJECTED:
            logger.info(f"Aprovação {approval_id} rejeitada")
            hitl_approvals_total.labels(status="rejected").inc()
            return "reject"
        elif approval.status == ApprovalStatus.PENDING:
            logger.debug(f"Aprovação {approval_id} ainda pendente")
            return "wait"
        else:
            logger.warning(f"Status de aprovação desconhecido: {approval.status}")
            return "wait"
    except Exception as e:
        logger.error(f"Erro ao verificar status de aprovação: {e}")
        return "wait"


"""Sistema de notificações."""
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Serviço de notificações."""
    
    @staticmethod
    def notify_approval_pending(approval_id: str, workflow_id: str):
        """Notificar que há aprovação pendente.
        
        Args:
            approval_id: ID da aprovação
            workflow_id: ID do workflow
        """
        # TODO: Implementar notificação (email, webhook, etc.)
        # Por enquanto, apenas log
        logger.info(
            f"Aprovação pendente: {approval_id} para workflow {workflow_id}. "
            f"Acesse /approvals/{approval_id} para revisar."
        )
        
        # Aqui pode ser adicionado:
        # - Envio de email
        # - Webhook para sistema externo
        # - Notificação push
        # - Integração com Slack/Teams
    
    @staticmethod
    def notify_approval_approved(approval_id: str, workflow_id: str, approved_by: Optional[str] = None):
        """Notificar que aprovação foi aprovada.
        
        Args:
            approval_id: ID da aprovação
            workflow_id: ID do workflow
            approved_by: Usuário que aprovou
        """
        logger.info(
            f"Aprovação aprovada: {approval_id} para workflow {workflow_id} "
            f"por {approved_by or 'usuário desconhecido'}"
        )
    
    @staticmethod
    def notify_approval_rejected(approval_id: str, workflow_id: str, comments: Optional[str] = None):
        """Notificar que aprovação foi rejeitada.
        
        Args:
            approval_id: ID da aprovação
            workflow_id: ID do workflow
            comments: Comentários da rejeição
        """
        logger.info(
            f"Aprovação rejeitada: {approval_id} para workflow {workflow_id}. "
            f"Comentários: {comments or 'Nenhum'}"
        )


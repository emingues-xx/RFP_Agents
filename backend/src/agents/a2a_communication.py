"""Comunicação Agent-to-Agent."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class A2AMessage:
    """Mensagem entre agentes."""
    from_agent: str
    to_agent: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validação pós-inicialização."""
        if not self.from_agent or not self.to_agent:
            raise ValueError("from_agent e to_agent são obrigatórios")
        if not self.message_type:
            raise ValueError("message_type é obrigatório")


class A2ACommunicator:
    """Gerenciador de comunicação A2A."""
    
    def __init__(self):
        """Inicializar comunicador."""
        self.message_queue: List[A2AMessage] = []
        self.message_history: List[A2AMessage] = []
        logger.info("A2ACommunicator inicializado")
    
    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        payload: Dict[str, Any]
    ) -> None:
        """Enviar mensagem entre agentes."""
        try:
            message = A2AMessage(
                from_agent=from_agent,
                to_agent=to_agent,
                message_type=message_type,
                payload=payload
            )
            self.message_queue.append(message)
            self.message_history.append(message)
            logger.debug(f"[A2A] Mensagem: {from_agent} -> {to_agent} ({message_type})")
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem A2A: {e}")
            raise
    
    def get_messages_for_agent(self, agent_name: str) -> List[A2AMessage]:
        """Obter mensagens para um agente."""
        messages = [m for m in self.message_queue if m.to_agent == agent_name]
        # Remover mensagens processadas da fila
        self.message_queue = [m for m in self.message_queue if m.to_agent != agent_name]
        logger.debug(f"[A2A] {len(messages)} mensagens para {agent_name}")
        return messages
    
    def get_message_history(
        self,
        from_agent: Optional[str] = None,
        to_agent: Optional[str] = None,
        message_type: Optional[str] = None
    ) -> List[A2AMessage]:
        """Obter histórico de mensagens com filtros opcionais."""
        filtered = self.message_history
        
        if from_agent:
            filtered = [m for m in filtered if m.from_agent == from_agent]
        if to_agent:
            filtered = [m for m in filtered if m.to_agent == to_agent]
        if message_type:
            filtered = [m for m in filtered if m.message_type == message_type]
        
        return filtered
    
    def clear_queue(self) -> None:
        """Limpar fila de mensagens."""
        self.message_queue.clear()
        logger.debug("[A2A] Fila de mensagens limpa")
    
    def get_queue_size(self) -> int:
        """Obter tamanho da fila de mensagens."""
        return len(self.message_queue)


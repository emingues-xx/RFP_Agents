"""Wrapper para LLM com fallback automático."""
from typing import Optional, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from src.utils.llm_factory import LLMFactory
import logging

logger = logging.getLogger(__name__)


class LLMWithFallback:
    """Wrapper de LLM com fallback automático."""
    
    def __init__(self, factory: Optional[LLMFactory] = None, session_id: Optional[str] = None):
        """Inicializar wrapper."""
        self.factory = factory or LLMFactory()
        self.primary_llm: Optional[BaseChatModel] = None
        self.fallback_llm: Optional[BaseChatModel] = None
        self._initialize_llms(session_id=session_id)
    
    def _initialize_llms(self, session_id: Optional[str] = None) -> None:
        """Inicializar LLMs primário e de fallback."""
        try:
            self.primary_llm = self.factory.get_default_llm(session_id=session_id)
            logger.info(f"LLM primário configurado: {self.factory.config.default_provider}")
        except Exception as e:
            logger.warning(f"Erro ao configurar LLM primário: {e}")
            self.primary_llm = None
        
        try:
            self.fallback_llm = self.factory.get_fallback_llm(session_id=session_id)
            logger.info(f"LLM de fallback configurado: {self.factory.config.fallback_provider}")
        except Exception as e:
            logger.warning(f"Erro ao configurar LLM de fallback: {e}")
            self.fallback_llm = None
    
    def invoke(self, messages: list[BaseMessage], **kwargs) -> BaseMessage:
        """Invoke com fallback automático."""
        # Tentar LLM primário
        if self.primary_llm:
            try:
                return self.primary_llm.invoke(messages, **kwargs)
            except Exception as e:
                logger.warning(f"Erro no LLM primário: {e}, tentando fallback...")
        
        # Tentar fallback
        if self.fallback_llm:
            try:
                return self.fallback_llm.invoke(messages, **kwargs)
            except Exception as e:
                logger.error(f"Erro no LLM de fallback: {e}")
                raise
        
        raise RuntimeError("Nenhum LLM disponível")
    
    def get_current_llm(self) -> Optional[BaseChatModel]:
        """Obter LLM atual (primário se disponível, senão fallback)."""
        return self.primary_llm or self.fallback_llm


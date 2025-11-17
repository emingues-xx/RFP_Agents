"""Wrapper para rastreamento de chamadas LLM com Langfuse."""
from typing import Optional, Dict, Any, List
from langfuse.callback import CallbackHandler
from src.utils.langfuse_client import langfuse_client
import logging

logger = logging.getLogger(__name__)


class LangfuseCallbackHandler(CallbackHandler):
    """Callback handler para Langfuse."""
    
    def __init__(self, session_id: Optional[str] = None, **kwargs):
        """Inicializar handler."""
        if langfuse_client.is_enabled():
            try:
                super().__init__(
                    public_key=langfuse_client.public_key,
                    secret_key=langfuse_client.secret_key,
                    host=langfuse_client.host,
                    session_id=session_id,
                    **kwargs
                )
                logger.debug(f"Langfuse callback handler criado (session_id={session_id})")
            except Exception as e:
                logger.error(f"Erro ao criar Langfuse callback handler: {e}")
                raise
        else:
            logger.warning("Langfuse não está habilitado, callback não será criado")
            # Criar um handler vazio para evitar erros
            super().__init__(
                public_key="",
                secret_key="",
                host="",
                session_id=session_id,
                **kwargs
            )
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """Chamado quando LLM inicia."""
        if langfuse_client.is_enabled():
            try:
                super().on_llm_start(serialized, prompts, **kwargs)
            except Exception as e:
                logger.error(f"Erro no on_llm_start do Langfuse: {e}")
    
    def on_llm_end(self, response: Any, **kwargs) -> None:
        """Chamado quando LLM termina."""
        if langfuse_client.is_enabled():
            try:
                super().on_llm_end(response, **kwargs)
            except Exception as e:
                logger.error(f"Erro no on_llm_end do Langfuse: {e}")
    
    def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Chamado quando LLM tem erro."""
        if langfuse_client.is_enabled():
            try:
                super().on_llm_error(error, **kwargs)
            except Exception as e:
                logger.error(f"Erro no on_llm_error do Langfuse: {e}")


def get_langfuse_callback(session_id: Optional[str] = None) -> Optional[LangfuseCallbackHandler]:
    """Obter callback handler do Langfuse."""
    if langfuse_client.is_enabled():
        try:
            return LangfuseCallbackHandler(session_id=session_id)
        except Exception as e:
            logger.error(f"Erro ao criar callback do Langfuse: {e}")
            return None
    return None


# Decorator para rastreamento
from langfuse.decorators import observe, langfuse_context


def track_llm_call(func):
    """Decorator para rastrear chamadas LLM."""
    if not langfuse_client.is_enabled():
        # Se Langfuse não estiver habilitado, retornar função original
        return func
    
    @observe(name=func.__name__)
    def wrapper(*args, **kwargs):
        """Wrapper com rastreamento."""
        try:
            # Adicionar metadados
            langfuse_context.update_current_trace(
                name=func.__name__,
                metadata={
                    "function": func.__name__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys())
                }
            )
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Erro no decorator track_llm_call: {e}")
            return func(*args, **kwargs)
    
    return wrapper


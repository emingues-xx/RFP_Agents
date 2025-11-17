"""Cliente Langfuse para observabilidade."""
from langfuse import Langfuse
from typing import Optional
from src.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)


class LangfuseClient:
    """Cliente Langfuse singleton."""
    
    _instance: Optional['LangfuseClient'] = None
    _client: Optional[Langfuse] = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar cliente Langfuse."""
        if self._client is None:
            settings = get_settings()
            try:
                if settings.langfuse_public_key and settings.langfuse_secret_key:
                    self._client = Langfuse(
                        public_key=settings.langfuse_public_key,
                        secret_key=settings.langfuse_secret_key,
                        host=settings.langfuse_url,
                    )
                    logger.info("Langfuse client inicializado com sucesso")
                else:
                    logger.warning("Langfuse não configurado: API keys não fornecidas")
                    self._client = None
            except Exception as e:
                logger.error(f"Erro ao inicializar Langfuse: {e}")
                self._client = None
    
    @property
    def client(self) -> Optional[Langfuse]:
        """Obter cliente Langfuse."""
        return self._client
    
    def is_enabled(self) -> bool:
        """Verificar se Langfuse está habilitado."""
        return self._client is not None
    
    @property
    def public_key(self) -> Optional[str]:
        """Obter public key."""
        settings = get_settings()
        return settings.langfuse_public_key
    
    @property
    def secret_key(self) -> Optional[str]:
        """Obter secret key."""
        settings = get_settings()
        return settings.langfuse_secret_key
    
    @property
    def host(self) -> str:
        """Obter host URL."""
        settings = get_settings()
        return settings.langfuse_url


# Instância global
langfuse_client = LangfuseClient()


"""Checkpoint para persistência de estado."""
from typing import Any
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from src.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


def create_checkpoint_saver() -> BaseCheckpointSaver:
    """Criar checkpoint saver usando PostgreSQL ou memória."""
    try:
        # Tentar usar PostgreSQL se disponível
        try:
            from langgraph.checkpoint.postgres import PostgresSaver
            from sqlalchemy import create_engine
            
            # Criar engine
            engine = create_engine(settings.database_url)
            
            # Criar PostgresSaver
            checkpoint_saver = PostgresSaver(engine)
            
            # Criar tabelas se não existirem
            checkpoint_saver.setup()
            
            logger.info("Checkpoint saver configurado com PostgreSQL")
            return checkpoint_saver
        except ImportError:
            logger.warning("PostgresSaver não disponível, usando MemorySaver")
            raise
        except Exception as e:
            logger.warning(f"Erro ao configurar PostgreSQL checkpoint: {e}")
            raise
        
    except Exception as e:
        logger.warning(f"Erro ao configurar checkpoint: {e}")
        # Fallback para memória (não persistente)
        logger.info("Usando MemorySaver como fallback")
        return MemorySaver()


"""Gerenciador de memória persistente."""
from typing import List, Optional, Dict, Any
from langchain.memory import ConversationBufferMemory
from langchain.memory.postgres import PostgresChatMessageHistory
from src.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class PersistentMemoryManager:
    """Gerenciador de memória persistente."""
    
    def __init__(self, session_id: str):
        """Inicializar gerenciador."""
        self.session_id = session_id
        self.memory = self._create_memory()
        logger.info(f"Memory manager inicializado para sessão: {session_id}")
    
    def _create_memory(self) -> ConversationBufferMemory:
        """Criar memória persistente."""
        try:
            connection_string = settings.database_url
            
            # Criar histórico no PostgreSQL
            message_history = PostgresChatMessageHistory(
                connection_string=connection_string,
                session_id=self.session_id,
                table_name="chat_history"
            )
            
            # Criar memória com histórico
            memory = ConversationBufferMemory(
                chat_memory=message_history,
                return_messages=True,
                memory_key="chat_history"
            )
            
            logger.debug("Memória persistente criada com sucesso")
            return memory
        except Exception as e:
            logger.error(f"Erro ao criar memória persistente: {e}")
            # Fallback para memória em memória
            logger.warning("Usando memória em memória como fallback")
            return ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history"
            )
    
    def save_context(self, input_str: str, output_str: str) -> None:
        """Salvar contexto na memória."""
        try:
            self.memory.save_context({"input": input_str}, {"output": output_str})
            logger.debug(f"Contexto salvo: input={input_str[:50]}...")
        except Exception as e:
            logger.error(f"Erro ao salvar contexto: {e}")
    
    def load_memory_variables(self) -> Dict[str, Any]:
        """Carregar variáveis da memória."""
        try:
            return self.memory.load_memory_variables({})
        except Exception as e:
            logger.error(f"Erro ao carregar variáveis da memória: {e}")
            return {"chat_history": []}
    
    def clear(self) -> None:
        """Limpar memória."""
        try:
            self.memory.clear()
            logger.info("Memória limpa")
        except Exception as e:
            logger.error(f"Erro ao limpar memória: {e}")


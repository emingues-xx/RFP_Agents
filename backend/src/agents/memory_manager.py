"""Gerenciador de memória persistente."""
from typing import List, Optional, Dict, Any, Union
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.memory.postgres import PostgresChatMessageHistory
from langchain_core.language_models import BaseChatModel
from src.config.settings import get_settings
from src.utils.metrics import (
    memory_messages_total,
    memory_sessions_total
)
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class PersistentMemoryManager:
    """Gerenciador de memória persistente."""
    
    def __init__(
        self,
        session_id: str,
        use_summary: bool = False,
        llm: Optional[BaseChatModel] = None
    ):
        """Inicializar gerenciador.
        
        Args:
            session_id: ID da sessão
            use_summary: Se True, usa ConversationSummaryMemory (requer LLM)
            llm: LLM para ConversationSummaryMemory (obrigatório se use_summary=True)
        """
        self.session_id = session_id
        self.use_summary = use_summary
        self.llm = llm
        
        if use_summary and not llm:
            logger.warning("use_summary=True mas LLM não fornecido, usando ConversationBufferMemory")
            self.use_summary = False
        
        self.memory = self._create_memory()
        
        # Métricas
        memory_sessions_total.inc()
        
        logger.info(f"PersistentMemoryManager inicializado para sessão: {session_id} (summary={use_summary})")
    
    def _create_memory(self) -> Union[ConversationBufferMemory, ConversationSummaryMemory]:
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
            if self.use_summary and self.llm:
                # Usar summary memory para sessões longas
                memory = ConversationSummaryMemory(
                    llm=self.llm,
                    chat_memory=message_history,
                    return_messages=True,
                    memory_key="chat_history"
                )
                logger.debug("ConversationSummaryMemory criada com sucesso")
            else:
                memory = ConversationBufferMemory(
                    chat_memory=message_history,
                    return_messages=True,
                    memory_key="chat_history"
                )
                logger.debug("ConversationBufferMemory criada com sucesso")
            
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
            
            # Métricas
            memory_messages_total.inc()
            
            logger.debug(f"Contexto salvo: input={input_str[:50]}...")
        except Exception as e:
            logger.error(f"Erro ao salvar contexto: {e}")
            raise
    
    def load_memory_variables(self) -> Dict[str, Any]:
        """Carregar variáveis da memória."""
        try:
            return self.memory.load_memory_variables({})
        except Exception as e:
            logger.error(f"Erro ao carregar variáveis da memória: {e}")
            return {"chat_history": []}
    
    def get_conversation_summary(self) -> str:
        """Obter resumo da conversa.
        
        Returns:
            Resumo textual da conversa
        """
        try:
            memory_vars = self.memory.load_memory_variables({})
            messages = memory_vars.get("chat_history", [])
            
            if not messages:
                return "Nenhuma conversa anterior."
            
            # Se é ConversationSummaryMemory, pode ter summary
            if isinstance(self.memory, ConversationSummaryMemory):
                # Tentar obter summary se disponível
                if hasattr(self.memory, 'moving_summary_buffer'):
                    summary = self.memory.moving_summary_buffer
                    if summary:
                        return f"Resumo da conversa:\n{summary}\n\nÚltimas mensagens:\n"
            
            # Criar resumo manual das últimas mensagens
            summary = f"Histórico com {len(messages)} mensagens:\n\n"
            for i, msg in enumerate(messages[-5:], 1):  # Últimas 5 mensagens
                role = "Usuário" if hasattr(msg, 'type') and msg.type == "human" else "Agente"
                content = msg.content if hasattr(msg, 'content') else str(msg)
                summary += f"[{i}] {role}: {content[:100]}{'...' if len(content) > 100 else ''}\n"
            
            return summary
        except Exception as e:
            logger.error(f"Erro ao obter resumo: {e}")
            return ""
    
    def get_message_count(self) -> int:
        """Obter número de mensagens na memória.
        
        Returns:
            Número de mensagens
        """
        try:
            memory_vars = self.memory.load_memory_variables({})
            messages = memory_vars.get("chat_history", [])
            return len(messages)
        except Exception as e:
            logger.error(f"Erro ao contar mensagens: {e}")
            return 0
    
    def clear(self) -> None:
        """Limpar memória."""
        try:
            self.memory.clear()
            logger.info(f"Memória limpa para sessão: {self.session_id}")
        except Exception as e:
            logger.error(f"Erro ao limpar memória: {e}")
            raise


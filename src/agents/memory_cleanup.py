"""Limpeza automática de memória antiga."""
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from src.config.settings import get_settings
from src.utils.metrics import memory_sessions_total
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class MemoryCleanup:
    """Gerenciador de limpeza de memória."""
    
    def __init__(self, retention_days: int = 90):
        """Inicializar limpeza.
        
        Args:
            retention_days: Número de dias para reter mensagens (padrão: 90)
        """
        self.retention_days = retention_days
        self.engine = create_engine(settings.database_url)
        logger.info(f"MemoryCleanup inicializado (retention: {retention_days} dias)")
    
    def cleanup_old_sessions(self) -> int:
        """Limpar sessões antigas.
        
        Returns:
            Número de registros removidos
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        try:
            with self.engine.connect() as conn:
                # Verificar se tabela existe
                check_table = conn.execute(
                    text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'chat_history'
                        );
                    """)
                )
                
                if not check_table.scalar():
                    logger.warning("Tabela chat_history não existe, nada para limpar")
                    return 0
                
                # Contar registros antes da limpeza
                count_before = conn.execute(
                    text("SELECT COUNT(*) FROM chat_history WHERE created_at < :cutoff_date"),
                    {"cutoff_date": cutoff_date}
                ).scalar()
                
                if count_before == 0:
                    logger.info("Nenhum registro antigo para limpar")
                    return 0
                
                # Deletar registros antigos
                result = conn.execute(
                    text("""
                        DELETE FROM chat_history 
                        WHERE created_at < :cutoff_date
                    """),
                    {"cutoff_date": cutoff_date}
                )
                deleted = result.rowcount
                conn.commit()
                
                logger.info(f"Limpeza concluída: {deleted} registros removidos (anteriores a {cutoff_date.date()})")
                return deleted
                
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")
            return 0
    
    def cleanup_by_session(self, session_id: str) -> int:
        """Limpar memória de uma sessão específica.
        
        Args:
            session_id: ID da sessão a limpar
        
        Returns:
            Número de registros removidos
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        DELETE FROM chat_history 
                        WHERE session_id = :session_id
                    """),
                    {"session_id": session_id}
                )
                deleted = result.rowcount
                conn.commit()
                
                logger.info(f"Limpeza da sessão {session_id}: {deleted} registros removidos")
                return deleted
                
        except Exception as e:
            logger.error(f"Erro ao limpar sessão {session_id}: {e}")
            return 0
    
    def get_session_count(self) -> int:
        """Obter número de sessões únicas.
        
        Returns:
            Número de sessões
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT COUNT(DISTINCT session_id) FROM chat_history")
                )
                count = result.scalar() or 0
                return count
        except Exception as e:
            logger.error(f"Erro ao contar sessões: {e}")
            return 0
    
    def get_message_count(self) -> int:
        """Obter número total de mensagens.
        
        Returns:
            Número de mensagens
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT COUNT(*) FROM chat_history")
                )
                count = result.scalar() or 0
                return count
        except Exception as e:
            logger.error(f"Erro ao contar mensagens: {e}")
            return 0
    
    def get_old_sessions(self, days: Optional[int] = None) -> List[str]:
        """Obter lista de sessões antigas.
        
        Args:
            days: Número de dias (usa retention_days se None)
        
        Returns:
            Lista de session_ids antigas
        """
        cutoff_days = days or self.retention_days
        cutoff_date = datetime.now() - timedelta(days=cutoff_days)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT DISTINCT session_id 
                        FROM chat_history 
                        WHERE created_at < :cutoff_date
                    """),
                    {"cutoff_date": cutoff_date}
                )
                sessions = [row[0] for row in result]
                return sessions
        except Exception as e:
            logger.error(f"Erro ao obter sessões antigas: {e}")
            return []


#!/usr/bin/env python
"""Worker RQ para processar RFPs em background."""
import os
import sys
import logging

# Configurar path para importações
# O worker será executado de /app no Docker
if '/app' not in sys.path:
    sys.path.insert(0, '/app')

from redis import Redis
from rq import Worker, Queue, Connection
from src.config.settings import get_settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


def create_redis_connection() -> Redis:
    """Criar conexão Redis."""
    redis_url = settings.redis_url
    return Redis.from_url(redis_url, decode_responses=True)


def main():
    """Função principal do worker."""
    logger.info("Iniciando worker RQ...")
    
    # Criar conexão Redis
    redis_conn = create_redis_connection()
    
    # Criar fila
    queue = Queue("rfp-queue", connection=redis_conn)
    
    # Criar worker
    worker = Worker([queue], connection=redis_conn, name="rfp-worker")
    
    logger.info(f"Worker iniciado. Escutando fila: {queue.name}")
    logger.info("Pressione Ctrl+C para parar")
    
    try:
        # Iniciar worker
        worker.work(with_scheduler=True)
    except KeyboardInterrupt:
        logger.info("Worker interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro no worker: {e}")
        raise


if __name__ == "__main__":
    main()


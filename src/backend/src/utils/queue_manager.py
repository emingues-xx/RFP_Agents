"""Gerenciador de filas Redis Queue (RQ)."""
from typing import Optional, Dict, Any
from redis import Redis
from rq import Queue, Job
from rq.job import JobStatus
from src.config.settings import get_settings
from src.utils.metrics import (
    queue_jobs_total,
    queue_job_duration_seconds,
    queue_size
)
import logging
import time

logger = logging.getLogger(__name__)
settings = get_settings()

# Instância global do Redis
_redis_connection: Optional[Redis] = None
_rq_queue: Optional[Queue] = None


def get_redis_connection() -> Redis:
    """Obter conexão Redis (singleton)."""
    global _redis_connection
    if _redis_connection is None:
        # Parsear REDIS_URL
        redis_url = settings.redis_url
        _redis_connection = Redis.from_url(
            redis_url,
            decode_responses=True
        )
        logger.info("Conexão Redis criada para RQ")
    return _redis_connection


def get_queue(queue_name: str = "rfp-queue") -> Queue:
    """Obter fila RQ (singleton).
    
    Args:
        queue_name: Nome da fila
    
    Returns:
        Instância da fila RQ
    """
    global _rq_queue
    if _rq_queue is None:
        redis_conn = get_redis_connection()
        _rq_queue = Queue(queue_name, connection=redis_conn)
        logger.info(f"Fila RQ '{queue_name}' criada")
    return _rq_queue


def enqueue_rfp_processing(
    input_text: str,
    session_id: str,
    file_path: Optional[str] = None
) -> str:
    """Enfileirar processamento de RFP.
    
    Args:
        input_text: Texto de entrada do RFP
        session_id: ID da sessão
        file_path: Caminho do arquivo (opcional)
    
    Returns:
        Job ID
    """
    from src.utils.queue_jobs import process_rfp_job
    
    queue = get_queue()
    
    # Enfileirar job
    job = queue.enqueue(
        process_rfp_job,
        input_text,
        session_id,
        file_path,
        job_timeout="30m",  # Timeout de 30 minutos
        result_ttl=86400,  # Resultado válido por 24 horas
        failure_ttl=86400  # Falhas mantidas por 24 horas
    )
    
    # Métricas
    queue_jobs_total.labels(status="queued", queue=queue.name).inc()
    
    # Atualizar tamanho da fila
    queue_size.labels(queue=queue.name).set(queue.count)
    
    logger.info(f"RFP enfileirado: job_id={job.id}, session_id={session_id}")
    return job.id


def get_job_status(job_id: str) -> Dict[str, Any]:
    """Obter status de um job.
    
    Args:
        job_id: ID do job
    
    Returns:
        Dicionário com status do job
    """
    try:
        job = Job.fetch(job_id, connection=get_redis_connection())
        
        status_info = {
            "job_id": job.id,
            "status": job.get_status(),
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None,
            "result": None,
            "error": None
        }
        
        # Adicionar resultado se disponível
        if job.is_finished:
            try:
                status_info["result"] = job.result
            except Exception as e:
                logger.warning(f"Erro ao obter resultado do job {job_id}: {e}")
        
        # Adicionar erro se houver
        if job.is_failed:
            try:
                status_info["error"] = str(job.exc_info)
            except Exception:
                status_info["error"] = "Erro desconhecido"
        
        # Calcular duração se disponível
        if job.started_at and job.ended_at:
            duration = (job.ended_at - job.started_at).total_seconds()
            queue_job_duration_seconds.labels(queue="rfp-queue").observe(duration)
        
        return status_info
        
    except Exception as e:
        logger.error(f"Erro ao obter status do job {job_id}: {e}")
        return {
            "job_id": job_id,
            "status": "not_found",
            "error": str(e)
        }


def get_job_result(job_id: str) -> Optional[Dict[str, Any]]:
    """Obter resultado de um job.
    
    Args:
        job_id: ID do job
    
    Returns:
        Resultado do job ou None se não disponível
    """
    try:
        job = Job.fetch(job_id, connection=get_redis_connection())
        
        if job.is_finished:
            return job.result
        elif job.is_failed:
            raise Exception(f"Job falhou: {job.exc_info}")
        else:
            return None  # Job ainda em execução
            
    except Exception as e:
        logger.error(f"Erro ao obter resultado do job {job_id}: {e}")
        raise


def get_queue_info(queue_name: str = "rfp-queue") -> Dict[str, Any]:
    """Obter informações da fila.
    
    Args:
        queue_name: Nome da fila
    
    Returns:
        Dicionário com informações da fila
    """
    queue = get_queue(queue_name)
    
    return {
        "name": queue.name,
        "count": queue.count,  # Jobs na fila
        "started_jobs": len(queue.started_job_registry),
        "finished_jobs": len(queue.finished_job_registry),
        "failed_jobs": len(queue.failed_job_registry),
        "deferred_jobs": len(queue.deferred_job_registry),
        "scheduled_jobs": len(queue.scheduled_job_registry)
    }


"""Rotas de API para Queue System."""
from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from src.utils.queue_manager import (
    enqueue_rfp_processing,
    get_job_status,
    get_job_result,
    get_queue_info
)
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rfps/queue", tags=["queue"])


class QueueRFPRequest(BaseModel):
    """Request para enfileirar RFP."""
    input_text: str
    session_id: Optional[str] = None
    file_path: Optional[str] = None


class QueueRFPResponse(BaseModel):
    """Response ao enfileirar RFP."""
    job_id: str
    session_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    """Response com status do job."""
    job_id: str
    status: str
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None


class QueueInfoResponse(BaseModel):
    """Response com informações da fila."""
    name: str
    count: int
    started_jobs: int
    finished_jobs: int
    failed_jobs: int
    deferred_jobs: int
    scheduled_jobs: int


@router.post("", response_model=QueueRFPResponse)
async def queue_rfp(request: QueueRFPRequest):
    """Enfileirar RFP para processamento.
    
    Args:
        request: Dados do RFP a processar
    
    Returns:
        Informações do job enfileirado
    """
    try:
        # Gerar session_id se não fornecido
        session_id = request.session_id or f"session-{uuid.uuid4().hex[:8]}"
        
        # Enfileirar
        job_id = enqueue_rfp_processing(
            input_text=request.input_text,
            session_id=session_id,
            file_path=request.file_path
        )
        
        logger.info(f"RFP enfileirado: job_id={job_id}, session_id={session_id}")
        
        return QueueRFPResponse(
            job_id=job_id,
            session_id=session_id,
            status="queued",
            message="RFP enfileirado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao enfileirar RFP: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status_endpoint(job_id: str):
    """Obter status de um job.
    
    Args:
        job_id: ID do job
    
    Returns:
        Status do job
    """
    try:
        status_info = get_job_status(job_id)
        
        if status_info["status"] == "not_found":
            raise HTTPException(status_code=404, detail="Job não encontrado")
        
        return JobStatusResponse(**status_info)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status do job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/result")
async def get_job_result_endpoint(job_id: str):
    """Obter resultado de um job.
    
    Args:
        job_id: ID do job
    
    Returns:
        Resultado do job
    """
    try:
        result = get_job_result(job_id)
        
        if result is None:
            raise HTTPException(
                status_code=202,
                detail="Job ainda em execução"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter resultado do job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info", response_model=QueueInfoResponse)
async def get_queue_info_endpoint():
    """Obter informações da fila.
    
    Returns:
        Informações da fila
    """
    try:
        info = get_queue_info()
        return QueueInfoResponse(**info)
        
    except Exception as e:
        logger.error(f"Erro ao obter informações da fila: {e}")
        raise HTTPException(status_code=500, detail=str(e))


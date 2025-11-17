"""Jobs para processamento em background usando RQ."""
from typing import Dict, Any, Optional
from src.workflows.workflow import RFPWorkflow
from src.utils.metrics import (
    queue_jobs_total,
    queue_job_duration_seconds
)
import logging
import time

logger = logging.getLogger(__name__)


def process_rfp_job(
    input_text: str,
    session_id: str,
    file_path: Optional[str] = None
) -> Dict[str, Any]:
    """Job para processar RFP em background.
    
    Args:
        input_text: Texto de entrada do RFP
        session_id: ID da sessão
        file_path: Caminho do arquivo (opcional)
    
    Returns:
        Resultado do workflow
    """
    start_time = time.time()
    
    try:
        logger.info(f"Iniciando processamento de RFP: session_id={session_id}")
        
        # Métricas
        queue_jobs_total.labels(status="started", queue="rfp-queue").inc()
        
        # Criar e executar workflow
        workflow = RFPWorkflow()
        
        # Preparar estado inicial
        initial_state = {
            "input_text": input_text,
            "input_type": None,
            "file_path": file_path,
            "context": {},
            "messages": [],
            "parsed_questions": None,
            "generated_responses": None,
            "verified_responses": None,
            "session_id": session_id,
            "workflow_id": f"wf-{session_id}",
            "current_step": "entry",
            "errors": [],
            "requires_approval": False,
            "approval_status": None,
            "approval_id": None,
            "coordination_plan": None
        }
        
        config = {
            "configurable": {"thread_id": session_id}
        }
        
        # Executar workflow
        result = workflow.app.invoke(initial_state, config=config)
        
        # Calcular duração
        duration = time.time() - start_time
        queue_job_duration_seconds.labels(queue="rfp-queue").observe(duration)
        queue_jobs_total.labels(status="completed", queue="rfp-queue").inc()
        
        logger.info(f"RFP processado com sucesso: session_id={session_id}, duration={duration:.2f}s")
        
        return {
            "success": True,
            "session_id": session_id,
            "workflow_id": result.get("workflow_id"),
            "result": result,
            "duration": duration
        }
        
    except Exception as e:
        # Métricas de erro
        duration = time.time() - start_time
        queue_job_duration_seconds.labels(queue="rfp-queue").observe(duration)
        queue_jobs_total.labels(status="failed", queue="rfp-queue").inc()
        
        logger.error(f"Erro ao processar RFP: session_id={session_id}, error={e}")
        
        return {
            "success": False,
            "session_id": session_id,
            "error": str(e),
            "duration": duration
        }


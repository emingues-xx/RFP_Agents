"""Rotas de API para workflow."""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from src.workflows.workflow import RFPWorkflow
from src.api.models.approval import ApprovalRequest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.settings import get_settings
import uuid
import tempfile
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/workflow", tags=["workflow"])
settings = get_settings()


class ProcessRequest(BaseModel):
    """Request para processar texto."""
    input_text: str
    session_id: Optional[str] = None


class ProcessResponse(BaseModel):
    """Resposta do processamento."""
    workflow_id: str
    session_id: str
    status: str
    requires_approval: bool
    approval_id: Optional[str] = None
    responses: list


@router.post("/process", response_model=ProcessResponse)
async def process_text(request: ProcessRequest):
    """Processar texto através do workflow.
    
    Args:
        request: Request com texto de entrada
    
    Returns:
        Resultado do workflow
    """
    try:
        session_id = request.session_id or f"session-{uuid.uuid4().hex[:8]}"
        
        workflow = RFPWorkflow()
        result = workflow.run(
            input_text=request.input_text,
            session_id=session_id
        )
        
        # Extrair informações relevantes
        approval_id = result.get("approval_id")
        verified_responses = result.get("verified_responses", [])
        
        # Converter respostas para formato serializável
        responses_data = []
        for resp in verified_responses:
            if isinstance(resp, dict):
                responses_data.append(resp)
            else:
                # Se for objeto Pydantic
                responses_data.append(resp.model_dump() if hasattr(resp, 'model_dump') else resp.dict())
        
        return ProcessResponse(
            workflow_id=result.get("workflow_id", f"wf-{session_id}"),
            session_id=session_id,
            status=result.get("current_step", "completed"),
            requires_approval=result.get("requires_approval", False),
            approval_id=approval_id,
            responses=responses_data
        )
    except Exception as e:
        logger.error(f"Erro ao processar texto: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-file", response_model=ProcessResponse)
async def process_file(file: UploadFile = File(...)):
    """Processar arquivo através do workflow.
    
    Args:
        file: Arquivo a ser processado (PDF, DOCX, Excel, CSV)
    
    Returns:
        Resultado do workflow
    """
    try:
        session_id = f"session-{uuid.uuid4().hex[:8]}"
        
        # Salvar arquivo temporariamente
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Criar workflow e processar
            workflow = RFPWorkflow()
            
            # Preparar estado inicial com arquivo
            from src.workflows.state import WorkflowState
            initial_state: WorkflowState = {
                "input_text": f"Processar arquivo: {file.filename}",
                "input_type": None,
                "file_path": tmp_file_path,
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
            
            config = {"configurable": {"thread_id": session_id}}
            result = workflow.app.invoke(initial_state, config=config)
            
            # Extrair informações
            approval_id = result.get("approval_id")
            verified_responses = result.get("verified_responses", [])
            
            # Converter respostas
            responses_data = []
            for resp in verified_responses:
                if isinstance(resp, dict):
                    responses_data.append(resp)
                else:
                    responses_data.append(resp.model_dump() if hasattr(resp, 'model_dump') else resp.dict())
            
            return ProcessResponse(
                workflow_id=result.get("workflow_id", f"wf-{session_id}"),
                session_id=session_id,
                status=result.get("current_step", "completed"),
                requires_approval=result.get("requires_approval", False),
                approval_id=approval_id,
                responses=responses_data
            )
        finally:
            # Limpar arquivo temporário
            try:
                os.unlink(tmp_file_path)
            except Exception as e:
                logger.warning(f"Erro ao remover arquivo temporário: {e}")
                
    except Exception as e:
        logger.error(f"Erro ao processar arquivo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


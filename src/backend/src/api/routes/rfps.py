"""Rotas de API para RFPs."""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
from src.api.models.approval import ApprovalRequest, ApprovalRequestModel, ApprovalStatus
from src.utils.portal_extractor import PortalExtractor
from src.agents.parser import ParserAgent
from src.utils.llm_factory import LLMFactory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.settings import get_settings
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rfps", tags=["rfps"])
settings = get_settings()


class RFPListItem(BaseModel):
    """Item da lista de RFPs."""
    id: str
    workflow_id: str
    session_id: str
    status: str
    created_at: str
    input_type: Optional[str] = None


class RFPDetail(BaseModel):
    """Detalhes de um RFP."""
    workflow_id: str
    session_id: str
    responses: List[dict]
    status: str
    created_at: str
    approval_id: Optional[str] = None


@router.get("", response_model=List[RFPListItem])
async def get_rfps(filter: str = "all"):
    """Obter lista de RFPs processados.
    
    Args:
        filter: Filtro de status (all, pending, approved, rejected)
    
    Returns:
        Lista de RFPs
    """
    try:
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            query = session.query(ApprovalRequestModel)
            
            # Aplicar filtro
            if filter == "pending":
                query = query.filter_by(status=ApprovalStatus.PENDING.value)
            elif filter == "approved":
                query = query.filter_by(status=ApprovalStatus.APPROVED.value)
            elif filter == "rejected":
                query = query.filter_by(status=ApprovalStatus.REJECTED.value)
            # "all" não aplica filtro
            
            approvals = query.order_by(ApprovalRequestModel.created_at.desc()).all()
            
            return [
                RFPListItem(
                    id=a.id,
                    workflow_id=a.workflow_id,
                    session_id=a.session_id,
                    status=a.status,
                    created_at=a.created_at.isoformat(),
                    input_type=None  # Pode ser extraído de responses se necessário
                )
                for a in approvals
            ]
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Erro ao buscar RFPs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}", response_model=RFPDetail)
async def get_rfp_detail(workflow_id: str):
    """Obter detalhes de um RFP.
    
    Args:
        workflow_id: ID do workflow
    
    Returns:
        Detalhes do RFP
    """
    try:
        # Buscar aprovações do workflow
        approvals = ApprovalRequest.get_by_workflow_id(workflow_id)
        
        if not approvals:
            raise HTTPException(status_code=404, detail="RFP não encontrado")
        
        # Usar a aprovação mais recente
        latest_approval = approvals[0]
        
        return RFPDetail(
            workflow_id=latest_approval.workflow_id,
            session_id=latest_approval.session_id,
            responses=latest_approval.responses,
            status=latest_approval.status.value,
            created_at=latest_approval.created_at.isoformat(),
            approval_id=latest_approval.id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar detalhes do RFP: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ImportFromPortalRequest(BaseModel):
    """Request para importar RFP de portal."""
    portal_url: str
    portal_type: Optional[str] = None
    auto_process: bool = False  # Se True, inicia processamento automaticamente


class ImportFromPortalResponse(BaseModel):
    """Response da importação de portal."""
    success: bool
    portal_url: str
    portal_type: str
    questionnaire_text: Optional[str] = None
    parsed_questions: Optional[List[dict]] = None
    question_count: Optional[int] = None
    job_id: Optional[str] = None  # Se auto_process=True
    message: str


@router.post("/import-from-portal", response_model=ImportFromPortalResponse)
async def import_from_portal(request: ImportFromPortalRequest):
    """Importar questionário de um portal via MCP.
    
    Args:
        request: Dados do portal a importar
    
    Returns:
        Questionário extraído e parseado
    """
    try:
        extractor = PortalExtractor()
        
        # Extrair questionário
        extraction_result = await extractor.extract_from_portal(
            portal_url=request.portal_url,
            portal_type=request.portal_type
        )
        
        if not extraction_result["success"]:
            raise HTTPException(
                status_code=400,
                detail="Falha na extração do portal"
            )
        
        questionnaire_text = extraction_result["questionnaire"]
        portal_type = extraction_result["portal_type"]
        
        # Se auto_process, enfileirar para processamento
        job_id = None
        if request.auto_process:
            from src.utils.queue_manager import enqueue_rfp_processing
            session_id = f"portal-{uuid.uuid4().hex[:8]}"
            job_id = enqueue_rfp_processing(
                input_text=questionnaire_text,
                session_id=session_id
            )
            logger.info(f"Portal importado e enfileirado: job_id={job_id}")
        
        # Parsear perguntas
        parsed_questions = None
        question_count = 0
        
        try:
            factory = LLMFactory()
            llm = factory.get_default_llm(session_id="portal-import")
            parser = ParserAgent(llm=llm)
            parsed = parser.normalize_questions(questionnaire_text)
            parsed_questions = [
                q.model_dump() if hasattr(q, 'model_dump') else q
                for q in parsed
            ]
            question_count = len(parsed_questions)
        except Exception as e:
            logger.warning(f"Erro ao parsear perguntas: {e}")
            # Continuar mesmo se parsing falhar
        
        return ImportFromPortalResponse(
            success=True,
            portal_url=request.portal_url,
            portal_type=portal_type,
            questionnaire_text=questionnaire_text[:1000] if questionnaire_text else None,  # Primeiros 1000 chars
            parsed_questions=parsed_questions,
            question_count=question_count,
            job_id=job_id,
            message="Questionário importado com sucesso"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao importar do portal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


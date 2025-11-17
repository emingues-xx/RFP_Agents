"""Rotas de API para RFPs."""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from src.api.models.approval import ApprovalRequest, ApprovalRequestModel, ApprovalStatus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.settings import get_settings
import logging

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


"""Rotas de API para aprovações."""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from src.api.models.approval import ApprovalRequest, ApprovalStatus, ApprovalRequestModel
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.settings import get_settings
from src.utils.notifications import NotificationService
from src.utils.metrics import hitl_approvals_total
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/approvals", tags=["approvals"])
settings = get_settings()


class ApprovalResponse(BaseModel):
    """Resposta de aprovação."""
    id: str
    workflow_id: str
    session_id: str
    status: str
    responses: List[dict]
    created_at: str
    updated_at: Optional[str] = None
    approved_by: Optional[str] = None
    comments: Optional[str] = None


class ApproveRequest(BaseModel):
    """Request para aprovar."""
    comments: Optional[str] = None
    approved_by: Optional[str] = None


class RejectRequest(BaseModel):
    """Request para rejeitar."""
    comments: Optional[str] = None


class EditRequest(BaseModel):
    """Request para editar."""
    responses: List[dict]
    comments: Optional[str] = None


@router.get("/pending", response_model=List[ApprovalResponse])
async def get_pending_approvals():
    """Obter aprovações pendentes."""
    try:
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            pending = session.query(ApprovalRequestModel).filter_by(
                status=ApprovalStatus.PENDING.value
            ).order_by(ApprovalRequestModel.created_at.desc()).all()
            
            return [
                ApprovalResponse(
                    id=p.id,
                    workflow_id=p.workflow_id,
                    session_id=p.session_id,
                    status=p.status,
                    responses=json.loads(p.responses) if p.responses else [],
                    created_at=p.created_at.isoformat(),
                    updated_at=p.updated_at.isoformat() if p.updated_at else None,
                    approved_by=p.approved_by,
                    comments=p.comments
                )
                for p in pending
            ]
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Erro ao buscar aprovações pendentes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{approval_id}", response_model=ApprovalResponse)
async def get_approval(approval_id: str):
    """Obter aprovação por ID."""
    approval = ApprovalRequest.get_by_id(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Aprovação não encontrada")
    
    return ApprovalResponse(
        id=approval.id,
        workflow_id=approval.workflow_id,
        session_id=approval.session_id,
        status=approval.status.value,
        responses=approval.responses,
        created_at=approval.created_at.isoformat(),
        updated_at=approval.updated_at.isoformat() if approval.updated_at else None,
        approved_by=approval.approved_by,
        comments=approval.comments
    )


@router.post("/{approval_id}/approve")
async def approve(approval_id: str, request: ApproveRequest):
    """Aprovar resposta."""
    try:
        approval = ApprovalRequest.get_by_id(approval_id)
        if not approval:
            raise HTTPException(status_code=404, detail="Aprovação não encontrada")
        
        if approval.status != ApprovalStatus.PENDING:
            raise HTTPException(status_code=400, detail="Aprovação já processada")
        
        approval.status = ApprovalStatus.APPROVED
        approval.comments = request.comments
        approval.approved_by = request.approved_by or "user"  # TODO: Obter do contexto de autenticação
        approval.updated_at = datetime.utcnow()
        approval.save()
        
        # Métricas
        hitl_approvals_total.labels(status="approved").inc()
        
        # Notificar
        NotificationService.notify_approval_approved(
            approval_id=approval_id,
            workflow_id=approval.workflow_id,
            approved_by=approval.approved_by
        )
        
        return {"status": "approved", "approval_id": approval_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao aprovar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{approval_id}/reject")
async def reject(approval_id: str, request: RejectRequest):
    """Rejeitar resposta."""
    try:
        approval = ApprovalRequest.get_by_id(approval_id)
        if not approval:
            raise HTTPException(status_code=404, detail="Aprovação não encontrada")
        
        if approval.status != ApprovalStatus.PENDING:
            raise HTTPException(status_code=400, detail="Aprovação já processada")
        
        approval.status = ApprovalStatus.REJECTED
        approval.comments = request.comments
        approval.updated_at = datetime.utcnow()
        approval.save()
        
        # Métricas
        hitl_approvals_total.labels(status="rejected").inc()
        
        # Notificar
        NotificationService.notify_approval_rejected(
            approval_id=approval_id,
            workflow_id=approval.workflow_id,
            comments=request.comments
        )
        
        return {"status": "rejected", "approval_id": approval_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao rejeitar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{approval_id}/edit")
async def edit(approval_id: str, request: EditRequest):
    """Editar resposta antes de aprovar."""
    try:
        approval = ApprovalRequest.get_by_id(approval_id)
        if not approval:
            raise HTTPException(status_code=404, detail="Aprovação não encontrada")
        
        if approval.status not in [ApprovalStatus.PENDING, ApprovalStatus.EDITED]:
            raise HTTPException(status_code=400, detail="Aprovação já processada")
        
        approval.responses = request.responses
        approval.status = ApprovalStatus.EDITED
        approval.comments = request.comments
        approval.updated_at = datetime.utcnow()
        approval.save()
        
        return {"status": "edited", "approval_id": approval_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao editar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{workflow_id}", response_model=List[ApprovalResponse])
async def get_approval_history(workflow_id: str):
    """Obter histórico de aprovações de um workflow."""
    try:
        approvals = ApprovalRequest.get_by_workflow_id(workflow_id)
        
        return [
            ApprovalResponse(
                id=a.id,
                workflow_id=a.workflow_id,
                session_id=a.session_id,
                status=a.status.value,
                responses=a.responses,
                created_at=a.created_at.isoformat(),
                updated_at=a.updated_at.isoformat() if a.updated_at else None,
                approved_by=a.approved_by,
                comments=a.comments
            )
            for a in approvals
        ]
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de aprovações: {e}")
        raise HTTPException(status_code=500, detail=str(e))


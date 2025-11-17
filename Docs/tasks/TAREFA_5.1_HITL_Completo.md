# Tarefa 5.1: Implementação de HITL Completo

## Objetivo
Implementar Human-in-the-Loop (HITL) completo com checkpoint no workflow que pausa para aprovação, API endpoints e gerenciamento de aprovações.

## Prioridade
Alta

## Estimativa
3 dias

## Responsável
Backend

---

## Instruções de Implementação

### 1. Implementar Checkpoint no Workflow que Pausa para Aprovação

#### Criar `src/workflows/hitl_node.py`:
```python
"""Node de HITL para aprovação humana."""
from typing import Dict, Any
from src.workflows.state import WorkflowState
import logging

logger = logging.getLogger(__name__)


def hitl_approval_node(state: WorkflowState) -> WorkflowState:
    """Node que pausa workflow para aprovação humana."""
    logger.info("Workflow pausado para aprovação humana")
    
    # Marcar que requer aprovação
    state["requires_approval"] = True
    state["approval_status"] = "pending"
    state["current_step"] = "awaiting_approval"
    
    # Criar registro de aprovação
    from src.api.models.approval import ApprovalRequest
    approval_request = ApprovalRequest.create_from_state(state)
    approval_id = approval_request.save()
    
    state["approval_id"] = approval_id
    logger.info(f"Aprovação criada: {approval_id}")
    
    return state


def check_approval_status(state: WorkflowState) -> str:
    """Verificar status de aprovação e rotear."""
    approval_status = state.get("approval_status")
    
    if approval_status == "approved":
        return "continue"
    elif approval_status == "rejected":
        return "reject"
    elif approval_status == "pending":
        return "wait"
    else:
        return "wait"
```

### 2. Criar Modelo de Dados para Aprovações

#### Criar `src/api/models/approval.py`:
```python
"""Modelos de dados para aprovações."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum
import uuid

Base = declarative_base()


class ApprovalStatus(str, Enum):
    """Status de aprovação."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"


class ApprovalRequestModel(Base):
    """Modelo SQLAlchemy para aprovações."""
    __tablename__ = "approval_requests"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    responses = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_by = Column(String, nullable=True)
    comments = Column(Text, nullable=True)


class ApprovalRequest(BaseModel):
    """Modelo Pydantic para aprovações."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    session_id: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    responses: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    comments: Optional[str] = None
    
    @classmethod
    def create_from_state(cls, state: WorkflowState) -> "ApprovalRequest":
        """Criar a partir do estado do workflow."""
        return cls(
            workflow_id=state["workflow_id"],
            session_id=state["session_id"],
            responses=state.get("verified_responses", [])
        )
    
    def save(self) -> str:
        """Salvar no banco de dados."""
        from src.config.settings import get_settings
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        settings = get_settings()
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            db_model = ApprovalRequestModel(
                id=self.id,
                workflow_id=self.workflow_id,
                session_id=self.session_id,
                status=self.status.value,
                responses=str(self.responses),
                created_at=self.created_at
            )
            session.add(db_model)
            session.commit()
            return self.id
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    
    @classmethod
    def get_by_id(cls, approval_id: str) -> Optional["ApprovalRequest"]:
        """Obter por ID."""
        from src.config.settings import get_settings
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        settings = get_settings()
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            db_model = session.query(ApprovalRequestModel).filter_by(id=approval_id).first()
            if not db_model:
                return None
            
            import json
            return cls(
                id=db_model.id,
                workflow_id=db_model.workflow_id,
                session_id=db_model.session_id,
                status=ApprovalStatus(db_model.status),
                responses=json.loads(db_model.responses) if db_model.responses else [],
                created_at=db_model.created_at,
                updated_at=db_model.updated_at,
                approved_by=db_model.approved_by,
                comments=db_model.comments
            )
        finally:
            session.close()
```

### 3. Implementar API Endpoints para Aprovação

#### Criar `src/api/routes/approvals.py`:
```python
"""Rotas de API para aprovações."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from src.api.models.approval import ApprovalRequest, ApprovalStatus
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/approvals", tags=["approvals"])


class ApprovalResponse(BaseModel):
    """Resposta de aprovação."""
    id: str
    workflow_id: str
    status: str
    responses: List[dict]
    created_at: str
    comments: Optional[str] = None


class ApproveRequest(BaseModel):
    """Request para aprovar."""
    comments: Optional[str] = None


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
        # Buscar todas as aprovações pendentes
        from src.config.settings import get_settings
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from src.api.models.approval import ApprovalRequestModel
        
        settings = get_settings()
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            pending = session.query(ApprovalRequestModel).filter_by(
                status=ApprovalStatus.PENDING.value
            ).all()
            
            import json
            return [
                ApprovalResponse(
                    id=p.id,
                    workflow_id=p.workflow_id,
                    status=p.status,
                    responses=json.loads(p.responses) if p.responses else [],
                    created_at=p.created_at.isoformat(),
                    comments=p.comments
                )
                for p in pending
            ]
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Erro ao buscar aprovações pendentes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
        approval.approved_by = "user"  # TODO: Obter do contexto de autenticação
        approval.updated_at = datetime.utcnow()
        approval.save()
        
        # Atualizar estado do workflow
        from src.workflows.workflow import RFPWorkflow
        workflow = RFPWorkflow()
        # TODO: Resumir workflow com aprovação
        
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
        
        if approval.status != ApprovalStatus.PENDING:
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


@router.get("/{approval_id}", response_model=ApprovalResponse)
async def get_approval(approval_id: str):
    """Obter aprovação por ID."""
    approval = ApprovalRequest.get_by_id(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Aprovação não encontrada")
    
    import json
    return ApprovalResponse(
        id=approval.id,
        workflow_id=approval.workflow_id,
        status=approval.status.value,
        responses=approval.responses,
        created_at=approval.created_at.isoformat(),
        comments=approval.comments
    )
```

### 4. Integrar Endpoints no FastAPI

#### Atualizar `src/api/main.py`:
```python
from src.api.routes.approvals import router as approvals_router

app.include_router(approvals_router)
```

### 5. Implementar Notificações para Aprovação Pendente

#### Criar `src/utils/notifications.py`:
```python
"""Sistema de notificações."""
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Serviço de notificações."""
    
    @staticmethod
    def notify_approval_pending(approval_id: str, workflow_id: str):
        """Notificar que há aprovação pendente."""
        # TODO: Implementar notificação (email, webhook, etc.)
        logger.info(f"Aprovação pendente: {approval_id} para workflow {workflow_id}")
        # Por enquanto, apenas log
```

### 6. Implementar Histórico de Aprovações

#### Adicionar endpoint:
```python
@router.get("/history/{workflow_id}", response_model=List[ApprovalResponse])
async def get_approval_history(workflow_id: str):
    """Obter histórico de aprovações de um workflow."""
    # Implementar busca no banco
    pass
```

### 7. Atualizar Workflow com Node de Aprovação

#### Atualizar `src/workflows/workflow.py`:
```python
from src.workflows.hitl_node import hitl_approval_node, check_approval_status

def _build_graph(self) -> StateGraph:
    # ... código existente ...
    
    # Adicionar node de aprovação
    workflow.add_node("approval", hitl_approval_node)
    
    # Adicionar edge após verifier
    workflow.add_edge("verifier", "approval")
    
    # Adicionar conditional edge para verificar aprovação
    workflow.add_conditional_edges(
        "approval",
        check_approval_status,
        {
            "continue": "exit",
            "reject": "exit",  # TODO: Adicionar node de reprocessamento
            "wait": "approval"  # Aguardar aprovação
        }
    )
```

### 8. Adicionar Métricas

#### Atualizar `src/utils/metrics.py`:
```python
# Métricas de HITL
hitl_approvals_total = Counter(
    'hitl_approvals_total',
    'Total de aprovações',
    ['status']  # pending, approved, rejected
)

hitl_approval_duration_seconds = Histogram(
    'hitl_approval_duration_seconds',
    'Tempo de espera por aprovação em segundos'
)
```

### 9. Criar Testes

#### Criar `tests/integration/test_hitl.py`:
```python
"""Testes de integração HITL."""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_get_pending_approvals():
    """Testar obtenção de aprovações pendentes."""
    response = client.get("/approvals/pending")
    assert response.status_code == 200

def test_approve():
    """Testar aprovação."""
    # Criar aprovação de teste primeiro
    pass
```

---

## Checklist de Validação

- [ ] Checkpoint no workflow que pausa para aprovação implementado
- [ ] Modelo de dados para aprovações criado
- [ ] API endpoints para aprovação implementados
- [ ] Notificações para aprovação pendente implementadas
- [ ] Histórico de aprovações implementado
- [ ] Fluxo completo de HITL testado
- [ ] Métricas adicionadas
- [ ] Documentação da API criada

---

## Comandos de Teste

```bash
# Testar endpoints de aprovação
python -m pytest tests/integration/test_hitl.py

# Testar workflow com HITL
python -m pytest tests/integration/test_workflow_hitl.py
```


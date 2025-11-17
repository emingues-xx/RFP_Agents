"""Modelos de dados para aprovações."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from enum import Enum
import uuid
import json
import logging

from src.config.settings import get_settings
from src.workflows.state import WorkflowState

logger = logging.getLogger(__name__)
Base = declarative_base()
settings = get_settings()


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
    workflow_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=False, index=True)
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING, index=True)
    responses = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_by = Column(String, nullable=True)
    comments = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<ApprovalRequestModel(id={self.id}, status={self.status}, workflow_id={self.workflow_id})>"


class ApprovalRequest(BaseModel):
    """Modelo Pydantic para aprovações."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    session_id: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    responses: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    comments: Optional[str] = None
    
    @classmethod
    def create_from_state(cls, state: WorkflowState) -> "ApprovalRequest":
        """Criar a partir do estado do workflow.
        
        Args:
            state: Estado do workflow
        
        Returns:
            Instância de ApprovalRequest
        """
        # Converter verified_responses para formato serializável
        verified_responses = state.get("verified_responses", [])
        responses_data = []
        
        for resp in verified_responses:
            if isinstance(resp, dict):
                responses_data.append(resp)
            else:
                # Se for um objeto Pydantic, converter para dict
                responses_data.append(resp.model_dump() if hasattr(resp, 'model_dump') else resp.dict())
        
        return cls(
            workflow_id=state.get("workflow_id", "unknown"),
            session_id=state.get("session_id", "unknown"),
            responses=responses_data
        )
    
    def save(self) -> str:
        """Salvar no banco de dados.
        
        Returns:
            ID da aprovação salva
        """
        from sqlalchemy import create_engine
        
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Criar tabela se não existir
            Base.metadata.create_all(engine)
            
            # Verificar se já existe
            existing = session.query(ApprovalRequestModel).filter_by(id=self.id).first()
            if existing:
                # Atualizar
                existing.workflow_id = self.workflow_id
                existing.session_id = self.session_id
                existing.status = self.status.value
                existing.responses = json.dumps(self.responses, ensure_ascii=False)
                existing.updated_at = datetime.utcnow()
                existing.approved_by = self.approved_by
                existing.comments = self.comments
            else:
                # Criar novo
                db_model = ApprovalRequestModel(
                    id=self.id,
                    workflow_id=self.workflow_id,
                    session_id=self.session_id,
                    status=self.status.value,
                    responses=json.dumps(self.responses, ensure_ascii=False),
                    created_at=self.created_at,
                    approved_by=self.approved_by,
                    comments=self.comments
                )
                session.add(db_model)
            
            session.commit()
            logger.info(f"Aprovação salva: {self.id} (status: {self.status.value})")
            return self.id
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao salvar aprovação: {e}")
            raise
        finally:
            session.close()
    
    @classmethod
    def get_by_id(cls, approval_id: str) -> Optional["ApprovalRequest"]:
        """Obter por ID.
        
        Args:
            approval_id: ID da aprovação
        
        Returns:
            Instância de ApprovalRequest ou None
        """
        from sqlalchemy import create_engine
        
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            db_model = session.query(ApprovalRequestModel).filter_by(id=approval_id).first()
            if not db_model:
                return None
            
            # Converter status
            try:
                status = ApprovalStatus(db_model.status)
            except ValueError:
                status = ApprovalStatus.PENDING
            
            # Parsear responses
            try:
                responses = json.loads(db_model.responses) if db_model.responses else []
            except json.JSONDecodeError:
                logger.warning(f"Erro ao parsear responses da aprovação {approval_id}")
                responses = []
            
            return cls(
                id=db_model.id,
                workflow_id=db_model.workflow_id,
                session_id=db_model.session_id,
                status=status,
                responses=responses,
                created_at=db_model.created_at,
                updated_at=db_model.updated_at,
                approved_by=db_model.approved_by,
                comments=db_model.comments
            )
        except Exception as e:
            logger.error(f"Erro ao obter aprovação {approval_id}: {e}")
            return None
        finally:
            session.close()
    
    @classmethod
    def get_by_workflow_id(cls, workflow_id: str) -> List["ApprovalRequest"]:
        """Obter todas as aprovações de um workflow.
        
        Args:
            workflow_id: ID do workflow
        
        Returns:
            Lista de ApprovalRequest
        """
        from sqlalchemy import create_engine
        
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            db_models = session.query(ApprovalRequestModel).filter_by(
                workflow_id=workflow_id
            ).order_by(ApprovalRequestModel.created_at.desc()).all()
            
            approvals = []
            for db_model in db_models:
                try:
                    status = ApprovalStatus(db_model.status)
                except ValueError:
                    status = ApprovalStatus.PENDING
                
                try:
                    responses = json.loads(db_model.responses) if db_model.responses else []
                except json.JSONDecodeError:
                    responses = []
                
                approvals.append(cls(
                    id=db_model.id,
                    workflow_id=db_model.workflow_id,
                    session_id=db_model.session_id,
                    status=status,
                    responses=responses,
                    created_at=db_model.created_at,
                    updated_at=db_model.updated_at,
                    approved_by=db_model.approved_by,
                    comments=db_model.comments
                ))
            
            return approvals
        except Exception as e:
            logger.error(f"Erro ao obter aprovações do workflow {workflow_id}: {e}")
            return []
        finally:
            session.close()


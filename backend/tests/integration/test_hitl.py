"""Testes de integração HITL."""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.models.approval import ApprovalRequest, ApprovalStatus, ApprovalRequestModel
from src.workflows.state import WorkflowState
from unittest.mock import patch, MagicMock
import json

client = TestClient(app)


@pytest.fixture
def sample_workflow_state():
    """Fixture com estado de workflow de exemplo."""
    return {
        "workflow_id": "test-workflow-123",
        "session_id": "test-session-123",
        "verified_responses": [
            {
                "qid": "Q001",
                "response_text": "Resposta de teste",
                "confidence_score": 0.9,
                "needs_review": False
            }
        ]
    }


def test_get_pending_approvals():
    """Testar obtenção de aprovações pendentes."""
    response = client.get("/approvals/pending")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_approval_from_state(sample_workflow_state):
    """Testar criação de aprovação a partir do estado."""
    approval = ApprovalRequest.create_from_state(sample_workflow_state)
    
    assert approval.workflow_id == "test-workflow-123"
    assert approval.session_id == "test-session-123"
    assert len(approval.responses) == 1
    assert approval.status == ApprovalStatus.PENDING


def test_approval_save_and_get(sample_workflow_state):
    """Testar salvar e recuperar aprovação."""
    # Criar aprovação
    approval = ApprovalRequest.create_from_state(sample_workflow_state)
    approval_id = approval.save()
    
    assert approval_id is not None
    
    # Recuperar
    retrieved = ApprovalRequest.get_by_id(approval_id)
    assert retrieved is not None
    assert retrieved.id == approval_id
    assert retrieved.workflow_id == approval.workflow_id


def test_approve_endpoint(sample_workflow_state):
    """Testar endpoint de aprovação."""
    # Criar aprovação
    approval = ApprovalRequest.create_from_state(sample_workflow_state)
    approval_id = approval.save()
    
    # Aprovar
    response = client.post(
        f"/approvals/{approval_id}/approve",
        json={"comments": "Aprovado para teste", "approved_by": "test_user"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["approval_id"] == approval_id
    
    # Verificar que foi atualizado
    updated = ApprovalRequest.get_by_id(approval_id)
    assert updated.status == ApprovalStatus.APPROVED
    assert updated.comments == "Aprovado para teste"


def test_reject_endpoint(sample_workflow_state):
    """Testar endpoint de rejeição."""
    # Criar aprovação
    approval = ApprovalRequest.create_from_state(sample_workflow_state)
    approval_id = approval.save()
    
    # Rejeitar
    response = client.post(
        f"/approvals/{approval_id}/reject",
        json={"comments": "Rejeitado para teste"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"
    
    # Verificar que foi atualizado
    updated = ApprovalRequest.get_by_id(approval_id)
    assert updated.status == ApprovalStatus.REJECTED


def test_edit_endpoint(sample_workflow_state):
    """Testar endpoint de edição."""
    # Criar aprovação
    approval = ApprovalRequest.create_from_state(sample_workflow_state)
    approval_id = approval.save()
    
    # Editar
    edited_responses = [
        {
            "qid": "Q001",
            "response_text": "Resposta editada",
            "confidence_score": 0.95
        }
    ]
    
    response = client.put(
        f"/approvals/{approval_id}/edit",
        json={"responses": edited_responses, "comments": "Editado para teste"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "edited"
    
    # Verificar que foi atualizado
    updated = ApprovalRequest.get_by_id(approval_id)
    assert updated.status == ApprovalStatus.EDITED
    assert len(updated.responses) == 1
    assert updated.responses[0]["response_text"] == "Resposta editada"


def test_get_approval_by_id(sample_workflow_state):
    """Testar obtenção de aprovação por ID."""
    # Criar aprovação
    approval = ApprovalRequest.create_from_state(sample_workflow_state)
    approval_id = approval.save()
    
    # Obter via API
    response = client.get(f"/approvals/{approval_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == approval_id
    assert data["workflow_id"] == approval.workflow_id


def test_get_approval_not_found():
    """Testar obtenção de aprovação inexistente."""
    response = client.get("/approvals/nonexistent-id")
    assert response.status_code == 404


def test_approve_already_processed(sample_workflow_state):
    """Testar aprovação já processada."""
    # Criar e aprovar
    approval = ApprovalRequest.create_from_state(sample_workflow_state)
    approval_id = approval.save()
    
    client.post(f"/approvals/{approval_id}/approve", json={})
    
    # Tentar aprovar novamente
    response = client.post(f"/approvals/{approval_id}/approve", json={})
    assert response.status_code == 400
    assert "já processada" in response.json()["detail"].lower()


def test_get_approval_history(sample_workflow_state):
    """Testar obtenção de histórico de aprovações."""
    workflow_id = sample_workflow_state["workflow_id"]
    
    # Criar múltiplas aprovações
    approval1 = ApprovalRequest.create_from_state(sample_workflow_state)
    approval1.save()
    
    state2 = sample_workflow_state.copy()
    state2["session_id"] = "test-session-456"
    approval2 = ApprovalRequest.create_from_state(state2)
    approval2.save()
    
    # Obter histórico
    response = client.get(f"/approvals/history/{workflow_id}")
    
    assert response.status_code == 200
    history = response.json()
    assert len(history) >= 2


def test_hitl_approval_node(sample_workflow_state):
    """Testar node de aprovação HITL."""
    from src.workflows.hitl_node import hitl_approval_node
    
    state: WorkflowState = {
        **sample_workflow_state,
        "requires_approval": False,
        "approval_status": None,
        "approval_id": None,
        "current_step": "verifier"
    }
    
    result = hitl_approval_node(state)
    
    assert result["requires_approval"] is True
    assert result["approval_status"] == "pending"
    assert result["approval_id"] is not None
    assert result["current_step"] == "awaiting_approval"


def test_check_approval_status_pending(sample_workflow_state):
    """Testar verificação de status pendente."""
    from src.workflows.hitl_node import check_approval_status
    
    approval = ApprovalRequest.create_from_state(sample_workflow_state)
    approval_id = approval.save()
    
    state: WorkflowState = {
        "approval_id": approval_id,
        "approval_status": "pending"
    }
    
    result = check_approval_status(state)
    assert result == "wait"


def test_check_approval_status_approved(sample_workflow_state):
    """Testar verificação de status aprovado."""
    from src.workflows.hitl_node import check_approval_status
    
    approval = ApprovalRequest.create_from_state(sample_workflow_state)
    approval_id = approval.save()
    approval.status = ApprovalStatus.APPROVED
    approval.save()
    
    state: WorkflowState = {
        "approval_id": approval_id,
        "approval_status": "approved"
    }
    
    result = check_approval_status(state)
    assert result == "continue"


def test_check_approval_status_rejected(sample_workflow_state):
    """Testar verificação de status rejeitado."""
    from src.workflows.hitl_node import check_approval_status
    
    approval = ApprovalRequest.create_from_state(sample_workflow_state)
    approval_id = approval.save()
    approval.status = ApprovalStatus.REJECTED
    approval.save()
    
    state: WorkflowState = {
        "approval_id": approval_id,
        "approval_status": "rejected"
    }
    
    result = check_approval_status(state)
    assert result == "reject"


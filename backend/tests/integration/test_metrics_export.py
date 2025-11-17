"""Testes de exportação de métricas."""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.utils.metrics import (
    agent_executions_total,
    llm_calls_total,
    http_requests_total,
    parser_extractions_total,
    knowledge_queries_total,
    verifier_validations_total,
    hitl_approvals_total,
    verifier_confidence_scores
)

client = TestClient(app)


def test_metrics_endpoint():
    """Testar endpoint de métricas."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text or "promhttp" in response.text


def test_metrics_format():
    """Testar formato das métricas."""
    response = client.get("/metrics")
    content = response.text
    
    # Verificar formato Prometheus
    assert "# TYPE" in content or "# HELP" in content
    
    # Verificar que é texto plano
    assert response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"


def test_metrics_http_present():
    """Testar se métricas HTTP estão presentes."""
    # Gerar algumas métricas
    http_requests_total.labels(method="GET", endpoint="/test", status="200").inc()
    
    response = client.get("/metrics")
    content = response.text
    
    assert "http_requests_total" in content


def test_metrics_agents_present():
    """Testar se métricas de agentes estão presentes."""
    # Gerar algumas métricas
    agent_executions_total.labels(agent_name="test", status="success").inc()
    
    response = client.get("/metrics")
    content = response.text
    
    assert "agent_executions_total" in content


def test_metrics_llm_present():
    """Testar se métricas de LLM estão presentes."""
    # Gerar algumas métricas
    llm_calls_total.labels(provider="openai", model="gpt-4", status="success").inc()
    
    response = client.get("/metrics")
    content = response.text
    
    assert "llm_calls_total" in content


def test_metrics_parser_present():
    """Testar se métricas de Parser estão presentes."""
    # Gerar algumas métricas
    parser_extractions_total.labels(file_type="pdf", status="success").inc()
    
    response = client.get("/metrics")
    content = response.text
    
    assert "parser_extractions_total" in content


def test_metrics_knowledge_present():
    """Testar se métricas de Knowledge estão presentes."""
    # Gerar algumas métricas
    knowledge_queries_total.labels(category="technical", status="success").inc()
    
    response = client.get("/metrics")
    content = response.text
    
    assert "knowledge_queries_total" in content


def test_metrics_verifier_present():
    """Testar se métricas de Verifier estão presentes."""
    # Gerar algumas métricas
    verifier_validations_total.labels(status="success").inc()
    verifier_confidence_scores.observe(0.85)
    
    response = client.get("/metrics")
    content = response.text
    
    assert "verifier_validations_total" in content
    assert "verifier_confidence_scores" in content


def test_metrics_hitl_present():
    """Testar se métricas de HITL estão presentes."""
    # Gerar algumas métricas
    hitl_approvals_total.labels(status="pending").inc()
    
    response = client.get("/metrics")
    content = response.text
    
    assert "hitl_approvals_total" in content


def test_metrics_all_custom_metrics():
    """Testar se todas as métricas customizadas estão presentes."""
    from src.utils.metrics import (
        parser_extraction_duration_seconds,
        parser_questions_normalized_total,
        knowledge_retrieval_duration_seconds,
        knowledge_retrieval_quality,
        knowledge_response_quality,
        verifier_detections_total,
        rag_queries_total,
        rag_retrieval_duration_seconds,
        rag_documents_retrieved,
        hitl_approval_duration_seconds
    )
    
    # Gerar métricas de exemplo
    parser_extraction_duration_seconds.labels(file_type="pdf").observe(1.2)
    parser_questions_normalized_total.labels(category="technical").inc()
    knowledge_retrieval_duration_seconds.observe(0.15)
    knowledge_retrieval_quality.observe(0.85)
    knowledge_response_quality.observe(0.90)
    verifier_detections_total.labels(type="prohibited_terms").inc()
    rag_queries_total.labels(status="success").inc()
    rag_retrieval_duration_seconds.observe(0.1)
    rag_documents_retrieved.observe(5)
    hitl_approval_duration_seconds.observe(30.0)
    
    response = client.get("/metrics")
    content = response.text
    
    # Verificar que todas as métricas estão presentes
    assert "parser_extraction_duration_seconds" in content
    assert "parser_questions_normalized_total" in content
    assert "knowledge_retrieval_duration_seconds" in content
    assert "knowledge_retrieval_quality" in content
    assert "knowledge_response_quality" in content
    assert "verifier_detections_total" in content
    assert "rag_queries_total" in content
    assert "rag_retrieval_duration_seconds" in content
    assert "rag_documents_retrieved" in content
    assert "hitl_approval_duration_seconds" in content


def test_metrics_labels():
    """Testar se labels estão sendo aplicados corretamente."""
    # Gerar métricas com diferentes labels
    agent_executions_total.labels(agent_name="orchestrator", status="success").inc()
    agent_executions_total.labels(agent_name="parser", status="success").inc()
    agent_executions_total.labels(agent_name="knowledge", status="error").inc()
    
    response = client.get("/metrics")
    content = response.text
    
    # Verificar que métricas com labels diferentes estão presentes
    assert "agent_executions_total" in content
    # Verificar que contém os labels
    assert "agent_name" in content or "orchestrator" in content or "parser" in content


def test_metrics_histogram_buckets():
    """Testar se histogramas têm buckets corretos."""
    from src.utils.metrics import agent_execution_duration_seconds
    
    # Observar valores em diferentes buckets
    agent_execution_duration_seconds.labels(agent_name="test").observe(0.5)
    agent_execution_duration_seconds.labels(agent_name="test").observe(1.0)
    agent_execution_duration_seconds.labels(agent_name="test").observe(5.0)
    
    response = client.get("/metrics")
    content = response.text
    
    # Verificar que histograma está presente
    assert "agent_execution_duration_seconds" in content
    # Verificar que buckets estão presentes
    assert "_bucket" in content or "le=" in content


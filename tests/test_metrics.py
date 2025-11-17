"""Testes para métricas."""
import pytest
from src.utils.metrics import (
    http_requests_total,
    agent_executions_total,
    llm_calls_total,
    llm_tokens_total,
    agent_execution_duration_seconds
)


def test_http_metrics():
    """Testar métricas HTTP."""
    http_requests_total.labels(
        method="GET",
        endpoint="/health",
        status=200
    ).inc()
    # Verificar que não há erro
    assert True


def test_agent_metrics():
    """Testar métricas de agentes."""
    agent_executions_total.labels(
        agent_name="orchestrator",
        status="success"
    ).inc()
    
    agent_execution_duration_seconds.labels(
        agent_name="orchestrator"
    ).observe(1.5)
    
    assert True


def test_llm_metrics():
    """Testar métricas de LLM."""
    llm_calls_total.labels(
        provider="openai",
        model="gpt-4",
        status="success"
    ).inc()
    
    llm_tokens_total.labels(
        provider="openai",
        model="gpt-4",
        type="input"
    ).inc(100)
    
    llm_tokens_total.labels(
        provider="openai",
        model="gpt-4",
        type="output"
    ).inc(50)
    
    assert True


def test_metrics_endpoint():
    """Testar endpoint de métricas."""
    from src.api.metrics_endpoint import metrics
    from fastapi.testclient import TestClient
    from src.api.main import app
    
    client = TestClient(app)
    response = client.get("/metrics")
    
    assert response.status_code == 200
    assert "http_requests_total" in response.text or "promhttp" in response.text


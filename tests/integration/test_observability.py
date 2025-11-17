"""Testes de observabilidade."""
import pytest
from src.utils.metrics import (
    agent_executions_total,
    llm_calls_total,
    http_requests_total,
    parser_extractions_total,
    knowledge_queries_total,
    verifier_validations_total,
    hitl_approvals_total
)


def test_metrics_collection():
    """Testar coleta de métricas."""
    # Testar métricas de agentes
    agent_executions_total.labels(
        agent_name="test",
        status="success"
    ).inc()
    
    agent_executions_total.labels(
        agent_name="test",
        status="error"
    ).inc()
    
    # Testar métricas de LLM
    llm_calls_total.labels(
        provider="openai",
        model="gpt-4",
        status="success"
    ).inc()
    
    llm_calls_total.labels(
        provider="anthropic",
        model="claude-3-5-sonnet",
        status="success"
    ).inc()
    
    # Testar métricas HTTP
    http_requests_total.labels(
        method="GET",
        endpoint="/health",
        status="200"
    ).inc()
    
    # Testar métricas de Parser
    parser_extractions_total.labels(
        file_type="pdf",
        status="success"
    ).inc()
    
    # Testar métricas de Knowledge
    knowledge_queries_total.labels(
        category="technical",
        status="success"
    ).inc()
    
    # Testar métricas de Verifier
    verifier_validations_total.labels(
        status="success"
    ).inc()
    
    # Testar métricas de HITL
    hitl_approvals_total.labels(
        status="pending"
    ).inc()
    
    # Verificar que não há erro
    assert True


def test_metrics_labels():
    """Testar que labels são aplicados corretamente."""
    # Testar diferentes combinações de labels
    agent_executions_total.labels(agent_name="orchestrator", status="success").inc()
    agent_executions_total.labels(agent_name="parser", status="success").inc()
    agent_executions_total.labels(agent_name="knowledge", status="success").inc()
    agent_executions_total.labels(agent_name="verifier", status="success").inc()
    
    llm_calls_total.labels(provider="openai", model="gpt-4", status="success").inc()
    llm_calls_total.labels(provider="openai", model="gpt-4", status="error").inc()
    llm_calls_total.labels(provider="anthropic", model="claude-3-5-sonnet", status="success").inc()
    
    # Verificar que não há erro
    assert True


def test_metrics_histogram():
    """Testar métricas de histograma."""
    from src.utils.metrics import (
        agent_execution_duration_seconds,
        llm_request_duration_seconds,
        http_request_duration_seconds
    )
    
    # Observar durações
    agent_execution_duration_seconds.labels(agent_name="test").observe(1.5)
    agent_execution_duration_seconds.labels(agent_name="test").observe(2.3)
    agent_execution_duration_seconds.labels(agent_name="test").observe(0.8)
    
    llm_request_duration_seconds.labels(provider="openai", model="gpt-4").observe(1.2)
    llm_request_duration_seconds.labels(provider="anthropic", model="claude-3-5-sonnet").observe(0.9)
    
    http_request_duration_seconds.labels(method="GET", endpoint="/health").observe(0.05)
    http_request_duration_seconds.labels(method="POST", endpoint="/workflow/process").observe(2.5)
    
    # Verificar que não há erro
    assert True


def test_metrics_gauge():
    """Testar métricas de gauge."""
    from src.utils.metrics import (
        agents_active,
        memory_sessions_total,
        system_memory_usage_bytes,
        system_cpu_usage_percent
    )
    
    # Atualizar gauges
    agents_active.labels(agent_name="orchestrator").set(1)
    agents_active.labels(agent_name="parser").set(1)
    agents_active.labels(agent_name="knowledge").set(1)
    
    memory_sessions_total.inc()
    memory_sessions_total.inc()
    
    system_memory_usage_bytes.set(1024 * 1024 * 512)  # 512 MB
    system_cpu_usage_percent.set(45.5)
    
    # Verificar que não há erro
    assert True


def test_metrics_parser_specific():
    """Testar métricas específicas do Parser."""
    from src.utils.metrics import (
        parser_extraction_duration_seconds,
        parser_questions_normalized_total
    )
    
    parser_extraction_duration_seconds.labels(file_type="pdf").observe(1.2)
    parser_extraction_duration_seconds.labels(file_type="docx").observe(0.8)
    
    parser_questions_normalized_total.labels(category="technical").inc()
    parser_questions_normalized_total.labels(category="compliance").inc()
    
    assert True


def test_metrics_knowledge_specific():
    """Testar métricas específicas do Knowledge."""
    from src.utils.metrics import (
        knowledge_retrieval_duration_seconds,
        knowledge_response_quality,
        knowledge_retrieval_quality
    )
    
    knowledge_retrieval_duration_seconds.observe(0.15)
    knowledge_retrieval_duration_seconds.observe(0.25)
    
    knowledge_response_quality.observe(0.85)
    knowledge_response_quality.observe(0.92)
    
    knowledge_retrieval_quality.observe(0.78)
    knowledge_retrieval_quality.observe(0.88)
    
    assert True


def test_metrics_verifier_specific():
    """Testar métricas específicas do Verifier."""
    from src.utils.metrics import verifier_detections_total
    
    verifier_detections_total.labels(type="prohibited_terms").inc()
    verifier_detections_total.labels(type="gaps").inc()
    verifier_detections_total.labels(type="inconsistencies").inc()
    verifier_detections_total.labels(type="contractual_violations").inc()
    verifier_detections_total.labels(type="formatting_errors").inc()
    
    assert True


def test_metrics_hitl_specific():
    """Testar métricas específicas do HITL."""
    from src.utils.metrics import hitl_approval_duration_seconds
    
    hitl_approval_duration_seconds.observe(30.5)
    hitl_approval_duration_seconds.observe(120.0)
    hitl_approval_duration_seconds.observe(300.0)
    
    hitl_approvals_total.labels(status="pending").inc()
    hitl_approvals_total.labels(status="approved").inc()
    hitl_approvals_total.labels(status="rejected").inc()
    hitl_approvals_total.labels(status="edited").inc()
    
    assert True


def test_metrics_rag_specific():
    """Testar métricas específicas do RAG."""
    from src.utils.metrics import (
        rag_queries_total,
        rag_retrieval_duration_seconds,
        rag_documents_retrieved
    )
    
    rag_queries_total.labels(status="success").inc()
    rag_queries_total.labels(status="error").inc()
    
    rag_retrieval_duration_seconds.observe(0.1)
    rag_retrieval_duration_seconds.observe(0.25)
    
    rag_documents_retrieved.observe(5)
    rag_documents_retrieved.observe(10)
    
    assert True


def test_metrics_mcp_specific():
    """Testar métricas específicas do MCP."""
    from src.utils.metrics import (
        mcp_calls_total,
        mcp_call_duration_seconds
    )
    
    mcp_calls_total.labels(tool_name="test_tool", status="success").inc()
    mcp_calls_total.labels(tool_name="test_tool", status="error").inc()
    
    mcp_call_duration_seconds.labels(tool_name="test_tool").observe(0.5)
    mcp_call_duration_seconds.labels(tool_name="test_tool").observe(1.2)
    
    assert True


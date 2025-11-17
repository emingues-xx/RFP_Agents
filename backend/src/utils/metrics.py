"""Métricas Prometheus para a aplicação."""
from prometheus_client import Counter, Histogram, Gauge, start_http_server, REGISTRY
import logging
import os

logger = logging.getLogger(__name__)

# Métricas de requisições HTTP
http_requests_total = Counter(
    'http_requests_total',
    'Total de requisições HTTP',
    ['method', 'endpoint', 'status']
)

# Métricas de latência HTTP
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'Duração das requisições HTTP em segundos',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# Métricas de agentes
agent_executions_total = Counter(
    'agent_executions_total',
    'Total de execuções de agentes',
    ['agent_name', 'status']
)

agent_execution_duration_seconds = Histogram(
    'agent_execution_duration_seconds',
    'Duração de execução dos agentes em segundos',
    ['agent_name'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0)
)

agents_active = Gauge(
    'agents_active',
    'Número de agentes ativos',
    ['agent_name']
)

# Métricas de LLM
llm_calls_total = Counter(
    'llm_calls_total',
    'Total de chamadas LLM',
    ['provider', 'model', 'status']
)

llm_tokens_total = Counter(
    'llm_tokens_total',
    'Total de tokens usados',
    ['provider', 'model', 'type']  # type: input/output
)

llm_cost_usd = Counter(
    'llm_cost_usd',
    'Custo total em USD',
    ['provider', 'model']
)

llm_request_duration_seconds = Histogram(
    'llm_request_duration_seconds',
    'Duração de chamadas LLM em segundos',
    ['provider', 'model'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
)

# Métricas de RAG
rag_queries_total = Counter(
    'rag_queries_total',
    'Total de queries RAG',
    ['status']
)

rag_retrieval_duration_seconds = Histogram(
    'rag_retrieval_duration_seconds',
    'Duração de retrieval RAG em segundos',
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

rag_documents_retrieved = Histogram(
    'rag_documents_retrieved',
    'Número de documentos recuperados por query RAG',
    buckets=(1, 5, 10, 20, 50, 100)
)

# Métricas de Parser
parser_extractions_total = Counter(
    'parser_extractions_total',
    'Total de extrações de documentos',
    ['file_type', 'status']
)

parser_extraction_duration_seconds = Histogram(
    'parser_extraction_duration_seconds',
    'Duração de extração em segundos',
    ['file_type'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
)

parser_questions_normalized_total = Counter(
    'parser_questions_normalized_total',
    'Total de perguntas normalizadas',
    ['category']
)

# Métricas de Knowledge
knowledge_queries_total = Counter(
    'knowledge_queries_total',
    'Total de queries de conhecimento',
    ['category', 'status']
)

knowledge_retrieval_duration_seconds = Histogram(
    'knowledge_retrieval_duration_seconds',
    'Duração de retrieval em segundos',
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

knowledge_response_quality = Histogram(
    'knowledge_response_quality',
    'Score de qualidade das respostas',
    buckets=(0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0)
)

# Métrica adicional de qualidade de retrieval (similarity score)
knowledge_retrieval_quality = Histogram(
    'knowledge_retrieval_quality',
    'Qualidade de retrieval (similarity score)',
    buckets=(0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0)
)

# Métricas de Verifier
verifier_validations_total = Counter(
    'verifier_validations_total',
    'Total de validações',
    ['status']
)

verifier_detections_total = Counter(
    'verifier_detections_total',
    'Total de problemas detectados',
    ['type']  # prohibited_terms, gaps, inconsistencies, contractual_violations, formatting_errors
)

verifier_confidence_scores = Histogram(
    'verifier_confidence_scores',
    'Scores de confiança das validações',
    buckets=(0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0)
)

# Métricas de Tools
tool_usage_total = Counter(
    'tool_usage_total',
    'Total de uso de tools',
    ['tool_name', 'status']
)

# Métricas de MCP
mcp_calls_total = Counter(
    'mcp_calls_total',
    'Total de chamadas MCP',
    ['tool_name', 'status']
)

mcp_call_duration_seconds = Histogram(
    'mcp_call_duration_seconds',
    'Duração de chamadas MCP em segundos',
    ['tool_name'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
)

# Métricas de Memória
memory_sessions_total = Gauge(
    'memory_sessions_total',
    'Total de sessões ativas na memória'
)

memory_messages_total = Counter(
    'memory_messages_total',
    'Total de mensagens salvas na memória'
)

# Métricas de HITL
hitl_approvals_total = Counter(
    'hitl_approvals_total',
    'Total de aprovações',
    ['status']  # pending, approved, rejected, edited
)

hitl_approval_duration_seconds = Histogram(
    'hitl_approval_duration_seconds',
    'Tempo de espera por aprovação em segundos',
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0, 3600.0)
)

# Métricas de sistema
system_memory_usage_bytes = Gauge(
    'system_memory_usage_bytes',
    'Uso de memória do sistema em bytes'
)

system_cpu_usage_percent = Gauge(
    'system_cpu_usage_percent',
    'Uso de CPU do sistema em percentual'
)


def start_metrics_server(port: int = 9090) -> None:
    """Iniciar servidor de métricas."""
    try:
        start_http_server(port, registry=REGISTRY)
        logger.info(f"Servidor de métricas iniciado na porta {port}")
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor de métricas: {e}")


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


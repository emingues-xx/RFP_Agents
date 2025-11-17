# Tarefa 1.6: Setup do Prometheus e Grafana

## Objetivo
Configurar Prometheus para coleta de métricas e Grafana para visualização.

## Prioridade
Alta

## Estimativa
2 dias

## Responsável
DevOps/Backend

---

## Instruções de Implementação

### 1. Configurar Prometheus no docker-compose

#### Já incluído na Tarefa 1.2, verificar configuração:
```yaml
prometheus:
  image: prom/prometheus:latest
  container_name: rfp-agents-prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./docker/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
```

### 2. Criar prometheus.yml

#### Criar `docker/prometheus/prometheus.yml`:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'rfp-agents'
    environment: 'development'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets: []

# Load rules
rule_files:
  # - "alerts.yml"

# Scrape configurations
scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Application metrics
  - job_name: 'app'
    static_configs:
      - targets: ['app:9090']
    metrics_path: '/metrics'
    scrape_interval: 10s

  # PostgreSQL exporter (opcional)
  # - job_name: 'postgres'
  #   static_configs:
  #     - targets: ['postgres-exporter:9187']

  # Redis exporter (opcional)
  # - job_name: 'redis'
  #   static_configs:
  #     - targets: ['redis-exporter:9121']
```

### 3. Integrar Prometheus Client na Aplicação Python

#### Criar `src/utils/metrics.py`:
```python
"""Métricas Prometheus para a aplicação."""
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from prometheus_client.core import CollectorRegistry
import logging

logger = logging.getLogger(__name__)

# Registry global
registry = CollectorRegistry()

# Métricas de requisições
http_requests_total = Counter(
    'http_requests_total',
    'Total de requisições HTTP',
    ['method', 'endpoint', 'status'],
    registry=registry
)

# Métricas de latência
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'Duração das requisições HTTP em segundos',
    ['method', 'endpoint'],
    registry=registry
)

# Métricas de agentes
agent_executions_total = Counter(
    'agent_executions_total',
    'Total de execuções de agentes',
    ['agent_name', 'status'],
    registry=registry
)

agent_execution_duration_seconds = Histogram(
    'agent_execution_duration_seconds',
    'Duração de execução dos agentes em segundos',
    ['agent_name'],
    registry=registry
)

agents_active = Gauge(
    'agents_active',
    'Número de agentes ativos',
    ['agent_name'],
    registry=registry
)

# Métricas de LLM
llm_calls_total = Counter(
    'llm_calls_total',
    'Total de chamadas LLM',
    ['provider', 'model', 'status'],
    registry=registry
)

llm_tokens_total = Counter(
    'llm_tokens_total',
    'Total de tokens usados',
    ['provider', 'model', 'type'],  # type: input/output
    registry=registry
)

llm_cost_usd = Counter(
    'llm_cost_usd',
    'Custo total em USD',
    ['provider', 'model'],
    registry=registry
)

# Métricas de RAG
rag_queries_total = Counter(
    'rag_queries_total',
    'Total de queries RAG',
    ['status'],
    registry=registry
)

rag_retrieval_duration_seconds = Histogram(
    'rag_retrieval_duration_seconds',
    'Duração de retrieval RAG em segundos',
    registry=registry
)


def start_metrics_server(port: int = 9090) -> None:
    """Iniciar servidor de métricas."""
    try:
        start_http_server(port, registry=registry)
        logger.info(f"Servidor de métricas iniciado na porta {port}")
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor de métricas: {e}")
```

### 4. Criar Métricas Customizadas Iniciais

#### Criar `src/api/metrics_endpoint.py`:
```python
"""Endpoint de métricas para Prometheus."""
from fastapi import APIRouter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

router = APIRouter()


@router.get("/metrics")
async def metrics():
    """Endpoint de métricas Prometheus."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

#### Integrar no FastAPI (`src/api/main.py`):
```python
from src.api.metrics_endpoint import router as metrics_router

app = FastAPI()
app.include_router(metrics_router)
```

### 5. Adicionar Middleware para Métricas HTTP

#### Criar `src/api/middleware/metrics_middleware.py`:
```python
"""Middleware para coletar métricas HTTP."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from src.utils.metrics import (
    http_requests_total,
    http_request_duration_seconds
)
import time
import logging

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware para métricas HTTP."""
    
    async def dispatch(self, request: Request, call_next):
        """Processar requisição e coletar métricas."""
        start_time = time.time()
        
        # Processar requisição
        response = await call_next(request)
        
        # Calcular duração
        duration = time.time() - start_time
        
        # Coletar métricas
        method = request.method
        endpoint = request.url.path
        status = response.status_code
        
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        return response
```

#### Adicionar ao FastAPI:
```python
from src.api.middleware.metrics_middleware import MetricsMiddleware

app.add_middleware(MetricsMiddleware)
```

### 6. Configurar Grafana no docker-compose

#### Verificar configuração (já na Tarefa 1.2):
```yaml
grafana:
  image: grafana/grafana:latest
  container_name: rfp-agents-grafana
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

### 7. Configurar Datasource do Prometheus no Grafana

#### Criar `docker/grafana/provisioning/datasources/prometheus.yml`:
```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      timeInterval: "15s"
```

### 8. Criar Dashboard Básico no Grafana

#### Criar `docker/grafana/provisioning/dashboards/dashboard.yml`:
```yaml
apiVersion: 1

providers:
  - name: 'Default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
```

#### Criar `docker/grafana/dashboards/app-metrics.json`:
```json
{
  "dashboard": {
    "title": "RFP Agents - Application Metrics",
    "panels": [
      {
        "title": "HTTP Requests Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "HTTP Request Duration",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p95"
          }
        ]
      },
      {
        "title": "Agent Executions",
        "targets": [
          {
            "expr": "rate(agent_executions_total[5m])",
            "legendFormat": "{{agent_name}}"
          }
        ]
      },
      {
        "title": "LLM Calls",
        "targets": [
          {
            "expr": "rate(llm_calls_total[5m])",
            "legendFormat": "{{provider}} {{model}}"
          }
        ]
      }
    ]
  }
}
```

### 9. Iniciar Servidor de Métricas na Aplicação

#### Atualizar `src/api/main.py`:
```python
from src.utils.metrics import start_metrics_server
import os

# Iniciar servidor de métricas
metrics_port = int(os.getenv("PROMETHEUS_PORT", "9090"))
start_metrics_server(metrics_port)
```

### 10. Testar Coleta e Visualização de Métricas

#### Criar `tests/test_metrics.py`:
```python
"""Testes para métricas."""
import pytest
from src.utils.metrics import (
    http_requests_total,
    agent_executions_total,
    llm_calls_total
)


def test_http_metrics():
    """Testar métricas HTTP."""
    http_requests_total.labels(
        method="GET",
        endpoint="/health",
        status=200
    ).inc()
    # Verificar que não há erro


def test_agent_metrics():
    """Testar métricas de agentes."""
    agent_executions_total.labels(
        agent_name="orchestrator",
        status="success"
    ).inc()


def test_llm_metrics():
    """Testar métricas de LLM."""
    llm_calls_total.labels(
        provider="openai",
        model="gpt-4",
        status="success"
    ).inc()
```

---

## Checklist de Validação

- [ ] Prometheus configurado no docker-compose
- [ ] prometheus.yml criado e configurado
- [ ] Prometheus client integrado na aplicação
- [ ] Métricas customizadas criadas
- [ ] Endpoint /metrics funcionando
- [ ] Middleware de métricas HTTP funcionando
- [ ] Grafana configurado
- [ ] Datasource do Prometheus configurado
- [ ] Dashboard básico criado
- [ ] Servidor de métricas iniciando automaticamente
- [ ] Testes criados
- [ ] Documentação atualizada

---

## Comandos de Teste

```bash
# Subir Prometheus e Grafana
docker-compose up -d prometheus grafana

# Verificar métricas
curl http://localhost:9090/metrics

# Verificar endpoint da aplicação
curl http://localhost:8000/metrics

# Acessar Prometheus
# http://localhost:9090

# Acessar Grafana
# http://localhost:3001 (admin/admin)

# Testar query no Prometheus
# rate(http_requests_total[5m])
```

---

## Próximos Passos
Após completar esta tarefa, seguir para: **Tarefa 1.7: Setup de Banco de Dados e Vector Store**


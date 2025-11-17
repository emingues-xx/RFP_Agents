# Tarefa 5.3: Observabilidade Completa

## Objetivo
Finalizar integração de observabilidade com Langfuse, Prometheus e Grafana, incluindo dashboards e alertas.

## Prioridade
Alta

## Estimativa
3 dias

## Responsável
Backend/DevOps

---

## Instruções de Implementação

### 1. Finalizar Integração Langfuse

#### Verificar se todas as chamadas LLM estão rastreadas:
```python
# Verificar em src/utils/llm_factory.py
# Verificar em src/utils/langfuse_wrapper.py
# Todas as chamadas devem ter session_id
```

#### Adicionar rastreamento de agentes:
```python
from langfuse.decorators import observe

@observe(name="orchestrator_agent")
def identify_input_type(self, input_text: str):
    # Método já rastreado
    pass
```

### 2. Finalizar Integração Prometheus

#### Verificar métricas customizadas em `src/utils/metrics.py`:
```python
# Já implementado:
# - agent_executions_total
# - agent_execution_duration_seconds
# - llm_calls_total
# - llm_tokens_total
# - etc.
```

#### Adicionar métricas de agentes específicos:
```python
# Métricas de Parser
parser_extractions_total = Counter(
    'parser_extractions_total',
    'Total de extrações',
    ['file_type', 'status']
)

# Métricas de Knowledge
knowledge_retrieval_quality = Histogram(
    'knowledge_retrieval_quality',
    'Qualidade de retrieval (similarity score)',
    buckets=(0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0)
)

# Métricas de Verifier
verifier_detections_total = Counter(
    'verifier_detections_total',
    'Total de problemas detectados',
    ['type']  # prohibited_terms, gaps, inconsistencies
)
```

### 3. Criar Dashboards no Grafana

#### Dashboard de Sistema (`docker/grafana/dashboards/system-metrics.json`):
```json
{
  "dashboard": {
    "title": "System Metrics",
    "panels": [
      {
        "title": "CPU Usage",
        "targets": [{
          "expr": "rate(process_cpu_seconds_total[5m]) * 100",
          "legendFormat": "CPU %"
        }]
      },
      {
        "title": "Memory Usage",
        "targets": [{
          "expr": "process_resident_memory_bytes",
          "legendFormat": "Memory"
        }]
      }
    ]
  }
}
```

#### Dashboard de Aplicação (`docker/grafana/dashboards/application-metrics.json`):
```json
{
  "dashboard": {
    "title": "Application Metrics",
    "panels": [
      {
        "title": "HTTP Request Rate",
        "targets": [{
          "expr": "rate(http_requests_total[5m])",
          "legendFormat": "{{method}} {{endpoint}}"
        }]
      },
      {
        "title": "HTTP Request Duration (p95)",
        "targets": [{
          "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
          "legendFormat": "p95"
        }]
      }
    ]
  }
}
```

#### Dashboard de Agentes (`docker/grafana/dashboards/agents-metrics.json`):
```json
{
  "dashboard": {
    "title": "Agents Performance",
    "panels": [
      {
        "title": "Agent Executions Rate",
        "targets": [{
          "expr": "rate(agent_executions_total[5m])",
          "legendFormat": "{{agent_name}} - {{status}}"
        }]
      },
      {
        "title": "Agent Execution Duration",
        "targets": [{
          "expr": "histogram_quantile(0.95, rate(agent_execution_duration_seconds_bucket[5m]))",
          "legendFormat": "{{agent_name}} p95"
        }]
      },
      {
        "title": "Active Agents",
        "targets": [{
          "expr": "agents_active",
          "legendFormat": "{{agent_name}}"
        }]
      }
    ]
  }
}
```

#### Dashboard de LLMs (`docker/grafana/dashboards/llm-metrics.json`):
```json
{
  "dashboard": {
    "title": "LLM Metrics",
    "panels": [
      {
        "title": "LLM Calls Rate",
        "targets": [{
          "expr": "rate(llm_calls_total[5m])",
          "legendFormat": "{{provider}} {{model}} - {{status}}"
        }]
      },
      {
        "title": "LLM Tokens Usage",
        "targets": [{
          "expr": "rate(llm_tokens_total[5m])",
          "legendFormat": "{{provider}} {{model}} - {{type}}"
        }]
      },
      {
        "title": "LLM Cost (USD)",
        "targets": [{
          "expr": "rate(llm_cost_usd[5m])",
          "legendFormat": "{{provider}} {{model}}"
        }]
      },
      {
        "title": "LLM Request Duration",
        "targets": [{
          "expr": "histogram_quantile(0.95, rate(llm_request_duration_seconds_bucket[5m]))",
          "legendFormat": "{{provider}} {{model}} p95"
        }]
      }
    ]
  }
}
```

### 4. Configurar Alertas

#### Criar `docker/prometheus/alerts.yml`:
```yaml
groups:
  - name: rfp_agents_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Alta taxa de erros HTTP"
          description: "Taxa de erros acima de 10% por 5 minutos"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Latência alta detectada"
          description: "p95 de latência acima de 5 segundos"

      - alert: HighLLMCost
        expr: rate(llm_cost_usd[1h]) > 10
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Custo alto de LLM"
          description: "Custo de LLM acima de $10/hora"

      - alert: AgentFailure
        expr: rate(agent_executions_total{status="error"}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Falha em agentes"
          description: "Taxa de falha de agentes acima de 10%"
```

#### Atualizar `docker/prometheus/prometheus.yml`:
```yaml
rule_files:
  - "alerts.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
```

### 5. Testar Observabilidade Completa

#### Criar `tests/integration/test_observability.py`:
```python
"""Testes de observabilidade."""
import pytest
from src.utils.metrics import (
    agent_executions_total,
    llm_calls_total
)

def test_metrics_collection():
    """Testar coleta de métricas."""
    agent_executions_total.labels(
        agent_name="test",
        status="success"
    ).inc()
    
    llm_calls_total.labels(
        provider="openai",
        model="gpt-4",
        status="success"
    ).inc()
    
    # Verificar que não há erro
    assert True
```

---

## Checklist de Validação

- [ ] Integração Langfuse finalizada
- [ ] Todas as chamadas LLM rastreadas
- [ ] Métricas de prompts e respostas capturadas
- [ ] Métricas de tokens e custos funcionando
- [ ] Integração Prometheus finalizada
- [ ] Métricas customizadas dos agentes exportadas
- [ ] Métricas de tempo de execução por agente funcionando
- [ ] Métricas de número de chamadas funcionando
- [ ] Métricas de taxa de sucesso/falha funcionando
- [ ] Dashboard de sistema criado
- [ ] Dashboard de aplicação criado
- [ ] Dashboard de agentes criado
- [ ] Dashboard de LLMs criado
- [ ] Alertas configurados
- [ ] Testes de observabilidade passando
- [ ] Documentação de dashboards e alertas criada

---

## Comandos de Teste

```bash
# Verificar métricas
curl http://localhost:8000/metrics

# Verificar Prometheus
curl http://localhost:9090/api/v1/query?query=http_requests_total

# Acessar Grafana
# http://localhost:3001

# Acessar Langfuse
# http://localhost:3020
```


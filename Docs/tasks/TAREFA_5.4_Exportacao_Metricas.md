# Tarefa 5.4: Exportação de Métricas Customizadas

## Objetivo
Definir e exportar métricas customizadas dos agentes para Prometheus.

## Prioridade
Média

## Estimativa
2 dias

## Responsável
Backend

---

## Instruções de Implementação

### 1. Definir Métricas Customizadas dos Agentes

#### Atualizar `src/utils/metrics.py` com todas as métricas:
```python
# Métricas de Parser
parser_extractions_total = Counter(
    'parser_extractions_total',
    'Total de extrações de documentos',
    ['file_type', 'status']
)

parser_extraction_duration_seconds = Histogram(
    'parser_extraction_duration_seconds',
    'Duração de extração em segundos',
    ['file_type']
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
    'Duração de retrieval em segundos'
)

knowledge_retrieval_quality = Histogram(
    'knowledge_retrieval_quality',
    'Qualidade de retrieval (similarity score)',
    buckets=(0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0)
)

knowledge_response_quality = Histogram(
    'knowledge_response_quality',
    'Score de qualidade das respostas',
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
    ['type']  # prohibited_terms, gaps, inconsistencies
)

verifier_confidence_scores = Histogram(
    'verifier_confidence_scores',
    'Scores de confiança das validações',
    buckets=(0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0)
)

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

# Métricas de RAG
rag_queries_total = Counter(
    'rag_queries_total',
    'Total de queries RAG',
    ['status']
)

rag_retrieval_duration_seconds = Histogram(
    'rag_retrieval_duration_seconds',
    'Duração de retrieval RAG em segundos'
)

rag_documents_retrieved = Histogram(
    'rag_documents_retrieved',
    'Número de documentos recuperados por query RAG',
    buckets=(1, 5, 10, 20, 50, 100)
)
```

### 2. Implementar Exportação para Prometheus

#### Verificar se endpoint `/metrics` já está funcionando:
```python
# Já implementado em src/api/metrics_endpoint.py
# Verificar se todas as métricas estão sendo expostas
```

### 3. Criar Labels Apropriados para Métricas

#### Garantir labels consistentes:
```python
# Usar labels padronizados:
# - agent_name: nome do agente
# - status: success, error
# - file_type: pdf, docx, xlsx, csv
# - category: técnico, segurança, compliance, jurídico
# - provider: openai, anthropic
# - model: gpt-4, claude-3, etc.
```

### 4. Testar Coleta de Métricas

#### Criar `tests/integration/test_metrics_export.py`:
```python
"""Testes de exportação de métricas."""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

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
```

### 5. Validar Visualização no Grafana

#### Criar queries de exemplo:
```promql
# Taxa de execuções por agente
rate(agent_executions_total[5m])

# Duração p95 por agente
histogram_quantile(0.95, rate(agent_execution_duration_seconds_bucket[5m]))

# Taxa de sucesso por agente
rate(agent_executions_total{status="success"}[5m]) / rate(agent_executions_total[5m])
```

### 6. Documentar Métricas Disponíveis

#### Criar `docs/metrics/available_metrics.md`:
```markdown
# Métricas Disponíveis

## HTTP
- `http_requests_total`: Total de requisições HTTP
- `http_request_duration_seconds`: Duração das requisições

## Agentes
- `agent_executions_total`: Total de execuções de agentes
- `agent_execution_duration_seconds`: Duração de execução
- `agents_active`: Número de agentes ativos

## Parser
- `parser_extractions_total`: Total de extrações
- `parser_extraction_duration_seconds`: Duração de extração
- `parser_questions_normalized_total`: Total de perguntas normalizadas

## Knowledge
- `knowledge_queries_total`: Total de queries
- `knowledge_retrieval_duration_seconds`: Duração de retrieval
- `knowledge_retrieval_quality`: Qualidade de retrieval
- `knowledge_response_quality`: Qualidade de respostas

## Verifier
- `verifier_validations_total`: Total de validações
- `verifier_detections_total`: Total de problemas detectados
- `verifier_confidence_scores`: Scores de confiança

## LLM
- `llm_calls_total`: Total de chamadas LLM
- `llm_tokens_total`: Total de tokens
- `llm_cost_usd`: Custo em USD
- `llm_request_duration_seconds`: Duração de chamadas

## RAG
- `rag_queries_total`: Total de queries RAG
- `rag_retrieval_duration_seconds`: Duração de retrieval
- `rag_documents_retrieved`: Documentos recuperados

## HITL
- `hitl_approvals_total`: Total de aprovações
- `hitl_approval_duration_seconds`: Tempo de espera por aprovação
```

---

## Checklist de Validação

- [ ] Métricas customizadas definidas
- [ ] Tempo de execução por agente implementado
- [ ] Número de chamadas por agente implementado
- [ ] Taxa de sucesso/falha por agente implementado
- [ ] Qualidade de respostas (score médio) implementado
- [ ] Exportação para Prometheus funcionando
- [ ] Labels apropriados criados
- [ ] Testes de coleta de métricas passando
- [ ] Visualização no Grafana validada
- [ ] Documentação de métricas criada

---

## Comandos de Teste

```bash
# Verificar métricas
curl http://localhost:8000/metrics | grep agent_executions_total

# Testar queries Prometheus
curl 'http://localhost:9090/api/v1/query?query=rate(agent_executions_total[5m])'

# Verificar no Grafana
# Acessar http://localhost:3001 e criar dashboard
```


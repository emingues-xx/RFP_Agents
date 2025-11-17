# Métricas Disponíveis

Este documento lista todas as métricas Prometheus disponíveis no sistema RFP Agents.

## HTTP

### `http_requests_total`
**Tipo**: Counter  
**Labels**: `method`, `endpoint`, `status`  
**Descrição**: Total de requisições HTTP recebidas pela aplicação.

**Exemplo de query**:
```promql
rate(http_requests_total[5m])
```

### `http_request_duration_seconds`
**Tipo**: Histogram  
**Labels**: `method`, `endpoint`  
**Descrição**: Duração das requisições HTTP em segundos.

**Buckets**: 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0

**Exemplo de query**:
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

---

## Agentes

### `agent_executions_total`
**Tipo**: Counter  
**Labels**: `agent_name`, `status`  
**Descrição**: Total de execuções de agentes.

**Valores de `agent_name`**: `orchestrator`, `parser`, `knowledge`, `verifier`, `workflow`  
**Valores de `status`**: `success`, `error`

**Exemplo de query**:
```promql
rate(agent_executions_total[5m])
```

### `agent_execution_duration_seconds`
**Tipo**: Histogram  
**Labels**: `agent_name`  
**Descrição**: Duração de execução dos agentes em segundos.

**Buckets**: 0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0

**Exemplo de query**:
```promql
histogram_quantile(0.95, rate(agent_execution_duration_seconds_bucket[5m]))
```

### `agents_active`
**Tipo**: Gauge  
**Labels**: `agent_name`  
**Descrição**: Número de agentes ativos no momento.

**Exemplo de query**:
```promql
agents_active
```

---

## Parser

### `parser_extractions_total`
**Tipo**: Counter  
**Labels**: `file_type`, `status`  
**Descrição**: Total de extrações de documentos realizadas pelo Parser.

**Valores de `file_type`**: `pdf`, `docx`, `excel`, `csv`  
**Valores de `status`**: `success`, `error`

**Exemplo de query**:
```promql
rate(parser_extractions_total[5m])
```

### `parser_extraction_duration_seconds`
**Tipo**: Histogram  
**Labels**: `file_type`  
**Descrição**: Duração de extração de documentos em segundos.

**Buckets**: 0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0

**Exemplo de query**:
```promql
histogram_quantile(0.95, rate(parser_extraction_duration_seconds_bucket[5m]))
```

### `parser_questions_normalized_total`
**Tipo**: Counter  
**Labels**: `category`  
**Descrição**: Total de perguntas normalizadas pelo Parser.

**Valores de `category`**: `technical`, `security`, `compliance`, `legal`, `general`

**Exemplo de query**:
```promql
rate(parser_questions_normalized_total[5m])
```

---

## Knowledge

### `knowledge_queries_total`
**Tipo**: Counter  
**Labels**: `category`, `status`  
**Descrição**: Total de queries de conhecimento realizadas.

**Valores de `category`**: `technical`, `security`, `compliance`, `legal`, `general`, `unknown`  
**Valores de `status`**: `success`, `error`

**Exemplo de query**:
```promql
rate(knowledge_queries_total[5m])
```

### `knowledge_retrieval_duration_seconds`
**Tipo**: Histogram  
**Descrição**: Duração de retrieval de documentos em segundos.

**Buckets**: 0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0

**Exemplo de query**:
```promql
histogram_quantile(0.95, rate(knowledge_retrieval_duration_seconds_bucket[5m]))
```

### `knowledge_retrieval_quality`
**Tipo**: Histogram  
**Descrição**: Qualidade de retrieval (similarity score) dos documentos recuperados.

**Buckets**: 0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0

**Exemplo de query**:
```promql
histogram_quantile(0.50, rate(knowledge_retrieval_quality_bucket[5m]))
```

### `knowledge_response_quality`
**Tipo**: Histogram  
**Descrição**: Score de qualidade das respostas geradas pelo Knowledge Agent.

**Buckets**: 0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0

**Exemplo de query**:
```promql
histogram_quantile(0.50, rate(knowledge_response_quality_bucket[5m]))
```

---

## Verifier

### `verifier_validations_total`
**Tipo**: Counter  
**Labels**: `status`  
**Descrição**: Total de validações realizadas pelo Verifier.

**Valores de `status`**: `success`, `error`

**Exemplo de query**:
```promql
rate(verifier_validations_total[5m])
```

### `verifier_detections_total`
**Tipo**: Counter  
**Labels**: `type`  
**Descrição**: Total de problemas detectados pelo Verifier.

**Valores de `type`**: `prohibited_terms`, `gaps`, `inconsistencies`, `contractual_violations`, `formatting_errors`

**Exemplo de query**:
```promql
rate(verifier_detections_total[5m])
```

### `verifier_confidence_scores`
**Tipo**: Histogram  
**Descrição**: Scores de confiança das validações realizadas pelo Verifier.

**Buckets**: 0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0

**Exemplo de query**:
```promql
histogram_quantile(0.50, rate(verifier_confidence_scores_bucket[5m]))
```

---

## LLM

### `llm_calls_total`
**Tipo**: Counter  
**Labels**: `provider`, `model`, `status`  
**Descrição**: Total de chamadas LLM realizadas.

**Valores de `provider`**: `openai`, `anthropic`  
**Valores de `model`**: `gpt-4`, `gpt-3.5-turbo`, `claude-3-5-sonnet`, etc.  
**Valores de `status`**: `success`, `error`

**Exemplo de query**:
```promql
rate(llm_calls_total[5m])
```

### `llm_tokens_total`
**Tipo**: Counter  
**Labels**: `provider`, `model`, `type`  
**Descrição**: Total de tokens usados nas chamadas LLM.

**Valores de `type`**: `input`, `output`

**Exemplo de query**:
```promql
rate(llm_tokens_total[5m])
```

### `llm_cost_usd`
**Tipo**: Counter  
**Labels**: `provider`, `model`  
**Descrição**: Custo total em USD das chamadas LLM.

**Exemplo de query**:
```promql
rate(llm_cost_usd[1h])
```

### `llm_request_duration_seconds`
**Tipo**: Histogram  
**Labels**: `provider`, `model`  
**Descrição**: Duração de chamadas LLM em segundos.

**Buckets**: 0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0

**Exemplo de query**:
```promql
histogram_quantile(0.95, rate(llm_request_duration_seconds_bucket[5m]))
```

---

## RAG

### `rag_queries_total`
**Tipo**: Counter  
**Labels**: `status`  
**Descrição**: Total de queries RAG realizadas.

**Valores de `status`**: `success`, `error`

**Exemplo de query**:
```promql
rate(rag_queries_total[5m])
```

### `rag_retrieval_duration_seconds`
**Tipo**: Histogram  
**Descrição**: Duração de retrieval RAG em segundos.

**Buckets**: 0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0

**Exemplo de query**:
```promql
histogram_quantile(0.95, rate(rag_retrieval_duration_seconds_bucket[5m]))
```

### `rag_documents_retrieved`
**Tipo**: Histogram  
**Descrição**: Número de documentos recuperados por query RAG.

**Buckets**: 1, 5, 10, 20, 50, 100

**Exemplo de query**:
```promql
histogram_quantile(0.50, rate(rag_documents_retrieved_bucket[5m]))
```

---

## HITL (Human-In-The-Loop)

### `hitl_approvals_total`
**Tipo**: Counter  
**Labels**: `status`  
**Descrição**: Total de aprovações HITL.

**Valores de `status`**: `pending`, `approved`, `rejected`, `edited`

**Exemplo de query**:
```promql
rate(hitl_approvals_total[5m])
```

### `hitl_approval_duration_seconds`
**Tipo**: Histogram  
**Descrição**: Tempo de espera por aprovação em segundos.

**Buckets**: 1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0, 3600.0

**Exemplo de query**:
```promql
histogram_quantile(0.95, rate(hitl_approval_duration_seconds_bucket[1h]))
```

---

## Tools

### `tool_usage_total`
**Tipo**: Counter  
**Labels**: `tool_name`, `status`  
**Descrição**: Total de uso de tools customizadas.

**Valores de `status`**: `success`, `error`

**Exemplo de query**:
```promql
rate(tool_usage_total[5m])
```

---

## MCP (Model Context Protocol)

### `mcp_calls_total`
**Tipo**: Counter  
**Labels**: `tool_name`, `status`  
**Descrição**: Total de chamadas MCP realizadas.

**Valores de `status`**: `success`, `error`

**Exemplo de query**:
```promql
rate(mcp_calls_total[5m])
```

### `mcp_call_duration_seconds`
**Tipo**: Histogram  
**Labels**: `tool_name`  
**Descrição**: Duração de chamadas MCP em segundos.

**Buckets**: 0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0

**Exemplo de query**:
```promql
histogram_quantile(0.95, rate(mcp_call_duration_seconds_bucket[5m]))
```

---

## Memória

### `memory_sessions_total`
**Tipo**: Gauge  
**Descrição**: Total de sessões ativas na memória persistente.

**Exemplo de query**:
```promql
memory_sessions_total
```

### `memory_messages_total`
**Tipo**: Counter  
**Descrição**: Total de mensagens salvas na memória persistente.

**Exemplo de query**:
```promql
rate(memory_messages_total[5m])
```

---

## Sistema

### `system_memory_usage_bytes`
**Tipo**: Gauge  
**Descrição**: Uso de memória do sistema em bytes.

**Exemplo de query**:
```promql
system_memory_usage_bytes / (1024 * 1024 * 1024)  # Converter para GB
```

### `system_cpu_usage_percent`
**Tipo**: Gauge  
**Descrição**: Uso de CPU do sistema em percentual.

**Exemplo de query**:
```promql
system_cpu_usage_percent
```

---

## Queries Úteis

### Taxa de Sucesso por Agente
```promql
rate(agent_executions_total{status="success"}[5m]) / rate(agent_executions_total[5m])
```

### Taxa de Erro HTTP
```promql
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])
```

### Custo Total de LLM (última hora)
```promql
sum(increase(llm_cost_usd[1h]))
```

### Tempo Médio de Aprovação HITL
```promql
histogram_quantile(0.50, rate(hitl_approval_duration_seconds_bucket[1h]))
```

### Qualidade Média de Respostas
```promql
histogram_quantile(0.50, rate(knowledge_response_quality_bucket[5m]))
```

---

## Acesso às Métricas

### Endpoint HTTP
```
GET http://localhost:8000/metrics
```

### Prometheus
```
http://localhost:9090
```

### Grafana
```
http://localhost:3001
```

---

## Convenções de Labels

- **`agent_name`**: Nome do agente (`orchestrator`, `parser`, `knowledge`, `verifier`, `workflow`)
- **`status`**: Status da operação (`success`, `error`)
- **`file_type`**: Tipo de arquivo (`pdf`, `docx`, `excel`, `csv`)
- **`category`**: Categoria do conteúdo (`technical`, `security`, `compliance`, `legal`, `general`)
- **`provider`**: Provedor LLM (`openai`, `anthropic`)
- **`model`**: Modelo LLM (`gpt-4`, `gpt-3.5-turbo`, `claude-3-5-sonnet`)
- **`type`**: Tipo de detecção ou token (`prohibited_terms`, `gaps`, `inconsistencies`, `input`, `output`)
- **`method`**: Método HTTP (`GET`, `POST`, `PUT`, `DELETE`)
- **`endpoint`**: Endpoint HTTP (`/workflow/process`, `/approvals`, etc.)
- **`tool_name`**: Nome da tool ou MCP tool utilizada


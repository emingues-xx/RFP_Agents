# Alertas Prometheus

Este documento descreve os alertas configurados no Prometheus para o sistema RFP Agents.

## Configuração

Os alertas estão definidos em `docker/prometheus/alerts.yml` e são carregados automaticamente pelo Prometheus.

## Alertas Configurados

### 1. HighErrorRate

**Severidade**: Critical  
**Componente**: HTTP

**Condição**: Taxa de erros HTTP acima de 10% por 5 minutos

**Expressão**:
```promql
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.1
```

**Ação**: Investigar logs de erro e status de saúde dos serviços

---

### 2. HighLatency

**Severidade**: Warning  
**Componente**: HTTP

**Condição**: p95 de latência HTTP acima de 5 segundos por 5 minutos

**Expressão**:
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 5
```

**Ação**: Verificar performance do backend e otimizar queries/processamento

---

### 3. HighLLMCost

**Severidade**: Warning  
**Componente**: LLM

**Condição**: Custo de LLM acima de $10/hora por 1 hora

**Expressão**:
```promql
sum(rate(llm_cost_usd[1h])) > 10
```

**Ação**: Revisar uso de LLM e considerar otimizações ou limites de rate

---

### 4. AgentFailure

**Severidade**: Critical  
**Componente**: Agents

**Condição**: Taxa de falha de agentes acima de 10% por 5 minutos

**Expressão**:
```promql
rate(agent_executions_total{status="error"}[5m]) / rate(agent_executions_total[5m]) > 0.1
```

**Ação**: Investigar logs dos agentes e verificar dependências (LLM, banco de dados, etc.)

---

### 5. HighLLMErrorRate

**Severidade**: Warning  
**Componente**: LLM

**Condição**: Taxa de erros LLM acima de 5% por 5 minutos

**Expressão**:
```promql
rate(llm_calls_total{status="error"}[5m]) / rate(llm_calls_total[5m]) > 0.05
```

**Ação**: Verificar status dos providers LLM (OpenAI, Anthropic) e chaves de API

---

### 6. HighMemoryUsage

**Severidade**: Warning  
**Componente**: System

**Condição**: Uso de memória acima de 8GB por 10 minutos

**Expressão**:
```promql
(system_memory_usage_bytes / (1024 * 1024 * 1024)) > 8
```

**Ação**: Verificar vazamentos de memória e otimizar uso de recursos

---

### 7. HighCPUUsage

**Severidade**: Warning  
**Componente**: System

**Condição**: Uso de CPU acima de 80% por 10 minutos

**Expressão**:
```promql
system_cpu_usage_percent > 80
```

**Ação**: Verificar processos que consomem CPU e otimizar código

---

### 8. NoAgentExecutions

**Severidade**: Warning  
**Componente**: Agents

**Condição**: Nenhuma execução de agente detectada nos últimos 15 minutos

**Expressão**:
```promql
rate(agent_executions_total[5m]) == 0
```

**Ação**: Verificar se o sistema está recebendo requisições e se os agentes estão funcionando

---

### 9. HighHITLPendingTime

**Severidade**: Warning  
**Componente**: HITL

**Condição**: p95 de tempo de aprovação pendente acima de 1 hora por 1 hora

**Expressão**:
```promql
histogram_quantile(0.95, rate(hitl_approval_duration_seconds_bucket[1h])) > 3600
```

**Ação**: Notificar usuários sobre aprovações pendentes e verificar se há bloqueios

## Configuração de Alertmanager

Para receber notificações dos alertas, configure o Alertmanager:

1. **Editar `docker/prometheus/prometheus.yml`**:
```yaml
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
```

2. **Configurar Alertmanager** (opcional):
   - Email
   - Slack
   - PagerDuty
   - Webhook

## Visualização de Alertas

### No Prometheus

1. Acessar: http://localhost:9090
2. Menu "Alerts"
3. Ver status de todos os alertas

### No Grafana

1. Acessar: http://localhost:3001
2. Menu "Alerting"
3. Ver alertas configurados

## Teste de Alertas

Para testar um alerta:

1. **Simular condição**: Gerar tráfego de erro ou alta latência
2. **Verificar no Prometheus**: http://localhost:9090/alerts
3. **Verificar notificações**: Se Alertmanager configurado

## Ajuste de Thresholds

Para ajustar thresholds dos alertas:

1. Editar `docker/prometheus/alerts.yml`
2. Modificar valores nas expressões (ex: `> 0.1` para `> 0.2`)
3. Reiniciar Prometheus:
```bash
docker-compose restart prometheus
```

## Boas Práticas

1. **Thresholds Realistas**: Ajustar baseado em baseline do sistema
2. **Períodos Adequados**: Usar `for` apropriado para evitar falsos positivos
3. **Severidades Corretas**: Usar `critical` apenas para problemas graves
4. **Anotações Claras**: Descrever problema e ação recomendada
5. **Testes Regulares**: Testar alertas periodicamente


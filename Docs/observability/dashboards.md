# Dashboards Grafana

Este documento descreve os dashboards disponíveis no Grafana para monitoramento do sistema RFP Agents.

## Acesso

- **URL**: http://localhost:3001
- **Usuário padrão**: admin
- **Senha padrão**: admin (alterar no primeiro login)

## Dashboards Disponíveis

### 1. System Metrics

**UID**: `rfp-agents-system-metrics`

Monitora métricas do sistema:

- **CPU Usage**: Uso de CPU do processo e sistema
- **Memory Usage**: Uso de memória do processo e sistema
- **System CPU Usage**: Uso de CPU do sistema

**Métricas utilizadas**:
- `process_cpu_seconds_total`
- `process_resident_memory_bytes`
- `system_memory_usage_bytes`
- `system_cpu_usage_percent`

### 2. Application Metrics

**UID**: `rfp-agents-application-metrics`

Monitora métricas da aplicação HTTP:

- **HTTP Request Rate**: Taxa de requisições HTTP por método, endpoint e status
- **HTTP Request Duration (p95/p50)**: Latência p95 e p50 das requisições HTTP
- **HTTP Error Rate**: Taxa de erros HTTP (status 5xx)
- **HTTP Requests by Status**: Total de requisições agrupadas por status

**Métricas utilizadas**:
- `http_requests_total`
- `http_request_duration_seconds`

### 3. Agents Performance

**UID**: `rfp-agents-agents-metrics`

Monitora performance dos agentes:

- **Agent Executions Rate**: Taxa de execuções por agente e status
- **Agent Execution Duration (p95/p50)**: Duração p95 e p50 de execução por agente
- **Active Agents**: Número de agentes ativos
- **Agent Error Rate**: Taxa de erros por agente
- **Parser Extractions Rate**: Taxa de extrações do Parser por tipo de arquivo
- **Verifier Detections Rate**: Taxa de detecções do Verifier por tipo de problema

**Métricas utilizadas**:
- `agent_executions_total`
- `agent_execution_duration_seconds`
- `agents_active`
- `parser_extractions_total`
- `verifier_detections_total`

### 4. LLM Metrics

**UID**: `rfp-agents-llm-metrics`

Monitora métricas de uso de LLMs:

- **LLM Calls Rate**: Taxa de chamadas LLM por provider, modelo e status
- **LLM Request Duration (p95/p50)**: Latência p95 e p50 das chamadas LLM
- **LLM Tokens Usage Rate**: Taxa de uso de tokens por provider, modelo e tipo (input/output)
- **LLM Cost (USD/hour)**: Custo por hora de uso de LLM por provider e modelo
- **LLM Error Rate**: Taxa de erros nas chamadas LLM
- **LLM Calls (Last Hour)**: Total de chamadas na última hora por provider, modelo e status

**Métricas utilizadas**:
- `llm_calls_total`
- `llm_request_duration_seconds`
- `llm_tokens_total`
- `llm_cost_usd`

## Como Usar

1. **Acessar Grafana**: http://localhost:3001
2. **Fazer login** com credenciais padrão
3. **Navegar para Dashboards**: Menu lateral > Dashboards
4. **Selecionar dashboard** desejado
5. **Ajustar período**: Usar seletor de tempo no canto superior direito

## Personalização

Os dashboards podem ser editados diretamente no Grafana:

1. Abrir o dashboard
2. Clicar em "Dashboard settings" (ícone de engrenagem)
3. Selecionar "JSON Model"
4. Editar e salvar

## Exportação

Para exportar um dashboard:

1. Abrir o dashboard
2. Clicar em "Share" (ícone de compartilhar)
3. Selecionar "Export"
4. Baixar JSON

## Importação

Para importar um dashboard:

1. Menu lateral > Dashboards
2. Clicar em "Import"
3. Colar JSON ou fazer upload do arquivo
4. Configurar datasource (Prometheus)
5. Salvar


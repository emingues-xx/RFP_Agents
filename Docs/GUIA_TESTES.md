# Guia de Testes - RFP Agents

Este documento fornece um roteiro completo para testar todas as funcionalidades do sistema RFP Agents.

## 📋 Pré-requisitos

Antes de começar, certifique-se de que:

- [ ] Docker e Docker Compose estão instalados e rodando
- [ ] Todos os serviços estão up: `docker-compose ps`
- [ ] Arquivo `.env` está configurado com as chaves necessárias
- [ ] Portas 3021 (frontend) e 3022 (API) estão disponíveis

## 🚀 Início Rápido

### 1. Subir os Serviços

```bash
# Subir todos os serviços
docker-compose up -d

# Aguardar inicialização (30-60 segundos)
sleep 30

# Verificar status
docker-compose ps
```

### 2. Verificar Saúde dos Serviços

```bash
# API
curl http://localhost:3022/health
# Esperado: {"status":"healthy"}

# Frontend
curl http://localhost:3021
# Esperado: HTML da aplicação

# PostgreSQL
docker-compose exec postgres psql -U postgres -d rfp_agents -c "SELECT 1;"
# Esperado: 1

# Redis
docker-compose exec redis redis-cli --no-auth-warning -a redis_password ping
# Esperado: PONG

# Worker
docker logs rfp-agents-worker | tail -20
# Esperado: "Worker iniciado. Escutando fila: rfp-queue"
```

---

## 🧪 Roteiro de Testes

### Fase 1: Testes de Infraestrutura

#### 1.1 Verificar Migrações do Banco

```bash
# Verificar se migrações rodaram
docker-compose logs app | grep -i migration

# Verificar versão atual do Alembic
docker-compose exec app alembic current

# Ver histórico de migrações
docker-compose exec app alembic history
```

**✅ Critério de Sucesso:** Migrações executadas sem erros

---

#### 1.2 Verificar Métricas Prometheus

```bash
# Verificar endpoint de métricas
curl http://localhost:3022/metrics | head -20

# Verificar métricas específicas
curl http://localhost:3022/metrics | grep "http_requests_total"
curl http://localhost:3022/metrics | grep "queue_jobs_total"
```

**✅ Critério de Sucesso:** Métricas sendo expostas corretamente

---

#### 1.3 Verificar Worker RQ

```bash
# Ver logs do worker
docker logs rfp-agents-worker

# Verificar conexão com Redis
docker-compose exec redis redis-cli --no-auth-warning -a redis_password
> KEYS rq:*
> EXIT
```

**✅ Critério de Sucesso:** Worker conectado e escutando a fila

---

### Fase 2: Testes da API

#### 2.1 Health Check

```bash
curl http://localhost:3022/health
```

**✅ Esperado:**
```json
{"status":"healthy"}
```

---

#### 2.2 Documentação da API

```bash
# Abrir no navegador
# http://localhost:3022/docs
```

**✅ Critério de Sucesso:** Swagger UI carrega e mostra todos os endpoints

---

#### 2.3 Listar RFPs

```bash
curl http://localhost:3022/rfps
```

**✅ Esperado:** Lista de RFPs (pode estar vazia inicialmente)

---

#### 2.4 Informações da Fila

```bash
curl http://localhost:3022/rfps/queue/info
```

**✅ Esperado:**
```json
{
  "name": "rfp-queue",
  "count": 0,
  "started_jobs": 0,
  "finished_jobs": 0,
  "failed_jobs": 0,
  "deferred_jobs": 0,
  "scheduled_jobs": 0
}
```

---

### Fase 3: Testes do Queue System

#### 3.1 Enfileirar RFP

```bash
curl -X POST http://localhost:3022/rfps/queue \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Qual é a capacidade máxima de processamento do sistema?",
    "session_id": "test-session-001"
  }'
```

**✅ Esperado:**
```json
{
  "job_id": "abc123...",
  "session_id": "test-session-001",
  "status": "queued",
  "message": "RFP enfileirado com sucesso"
}
```

**📝 Anotar o `job_id` para próximos testes**

---

#### 3.2 Verificar Status do Job

```bash
# Substituir {job_id} pelo ID retornado anteriormente
curl http://localhost:3022/rfps/queue/{job_id}/status
```

**✅ Esperado:**
```json
{
  "job_id": "abc123...",
  "status": "started",  // ou "finished", "failed"
  "created_at": "2024-...",
  "started_at": "2024-...",
  "ended_at": null,
  "result": null,
  "error": null
}
```

**⏱️ Aguardar alguns segundos e verificar novamente até status ser "finished"**

---

#### 3.3 Obter Resultado do Job

```bash
# Após job estar "finished"
curl http://localhost:3022/rfps/queue/{job_id}/result
```

**✅ Esperado:**
```json
{
  "success": true,
  "session_id": "test-session-001",
  "workflow_id": "wf-test-session-001",
  "result": { ... },
  "duration": 15.5
}
```

---

#### 3.4 Verificar Logs do Worker

```bash
docker logs rfp-agents-worker | tail -30
```

**✅ Critério de Sucesso:** Logs mostram processamento do job

---

#### 3.5 Verificar Métricas da Fila

```bash
curl http://localhost:3022/metrics | grep "queue_"
```

**✅ Esperado:** Métricas `queue_jobs_total`, `queue_job_duration_seconds`, `queue_size` presentes

---

### Fase 4: Testes de Integração MCP

#### 4.1 Importar de Portal Genérico

```bash
curl -X POST http://localhost:3022/rfps/import-from-portal \
  -H "Content-Type: application/json" \
  -d '{
    "portal_url": "https://example.com",
    "portal_type": "generic",
    "auto_process": false
  }'
```

**✅ Esperado:**
```json
{
  "success": true,
  "portal_url": "https://example.com",
  "portal_type": "generic",
  "questionnaire_text": "...",
  "parsed_questions": [...],
  "question_count": 0,
  "message": "Questionário importado com sucesso"
}
```

**⚠️ Nota:** Para Playwright/Atlassian, servidores MCP precisam estar configurados

---

#### 4.2 Importar e Processar Automaticamente

```bash
curl -X POST http://localhost:3022/rfps/import-from-portal \
  -H "Content-Type: application/json" \
  -d '{
    "portal_url": "https://example.com",
    "auto_process": true
  }'
```

**✅ Esperado:** Retorna `job_id` e enfileira automaticamente

---

### Fase 5: Testes do Workflow Completo

#### 5.1 Processar Texto Direto

```bash
curl -X POST http://localhost:3022/workflow/process \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Qual é a política de segurança de dados da empresa?"
  }'
```

**✅ Esperado:** Workflow executa e retorna respostas

---

#### 5.2 Processar Arquivo

```bash
# Criar arquivo de teste
echo "Pergunta 1: Qual é a capacidade do sistema?" > test_rfp.txt

# Enviar arquivo
curl -X POST http://localhost:3022/workflow/process-file \
  -F "file=@test_rfp.txt"
```

**✅ Esperado:** Arquivo processado e respostas geradas

---

### Fase 6: Testes do Frontend

#### 6.1 Acessar Frontend

```bash
# Abrir no navegador
# http://localhost:3021
```

**✅ Critério de Sucesso:** Página carrega sem erros

---

#### 6.2 Testar Navegação

- [ ] Acessar página de RFPs
- [ ] Acessar página de Aprovações
- [ ] Acessar página de Exploração

**✅ Critério de Sucesso:** Todas as rotas funcionam

---

#### 6.3 Testar Processamento via Frontend

1. Acessar http://localhost:3021
2. Inserir texto de RFP
3. Clicar em "Processar"
4. Aguardar resultado

**✅ Critério de Sucesso:** Processamento funciona e mostra resultado

---

### Fase 7: Testes de Aprovação (HITL)

#### 7.1 Listar Aprovações Pendentes

```bash
curl http://localhost:3022/approvals?status=pending
```

**✅ Esperado:** Lista de aprovações pendentes

---

#### 7.2 Obter Detalhes de Aprovação

```bash
# Substituir {approval_id} pelo ID real
curl http://localhost:3022/approvals/{approval_id}
```

**✅ Esperado:** Detalhes completos da aprovação

---

#### 7.3 Aprovar Respostas

```bash
curl -X POST http://localhost:3022/approvals/{approval_id}/approve \
  -H "Content-Type: application/json" \
  -d '{
    "comments": "Aprovado após revisão",
    "approved_by": "test-user"
  }'
```

**✅ Esperado:** Aprovação registrada com sucesso

---

#### 7.4 Rejeitar Respostas

```bash
curl -X POST http://localhost:3022/approvals/{approval_id}/reject \
  -H "Content-Type: application/json" \
  -d '{
    "comments": "Necessita revisão"
  }'
```

**✅ Esperado:** Rejeição registrada

---

### Fase 8: Testes de Observabilidade

#### 8.1 Verificar Langfuse

```bash
# Abrir no navegador
# http://localhost:3020
```

**✅ Critério de Sucesso:**
- [ ] Login funciona
- [ ] Traces aparecem após processar RFPs
- [ ] Métricas de LLM são visíveis

---

#### 8.2 Verificar Prometheus

```bash
# Abrir no navegador
# http://localhost:9090
```

**✅ Critério de Sucesso:**
- [ ] Interface carrega
- [ ] Métricas da aplicação aparecem
- [ ] Queries funcionam

---

#### 8.3 Verificar Grafana

```bash
# Abrir no navegador
# http://localhost:3001
# Login: admin/admin
```

**✅ Critério de Sucesso:**
- [ ] Dashboards carregam
- [ ] Métricas são exibidas
- [ ] Gráficos atualizam

---

## 🔍 Testes de Carga e Performance

### Teste de Múltiplos Jobs

```bash
# Enfileirar 10 RFPs simultaneamente
for i in {1..10}; do
  curl -X POST http://localhost:3022/rfps/queue \
    -H "Content-Type: application/json" \
    -d "{
      \"input_text\": \"Teste $i: Qual é a capacidade do sistema?\",
      \"session_id\": \"test-session-$i\"
    }" &
done
wait

# Verificar status da fila
curl http://localhost:3022/rfps/queue/info
```

**✅ Critério de Sucesso:** Todos os jobs são processados

---

## 🐛 Troubleshooting

### Problemas Comuns

#### Worker não processa jobs

```bash
# Verificar se worker está rodando
docker ps | grep worker

# Verificar logs
docker logs rfp-agents-worker

# Reiniciar worker
docker-compose restart worker
```

#### API não responde

```bash
# Verificar logs
docker-compose logs app | tail -50

# Verificar se migrações rodaram
docker-compose logs app | grep -i migration

# Reiniciar app
docker-compose restart app
```

#### Frontend não carrega

```bash
# Verificar se frontend está rodando
docker ps | grep frontend

# Verificar logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

#### Erro de conexão com banco

```bash
# Verificar se PostgreSQL está saudável
docker-compose ps postgres

# Verificar conexão
docker-compose exec postgres psql -U postgres -d rfp_agents -c "SELECT 1;"

# Verificar variável DATABASE_URL
docker-compose exec app env | grep DATABASE_URL
```

---

## ✅ Checklist Final

Antes de considerar o sistema funcional, verifique:

- [ ] Todos os serviços estão rodando
- [ ] Health check da API responde
- [ ] Frontend carrega corretamente
- [ ] Worker processa jobs
- [ ] Queue System funciona (enfileirar, status, resultado)
- [ ] Workflow processa RFPs
- [ ] Aprovações (HITL) funcionam
- [ ] Métricas são expostas
- [ ] Langfuse registra traces
- [ ] Prometheus coleta métricas
- [ ] Grafana exibe dashboards

---

## 📊 Métricas de Sucesso

### Performance Esperada

- **Tempo de resposta da API**: < 200ms (endpoints simples)
- **Tempo de processamento de RFP**: 10-60 segundos (depende da complexidade)
- **Throughput de jobs**: Múltiplos jobs simultâneos sem problemas
- **Disponibilidade**: 99%+ (serviços rodando)

### Métricas a Monitorar

- `http_requests_total`: Total de requisições
- `http_request_duration_seconds`: Latência das requisições
- `queue_jobs_total`: Jobs processados
- `queue_job_duration_seconds`: Tempo de processamento
- `agent_executions_total`: Execuções de agentes
- `llm_calls_total`: Chamadas LLM
- `llm_cost_usd`: Custo acumulado

---

## 🎯 Próximos Passos

Após validar todos os testes:

1. **Testes de Integração Contínua**: Configurar CI/CD
2. **Testes de Carga**: Usar ferramentas como Locust ou k6
3. **Testes End-to-End**: Automatizar com Playwright ou Cypress
4. **Monitoramento**: Configurar alertas no Prometheus/Grafana

---

## 📝 Notas

- Este guia assume que todos os serviços estão rodando via Docker Compose
- Para testes locais sem Docker, ajuste as URLs e comandos conforme necessário
- Alguns testes requerem configuração adicional (ex: servidores MCP)
- Mantenha este documento atualizado conforme novas funcionalidades são adicionadas


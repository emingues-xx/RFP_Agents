# Sprint 1-2: Setup e Infraestrutura (2 semanas)

## Objetivo
Configurar todo o ambiente de desenvolvimento, infraestrutura local com Docker Compose, e dependências necessárias para o projeto.

---

## Tarefa 1.1: Setup do Ambiente de Desenvolvimento
**Prioridade**: Alta  
**Estimativa**: 2 dias  
**Responsável**: DevOps/Backend

### Subtarefas:
- [ ] Configurar repositório Git com estrutura de pastas
- [ ] Configurar branch strategy (main, develop, feature/*)
- [ ] Setup de ambiente Python (venv ou conda)
- [ ] Configurar pre-commit hooks (black, flake8, mypy)
- [ ] Configurar .gitignore adequado
- [ ] Documentar processo de setup local no README

---

## Tarefa 1.2: Docker Compose para Ambiente Local
**Prioridade**: Alta  
**Estimativa**: 3 dias  
**Responsável**: DevOps/Backend

### Subtarefas:
- [ ] Criar Dockerfile para aplicação principal
- [ ] Criar docker-compose.yml com todos os serviços:
  - [ ] Aplicação Python (API + Workers)
  - [ ] PostgreSQL (banco de dados)
  - [ ] Redis (cache)
  - [ ] Vector Database (Milvus)
  - [ ] Langfuse (observabilidade LLMs)
  - [ ] Prometheus (métricas)
  - [ ] Grafana (dashboards)
- [ ] Criar arquivos .env.example com todas as variáveis
- [ ] Configurar volumes persistentes para dados
- [ ] Configurar networks entre containers
- [ ] Criar scripts de inicialização (init-db.sh, etc.)
- [ ] Documentar comandos docker-compose no README
- [ ] Testar subida completa do ambiente local
- [ ] Validar comunicação entre serviços

### Estrutura do docker-compose.yml

O docker-compose.yml deve incluir os seguintes serviços:

1. **app** (Aplicação principal)
   - Build a partir do Dockerfile
   - Portas: 8000 (API)
   - Dependências: postgres, redis, vector-db
   - Variáveis de ambiente para LLM providers

2. **postgres** (Banco de dados)
   - Imagem: postgres:15
   - Volumes para persistência
   - Porta: 5432

3. **redis** (Cache)
   - Imagem: redis:7-alpine
   - Porta: 6379

4. **vector-db** (Vector Database)
   - Milvus   

5. **langfuse** (Observabilidade LLMs)
   - Imagem oficial ou self-hosted
   - Porta: 3000

6. **prometheus** (Métricas)
   - Imagem: prom/prometheus
   - Porta: 9090
   - Config: prometheus.yml

7. **grafana** (Dashboards)
   - Imagem: grafana/grafana
   - Porta: 3001
   - Volumes para dashboards e datasources

### Arquivos Necessários

- [ ] `docker-compose.yml` - Configuração principal
- [ ] `Dockerfile` - Build da aplicação
- [ ] `.env.example` - Template de variáveis
- [ ] `prometheus.yml` - Configuração do Prometheus
- [ ] `grafana/provisioning/` - Dashboards e datasources
- [ ] `init-db.sh` - Script de inicialização do banco
- [ ] `docker-compose.override.yml` - Overrides para desenvolvimento (opcional)

---

## Tarefa 1.3: Instalação e Configuração de Dependências
**Prioridade**: Alta  
**Estimativa**: 2 dias  
**Responsável**: Backend

### Subtarefas:
- [ ] Criar requirements.txt com todas as dependências:
  - [ ] LangGraph e LangChain
  - [ ] FastAPI ou Flask (API)
  - [ ] psycopg2 (PostgreSQL)
  - [ ] redis-py (Redis)
  - [ ] Bibliotecas de processamento de documentos
  - [ ] SDKs de LLM providers
  - [ ] Langfuse SDK
  - [ ] Prometheus client
- [ ] Criar requirements-dev.txt (testes, linting)
- [ ] Configurar versões específicas (pinning)
- [ ] Testar instalação em ambiente limpo
- [ ] Documentar dependências e versões

---

## Tarefa 1.4: Configuração de LLM Providers
**Prioridade**: Alta  
**Estimativa**: 1 dia  
**Responsável**: Backend

### Subtarefas:
- [ ] Criar módulo de configuração de LLM providers
- [ ] Implementar abstração para múltiplos providers
- [ ] Configurar OpenAI (GPT-4)
- [ ] Configurar Anthropic (Claude 3.5 Sonnet)
- [ ] Implementar fallback automático
- [ ] Criar sistema de configuração por variáveis de ambiente
- [ ] Testar conexão com ambos providers
- [ ] Documentar configuração de API keys

---

## Tarefa 1.5: Setup do Langfuse
**Prioridade**: Alta  
**Estimativa**: 1 dia  
**Responsável**: Backend/DevOps

### Subtarefas:
- [ ] Configurar Langfuse no docker-compose
- [ ] Configurar variáveis de ambiente (API keys, URL)
- [ ] Integrar Langfuse SDK na aplicação
- [ ] Criar wrapper para rastreamento de chamadas LLM
- [ ] Testar rastreamento básico
- [ ] Configurar dashboards iniciais no Langfuse
- [ ] Documentar uso e acesso

---

## Tarefa 1.6: Setup do Prometheus e Grafana
**Prioridade**: Alta  
**Estimativa**: 2 dias  
**Responsável**: DevOps/Backend

### Subtarefas:
- [ ] Configurar Prometheus no docker-compose
- [ ] Criar prometheus.yml com configuração de scraping
- [ ] Integrar Prometheus client na aplicação Python
- [ ] Criar métricas customizadas iniciais:
  - [ ] Contador de requisições
  - [ ] Histograma de latência
  - [ ] Gauge de agentes ativos
- [ ] Configurar Grafana no docker-compose
- [ ] Configurar datasource do Prometheus no Grafana
- [ ] Criar dashboard básico no Grafana
- [ ] Testar coleta e visualização de métricas
- [ ] Documentar acesso e uso

---

## Tarefa 1.7: Setup de Banco de Dados e Vector Store
**Prioridade**: Alta  
**Estimativa**: 2 dias  
**Responsável**: Backend

### Subtarefas:
- [ ] Configurar PostgreSQL no docker-compose
- [ ] Criar scripts de migração (Alembic ou similar)
- [ ] Definir schema inicial do banco:
  - [ ] Tabela de sessões/conversas
  - [ ] Tabela de memória persistente
  - [ ] Tabela de aprovações
- [ ] Configurar Vector Database (Chroma/Pinecone/Weaviate)
- [ ] Criar módulo de conexão com vector store
- [ ] Testar conexões com ambos
- [ ] Criar scripts de seed/initial data (se necessário)

---

## Tarefa 1.8: CI/CD Básico
**Prioridade**: Média  
**Estimativa**: 1 dia  
**Responsável**: DevOps

### Subtarefas:
- [ ] Configurar GitHub Actions (ou similar)
- [ ] Pipeline de testes automatizados
- [ ] Pipeline de linting e formatação
- [ ] Pipeline de build de Docker images
- [ ] Configurar secrets no CI/CD
- [ ] Documentar processo de deploy

---

## Entregas do Sprint

Ao final deste sprint, deve-se ter:
- ✅ Ambiente de desenvolvimento configurado
- ✅ Docker Compose funcionando com todos os serviços
- ✅ Dependências instaladas e documentadas
- ✅ LLM providers configurados
- ✅ Observabilidade básica funcionando (Langfuse + Prometheus/Grafana)
- ✅ Banco de dados e vector store configurados
- ✅ CI/CD básico configurado


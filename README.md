# RFP Agents - Sistema de Agentes para Preenchimento de RFPs

Sistema multi-agente baseado em LangGraph (+LangChain) para preenchimento automatizado de RFPs (Request for Proposals).

## 📋 Visão Geral

Este projeto implementa um sistema de agentes de IA que trabalham em conjunto para analisar, mapear e preencher RFPs de forma automatizada, com suporte a Human-In-The-Loop (HITL) para validação e aprovação.

## 🏗️ Arquitetura

O sistema é composto por quatro agentes especializados:

1. **Orquestrador**: Coordena o fluxo de trabalho e gerencia o estado global
2. **Parser & Mapeador**: Analisa e estrutura o RFP
3. **Conhecimento & Redação**: Busca informações e redige respostas
4. **Verificador**: Valida a qualidade e completude das respostas

## 📁 Estrutura do Projeto

```
RFP_Agents/
├── src/
│   ├── backend/              # Backend Python
│   │   ├── src/              # Código fonte Python
│   │   │   ├── agents/       # Agentes especializados
│   │   │   ├── api/          # API REST (FastAPI)
│   │   │   ├── config/       # Configurações
│   │   │   ├── mcp/          # Integração MCP
│   │   │   ├── rag/          # Sistema RAG
│   │   │   ├── tools/        # Ferramentas customizadas
│   │   │   ├── utils/        # Utilitários
│   │   │   └── workflows/    # Workflows LangGraph
│   │   ├── pyproject.toml    # Configuração do projeto Python
│   │   ├── requirements.txt  # Dependências de produção
│   │   └── requirements-dev.txt  # Dependências de desenvolvimento
│   └── frontend/             # Frontend React/TypeScript
│       ├── src/              # Código fonte TypeScript
│       ├── package.json      # Dependências Node.js
│       └── vite.config.ts    # Configuração Vite
├── tests/                     # Testes (unit, integration, e2e)
├── docs/                      # Documentação
├── scripts/                   # Scripts auxiliares
├── docker/                    # Configurações Docker
├── docker-compose.yml        # Orquestração de serviços
├── Dockerfile                 # Imagem Docker do backend
└── .env                       # Variáveis de ambiente
```

## 📚 Documentação

- [PRD - Product Requirements Document](docs/PRD_RFP_Agentes.md)
- [Tarefas Detalhadas](docs/tasks/)

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.11+
- Node.js 18+ (para frontend)
- Docker e Docker Compose
- Git

### Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/emingues-xx/RFP_Agents.git
cd RFP_Agents
```

2. **Configure variáveis de ambiente:**
```bash
# Copie o arquivo .env.example se existir, ou crie um .env
# Edite .env com suas configurações (veja seção abaixo)
```

3. **Instale as dependências do backend (opcional - recomendado usar Docker):**
```bash
cd src/backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. **Instale as dependências do frontend (opcional):**
```bash
cd src/frontend
npm install
```

### Configuração de Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

#### LLM Providers
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_TEMPERATURE=0.7
ANTHROPIC_MAX_TOKENS=2000

DEFAULT_LLM_PROVIDER=openai  # ou anthropic
ENABLE_LLM_FALLBACK=true
FALLBACK_LLM_PROVIDER=anthropic
```

#### Langfuse
```env
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_BASE_URL=http://localhost:3020
```

#### Database
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=rfp_agents
```

#### Redis
```env
REDIS_PASSWORD=redis_password
REDIS_URL=redis://:redis_password@redis:6379/0
```

#### Milvus
```env
MILVUS_HOST=milvus
MILVUS_PORT=19530
MILVUS_USERNAME=root
MILVUS_PASSWORD=Milvus
```

#### MinIO
```env
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

#### Application
```env
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Uso no Código

```python
from src.utils.llm_factory import LLMFactory
from src.utils.llm_with_fallback import LLMWithFallback
from langchain_core.messages import HumanMessage

# Criar factory
factory = LLMFactory()

# Obter LLM padrão
llm = factory.get_default_llm()

# Ou usar com fallback automático
llm_wrapper = LLMWithFallback()
response = llm_wrapper.invoke([HumanMessage(content="Hello")])
```

### Executar com Docker Compose

1. **Inicie todos os serviços:**
```bash
docker-compose up -d
```

2. **Acesse a aplicação:**
- **API Backend**: http://localhost:8000
- **Frontend**: http://localhost:5173 (se configurado)
- **Langfuse**: http://localhost:3020
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

3. **Execute migrações (quando disponível):**
```bash
docker-compose exec app alembic upgrade head
```

## 🌿 Branch Strategy

- `main`: Produção/estável
- `develop`: Desenvolvimento
- `feature/*`: Features individuais
- `hotfix/*`: Correções urgentes

## 🛠️ Tecnologias

### Backend
- **Framework**: LangGraph + LangChain
- **Linguagem**: Python 3.11+
- **API**: FastAPI
- **Banco de Dados**: PostgreSQL
- **Cache**: Redis
- **Vector DB**: Milvus
- **Observabilidade**: Langfuse, Prometheus, Grafana
- **LLM Providers**: OpenAI, Anthropic (Claude)

### Frontend
- **Framework**: React + TypeScript
- **Build Tool**: Vite
- **HTTP Client**: Axios/Fetch

## 📦 Dependências Principais

### Core
- **LangChain**: 0.1.0 - Framework para construção de aplicações LLM
- **LangGraph**: 0.0.20 - Extensão para workflows em grafo
- **FastAPI**: 0.109.0 - Framework web moderno e rápido

### LLM Providers
- **OpenAI**: 1.10.0 - SDK para GPT models
- **Anthropic**: 0.18.1 - SDK para Claude models

### Observability
- **Langfuse**: 2.15.0 - Observabilidade para LLMs
- **Prometheus Client**: 0.19.0 - Métricas para Prometheus

### Database
- **PostgreSQL (psycopg2)**: 2.9.9 - Driver para PostgreSQL
- **SQLAlchemy**: 2.0.25 - ORM
- **Milvus (pymilvus)**: 2.3.4 - Vector database

### Document Processing
- **PyPDF2**: 3.0.1 - Processamento de PDFs
- **python-docx**: 1.1.0 - Processamento de DOCX
- **pytesseract**: 0.3.10 - OCR

## 📥 Instalação de Dependências

### Backend
```bash
cd src/backend

# Instalar dependências de produção
pip install -r requirements.txt

# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Ou instalar tudo de uma vez
pip install -r requirements.txt -r requirements-dev.txt
```

### Frontend
```bash
cd src/frontend
npm install
```

### Comandos Úteis

```bash
# Verificar instalação Python
python -c "import langchain; print(langchain.__version__)"
python -c "import langgraph; print(langgraph.__version__)"

# Verificar dependências conflitantes
pip check

# Listar dependências instaladas
pip list

# Gerar requirements atualizado
pip freeze > requirements-current.txt
```

## 🐳 Docker Compose

### Comandos Úteis

```bash
# Subir todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f app

# Parar todos os serviços
docker-compose down

# Parar e remover volumes
docker-compose down -v

# Rebuild da aplicação
docker-compose build app

# Executar comandos no container
docker-compose exec app bash

# Ver status dos serviços
docker-compose ps
```

### Testes de Conexão

```bash
# Testar conexão com PostgreSQL
docker-compose exec postgres psql -U postgres -d rfp_agents -c "SELECT 1;"

# Testar conexão com Redis
docker-compose exec redis redis-cli --no-auth-warning -a redis_password ping

# Testar conexão com Milvus
docker-compose exec milvus milvus health

# Testar API
curl http://localhost:8000/health
```

## 🔍 Langfuse - Observabilidade de LLMs

### Acesso
- URL: http://localhost:3020
- Credenciais: Criar conta na primeira execução

### Configuração
1. Subir serviços: `docker-compose up -d langfuse langfuse-db clickhouse`
2. Acessar http://localhost:3020
3. Criar conta
4. Obter API keys em Settings > API Keys
5. Adicionar ao `.env`:
```env
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_URL=http://localhost:3020
```

### Uso no Código
```python
from src.utils.llm_factory import LLMFactory

factory = LLMFactory()
llm = factory.create_openai_llm(session_id="session-123")
# Chamadas serão automaticamente rastreadas
response = llm.invoke([HumanMessage(content="Hello")])
```

### Visualizar Traces
- Acessar http://localhost:3020/traces
- Filtrar por session_id, modelo, etc.
- Ver custos, latência, tokens usados

### Comandos Úteis
```bash
# Subir Langfuse
docker-compose up -d langfuse langfuse-db clickhouse

# Ver logs
docker-compose logs -f langfuse

# Testar conexão
curl http://localhost:3020/api/public/health
```

## 📊 Prometheus e Grafana - Observabilidade de Sistema

### Acesso
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

### Configuração

#### Prometheus
- Coleta métricas da aplicação em `http://app:9090/metrics`
- Configuração em `docker/prometheus/prometheus.yml`
- Métricas disponíveis via endpoint `/metrics` da aplicação

#### Grafana
- Datasource do Prometheus configurado automaticamente
- Dashboard básico disponível: "RFP Agents - Application Metrics"
- Dashboards em `docker/grafana/dashboards/`

### Métricas Disponíveis

#### HTTP
- `http_requests_total`: Total de requisições HTTP
- `http_request_duration_seconds`: Duração das requisições

#### Agentes
- `agent_executions_total`: Total de execuções de agentes
- `agent_execution_duration_seconds`: Duração de execução
- `agents_active`: Número de agentes ativos

#### LLM
- `llm_calls_total`: Total de chamadas LLM
- `llm_tokens_total`: Total de tokens usados
- `llm_cost_usd`: Custo total em USD
- `llm_request_duration_seconds`: Duração de chamadas LLM

#### RAG
- `rag_queries_total`: Total de queries RAG
- `rag_retrieval_duration_seconds`: Duração de retrieval
- `rag_documents_retrieved`: Documentos recuperados

### Comandos Úteis

```bash
# Subir Prometheus e Grafana
docker-compose up -d prometheus grafana

# Verificar métricas da aplicação
curl http://localhost:8000/metrics

# Verificar métricas do Prometheus
curl http://localhost:9090/metrics

# Acessar Prometheus UI
# http://localhost:9090

# Acessar Grafana
# http://localhost:3001 (admin/admin)
```

## 🧪 Testes

### Executar Testes

```bash
cd src/backend

# Executar todos os testes
pytest

# Executar testes com cobertura
pytest --cov=src --cov-report=html

# Executar testes específicos
pytest tests/unit/test_orchestrator.py

# Executar testes de integração
pytest tests/integration/
```

## 📝 Licença

[Adicione a licença aqui]

## 👥 Contribuidores

[Adicione informações dos contribuidores aqui]

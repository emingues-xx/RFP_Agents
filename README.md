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
├── backend/              # Backend Python
│   ├── src/              # Código fonte Python
│   │   ├── agents/       # Agentes especializados
│   │   ├── api/          # API REST
│   │   ├── tools/        # Ferramentas customizadas
│   │   ├── utils/        # Utilitários
│   │   └── config/       # Configurações
│   ├── tests/            # Testes (unit, integration, e2e)
│   ├── scripts/          # Scripts auxiliares
│   ├── requirements.txt  # Dependências Python
│   ├── pyproject.toml    # Configuração do projeto
│   └── Dockerfile        # Dockerfile do backend
├── frontend/             # Frontend React/TypeScript
│   ├── src/              # Código fonte TypeScript
│   ├── package.json      # Dependências Node.js
│   └── vite.config.ts   # Configuração Vite
├── docs/                 # Documentação
├── docker/               # Configurações Docker
└── docker-compose.yml    # Orquestração de serviços
```

## 📚 Documentação

- [PRD - Product Requirements Document](Docs/PRD_RFP_Agentes.md)
- [Tarefas Detalhadas](Docs/Tarefas/README_TAREFAS.md)
- [Sprints](Docs/Sprints/)

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Git

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/emingues-xx/RFP_Agents.git
cd RFP_Agents
```

2. Crie e ative o ambiente virtual:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instale as dependências (opcional - recomendado usar Docker):
```bash
# Se desenvolver localmente (sem Docker)
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Nota: Algumas dependências podem requerer compilação no Windows
# Recomendado: usar Docker (veja passo 5)
```

4. Configure variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env com suas configurações
```

### Configuração de LLM Providers

#### OpenAI
1. Obter API key em: https://platform.openai.com/api-keys
2. Adicionar ao `.env`:
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000
```

#### Anthropic
1. Obter API key em: https://console.anthropic.com/
2. Adicionar ao `.env`:
```env
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_TEMPERATURE=0.7
ANTHROPIC_MAX_TOKENS=2000
```

#### Configuração de Provider Padrão
```env
DEFAULT_LLM_PROVIDER=openai  # ou anthropic
ENABLE_LLM_FALLBACK=true
FALLBACK_LLM_PROVIDER=anthropic
```

#### Uso no Código
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

5. Inicie os serviços com Docker Compose:
```bash
docker-compose up -d
```

6. Execute as migrações (quando disponível):
```bash
docker-compose exec app alembic upgrade head
```

7. Acesse a aplicação:
- API: http://localhost:8000
- Langfuse: http://localhost:3000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin)

## 🌿 Branch Strategy

- `main`: Produção/estável
- `develop`: Desenvolvimento
- `feature/*`: Features individuais
- `hotfix/*`: Correções urgentes

## 🛠️ Tecnologias

- **Framework**: LangGraph + LangChain
- **Linguagem**: Python
- **Banco de Dados**: PostgreSQL
- **Cache**: Redis
- **Vector DB**: Milvus
- **Observabilidade**: Langfuse, Prometheus, Grafana
- **LLM Providers**: OpenAI, Anthropic (Claude)

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

```bash
# Instalar dependências de produção
pip install -r requirements.txt

# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Ou instalar tudo de uma vez
pip install -r requirements.txt -r requirements-dev.txt
```

### Comandos Úteis

```bash
# Verificar instalação
python -c "import langchain; print(langchain.__version__)"
python -c "import langgraph; print(langgraph.__version__)"

# Verificar dependências conflitantes
pip check

# Listar dependências instaladas
pip list

# Gerar requirements atualizado
pip freeze > requirements-current.txt
```

## 📝 Licença

[Adicione a licença aqui]

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
1. Subir serviços: `docker-compose up -d langfuse langfuse-db`
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
docker-compose up -d langfuse langfuse-db

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

## 👥 Contribuidores

[Adicione informações dos contribuidores aqui]


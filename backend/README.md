# Backend - RFP Agents

Backend Python do sistema de agentes para preenchimento de RFPs.

## Estrutura

```
backend/
├── src/              # Código fonte Python
│   ├── agents/       # Agentes especializados
│   ├── api/          # API REST (FastAPI)
│   ├── config/       # Configurações
│   ├── mcp/          # Integração MCP
│   ├── rag/          # RAG e vector store
│   ├── tools/        # Ferramentas customizadas
│   ├── utils/        # Utilitários
│   └── workflows/    # Workflows LangGraph
├── tests/            # Testes
│   ├── unit/         # Testes unitários
│   ├── integration/  # Testes de integração
│   └── e2e/          # Testes end-to-end
├── scripts/          # Scripts auxiliares
├── requirements.txt  # Dependências Python
└── pyproject.toml   # Configuração do projeto
```

## Instalação

### Com Docker (Recomendado)

```bash
# Na raiz do projeto
docker-compose up -d
```

### Local

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## Executar

### API

```bash
# Com Docker
docker-compose up app

# Local
cd backend
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Testes

```bash
# Todos os testes
pytest

# Testes unitários
pytest tests/unit/

# Testes de integração
pytest tests/integration/

# Testes end-to-end
pytest tests/e2e/

# Com cobertura
pytest --cov=src --cov-report=html
```

## Configuração

Copie `.env.example` para `.env` e configure as variáveis de ambiente:

- `OPENAI_API_KEY`: Chave da API OpenAI
- `ANTHROPIC_API_KEY`: Chave da API Anthropic
- `DATABASE_URL`: URL do PostgreSQL
- `REDIS_URL`: URL do Redis
- `MILVUS_HOST`: Host do Milvus
- `LANGFUSE_PUBLIC_KEY`: Chave pública do Langfuse
- `LANGFUSE_SECRET_KEY`: Chave secreta do Langfuse

## Endpoints

- `GET /`: Informações da API
- `GET /health`: Health check
- `GET /metrics`: Métricas Prometheus
- `POST /workflow/process`: Processar texto
- `POST /workflow/process-file`: Processar arquivo
- `GET /rfps/`: Listar RFPs
- `GET /rfps/{id}`: Detalhes do RFP
- `GET /approvals/`: Listar aprovações pendentes
- `GET /approvals/{id}`: Detalhes da aprovação
- `POST /approvals/{id}/approve`: Aprovar
- `POST /approvals/{id}/reject`: Rejeitar
- `POST /approvals/{id}/edit`: Editar resposta


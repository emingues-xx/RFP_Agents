# Tarefa 1.3: Instalação e Configuração de Dependências

## Objetivo
Criar e configurar todos os arquivos de dependências Python necessários para o projeto.

## Prioridade
Alta

## Estimativa
2 dias

## Responsável
Backend

---

## Instruções de Implementação

### 1. Criar requirements.txt

#### Criar arquivo `requirements.txt`:
```txt
# Core Frameworks
langchain==0.1.0
langchain-core==0.1.10
langchain-community==0.0.10
langgraph==0.0.20
langsmith==0.0.65

# API Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.25
alembic==1.13.1

# Cache
redis==5.0.1
hiredis==2.2.3

# Vector Database
pymilvus==2.3.4

# LLM Providers
openai==1.10.0
anthropic==0.18.1

# Observability
langfuse==2.15.0
prometheus-client==0.19.0

# Document Processing
pypdf2==3.0.1
pdfplumber==0.10.3
python-docx==1.1.0
openpyxl==3.1.2
pandas==2.1.4

# OCR
pytesseract==0.3.10
Pillow==10.2.0

# Utilities
python-dotenv==1.0.0
httpx==0.26.0
aiohttp==3.9.1
tenacity==8.2.3

# MCP
mcp==0.9.0

# Embeddings
sentence-transformers==2.2.2
```

### 2. Criar requirements-dev.txt

#### Criar arquivo `requirements-dev.txt`:
```txt
# Incluir requirements base
-r requirements.txt

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
pytest-mock==3.12.0
httpx==0.26.0  # Para test client

# Linting & Formatting
black==24.1.1
flake8==7.0.0
mypy==1.8.0
isort==5.13.2

# Type stubs
types-redis==4.6.0.11
types-requests==2.31.0.20240106

# Pre-commit
pre-commit==3.6.0

# Documentation
mkdocs==1.5.3
mkdocs-material==9.5.3

# Development tools
ipython==8.20.0
ipdb==0.13.13
```

### 3. Configurar Versões Específicas (Pinning)

#### Criar script `scripts/pin-requirements.sh`:
```bash
#!/bin/bash
# Script para fixar versões exatas

pip freeze > requirements-pinned.txt
```

#### Criar `requirements-lock.txt` (opcional, para produção):
```bash
# Gerar arquivo de lock
pip-compile requirements.txt -o requirements-lock.txt
```

### 4. Criar pyproject.toml (Opcional mas Recomendado)

#### Criar arquivo `pyproject.toml`:
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "rfp-agents"
version = "0.1.0"
description = "Sistema de Agentes para Preenchimento de RFPs"
requires-python = ">=3.11"
dependencies = [
    # Será lido do requirements.txt
]

[project.optional-dependencies]
dev = [
    # Será lido do requirements-dev.txt
]

[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 100
skip_gitignore = true

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=src --cov-report=html --cov-report=term-missing"
```

### 5. Testar Instalação em Ambiente Limpo

#### Criar script `scripts/test-install.sh`:
```bash
#!/bin/bash
set -e

echo "Testing clean installation..."

# Criar venv temporário
python -m venv test_venv
source test_venv/bin/activate  # Linux/Mac
# test_venv\Scripts\activate  # Windows

# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
python -c "import langchain; print('LangChain OK')"
python -c "import langgraph; print('LangGraph OK')"
python -c "import fastapi; print('FastAPI OK')"
python -c "import openai; print('OpenAI OK')"
python -c "import anthropic; print('Anthropic OK')"
python -c "import langfuse; print('Langfuse OK')"
python -c "import prometheus_client; print('Prometheus OK')"

echo "All dependencies installed successfully!"

# Limpar
deactivate
rm -rf test_venv
```

### 6. Documentar Dependências e Versões

#### Adicionar ao README.md:
```markdown
## Dependências Principais

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

## Instalação de Dependências

```bash
# Instalar dependências de produção
pip install -r requirements.txt

# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Ou instalar tudo de uma vez
pip install -r requirements.txt -r requirements-dev.txt
```
```

---

## Checklist de Validação

- [ ] requirements.txt criado com todas as dependências
- [ ] requirements-dev.txt criado
- [ ] Versões específicas configuradas (pinning)
- [ ] pyproject.toml criado (opcional)
- [ ] Script de teste de instalação criado
- [ ] README atualizado com documentação
- [ ] Testar: Instalação em ambiente limpo deve funcionar
- [ ] Validar: Todas as importações devem funcionar
- [ ] Validar: Não há conflitos de versão

---

## Comandos de Teste

```bash
# Instalar dependências
pip install -r requirements.txt

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

---

## Troubleshooting

### Problema: Conflito de versões
**Solução**: Usar `pip-compile` para resolver dependências:
```bash
pip install pip-tools
pip-compile requirements.in
```

### Problema: Instalação lenta
**Solução**: Usar cache do pip:
```bash
pip install --cache-dir ~/.pip-cache -r requirements.txt
```

### Problema: Dependências do sistema (Tesseract, etc.)
**Solução**: Instalar via apt/yum antes:
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-por
```

---

## Próximos Passos
Após completar esta tarefa, seguir para: **Tarefa 1.4: Configuração de LLM Providers**


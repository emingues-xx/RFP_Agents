# Tarefa 1.1: Setup do Ambiente de Desenvolvimento

## Objetivo
Configurar o ambiente de desenvolvimento local com todas as ferramentas e configurações necessárias.

## Prioridade
Alta

## Estimativa
2 dias

## Responsável
DevOps/Backend

---

## Instruções de Implementação

### 1. Configurar Repositório Git com Estrutura de Pastas

#### Ações:
```bash
# Criar estrutura de pastas
mkdir -p src/agents
mkdir -p src/api
mkdir -p src/tools
mkdir -p src/utils
mkdir -p src/config
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/e2e
mkdir -p docs
mkdir -p scripts
mkdir -p docker
mkdir -p .github/workflows
```

#### Estrutura Final Esperada:
```
poc_langchain/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py
│   │   ├── parser.py
│   │   ├── knowledge.py
│   │   └── verifier.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── routes/
│   ├── tools/
│   │   ├── __init__.py
│   │   └── custom_tools.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── config/
│       ├── __init__.py
│       └── settings.py
├── tests/
├── docs/
├── scripts/
├── docker/
└── .github/workflows/
```

### 2. Configurar Branch Strategy

#### Ações:
```bash
# Criar branches principais
git checkout -b develop
git checkout -b main

# Configurar branch padrão
git config init.defaultBranch main
```

#### Documentar no README:
```markdown
## Branch Strategy
- `main`: Produção/estável
- `develop`: Desenvolvimento
- `feature/*`: Features individuais
- `hotfix/*`: Correções urgentes
```

### 3. Setup de Ambiente Python

#### Ações:
```bash
# Criar venv
python -m venv venv

# Ativar venv (Windows)
venv\Scripts\activate

# Ativar venv (Linux/Mac)
source venv/bin/activate

# Criar arquivo .python-version (se usar pyenv)
echo "3.11" > .python-version
```

### 4. Configurar Pre-commit Hooks

#### Criar arquivo `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-toml
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100, --extend-ignore=E203]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports]
```

#### Instalar pre-commit:
```bash
pip install pre-commit
pre-commit install
```

### 5. Configurar .gitignore

#### Criar arquivo `.gitignore`:
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.*.local

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Build
dist/
build/
*.egg-info/

# Logs
*.log
logs/

# Database
*.db
*.sqlite

# Docker
.dockerignore

# OS
.DS_Store
Thumbs.db

# Project specific
*.pdf
*.docx
*.xlsx
data/
models/
```

### 6. Documentar Processo de Setup Local no README

#### Criar/Atualizar `README.md`:
```markdown
# Sistema de Agentes para Preenchimento de RFPs

## Setup Local

### Pré-requisitos
- Python 3.11+
- Docker e Docker Compose
- Git

### Instalação

1. Clone o repositório:
```bash
git clone <repo-url>
cd poc_langchain
```

2. Crie e ative o ambiente virtual:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Configure variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env com suas configurações
```

5. Inicie os serviços com Docker Compose:
```bash
docker-compose up -d
```

6. Execute as migrações:
```bash
alembic upgrade head
```

7. Inicie a aplicação:
```bash
uvicorn src.api.main:app --reload
```

## Estrutura do Projeto

[Descrever estrutura]
```

---

## Checklist de Validação

- [ ] Estrutura de pastas criada
- [ ] Branch strategy configurada
- [ ] Ambiente Python (venv) criado e ativado
- [ ] Pre-commit hooks instalados e funcionando
- [ ] .gitignore configurado
- [ ] README.md criado com instruções de setup
- [ ] Testar: `pre-commit run --all-files` deve passar

---


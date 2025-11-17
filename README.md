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
│   ├── agents/          # Agentes especializados
│   ├── api/             # API REST
│   ├── tools/            # Ferramentas customizadas
│   ├── utils/            # Utilitários
│   └── config/           # Configurações
├── tests/                # Testes (unit, integration, e2e)
├── docs/                 # Documentação
├── scripts/              # Scripts auxiliares
└── docker/               # Configurações Docker
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

6. Execute as migrações (quando disponível):
```bash
alembic upgrade head
```

7. Inicie a aplicação:
```bash
uvicorn src.api.main:app --reload
```

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

## 📝 Licença

[Adicione a licença aqui]

## 👥 Contribuidores

[Adicione informações dos contribuidores aqui]


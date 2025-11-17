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


# Script PowerShell para testar instalação limpa
# Equivalente ao test-install.sh para Windows

Write-Host "Testing clean installation..." -ForegroundColor Cyan

# Criar venv temporário
python -m venv test_venv
.\test_venv\Scripts\Activate.ps1

# Atualizar pip
python -m pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
Write-Host "`nVerifying installations..." -ForegroundColor Yellow
python -c "import langchain; print('LangChain OK')"
python -c "import langgraph; print('LangGraph OK')"
python -c "import fastapi; print('FastAPI OK')"
python -c "import openai; print('OpenAI OK')"
python -c "import anthropic; print('Anthropic OK')"
python -c "import langfuse; print('Langfuse OK')"
python -c "import prometheus_client; print('Prometheus OK')"

Write-Host "`nAll dependencies installed successfully!" -ForegroundColor Green

# Limpar
deactivate
Remove-Item -Recurse -Force test_venv


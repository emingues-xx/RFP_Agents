FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    tesseract-ocr \
    tesseract-ocr-por \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY src/ ./src/
COPY alembic.ini .
COPY alembic/ ./alembic/

# Expor porta
EXPOSE 8000

# Comando padrão
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]


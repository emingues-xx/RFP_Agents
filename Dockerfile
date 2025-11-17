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
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Atualizar certificados e pip
RUN apt-get update && apt-get install -y ca-certificates && \
    update-ca-certificates && \
    pip install --upgrade pip setuptools wheel --trusted-host pypi.org --trusted-host files.pythonhosted.org

# Copiar requirements
COPY src/backend/requirements.txt .

# Instalar dependências em etapas para evitar problemas de resolução
# Primeiro: dependências core sem versões flexíveis
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    langchain==0.1.0 \
    langchain-core==0.1.10 \
    langchain-community==0.0.10 \
    langgraph==0.0.20 \
    fastapi==0.109.0 \
    uvicorn[standard]==0.27.0 \
    pydantic==2.5.3 \
    pydantic-settings==2.1.0 \
    psycopg2-binary==2.9.9 \
    sqlalchemy==2.0.25 \
    alembic==1.13.1 \
    redis==5.0.1 \
    rq==1.15.1

# Segundo: dependências com versões flexíveis
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    langgraph-checkpoint-postgres \
    langchain-postgres \
    "langsmith>=0.0.77,<0.1.0" \
    "hiredis>=3.3.0" \
    pymilvus==2.3.4 \
    "langchain-milvus>=0.1.0" \
    "pyarrow>=12.0.0" \
    "ujson>=2.0.0" \
    "protobuf>=3.20.0" \
    "minio>=7.0.0" \
    "environs<=9.5.0"

# Terceiro: LLM e observabilidade
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    openai==1.10.0 \
    anthropic==0.18.1 \
    langfuse==2.60.10 \
    "wrapt>=1.14,<2.0" \
    prometheus-client==0.19.0

# Quarto: processamento de documentos
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    pypdf2==3.0.1 \
    pdfplumber==0.10.3 \
    pdfminer.six==20221105 \
    "pypdfium2>=4.18.0" \
    python-docx==1.1.0 \
    "lxml>=3.1.0" \
    openpyxl==3.1.2 \
    pandas==2.1.4 \
    pytz \
    tzdata

# Quinto: OCR e utilitários
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    pytesseract==0.3.10 \
    Pillow==10.2.0 \
    "pdf2image>=1.16.0" \
    python-dotenv==1.0.0 \
    httpx==0.26.0 \
    aiohttp==3.9.1 \
    tenacity==8.2.3 \
    mcp==0.9.1 \
    "sentence-transformers>=2.3.0"

# Copiar código
COPY src/backend/src/ ./src/
COPY src/backend/alembic.ini .
COPY src/backend/alembic/ ./alembic/
COPY scripts/run_migrations.py ./scripts/

# Expor porta
EXPOSE 8000

# Comando padrão
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]


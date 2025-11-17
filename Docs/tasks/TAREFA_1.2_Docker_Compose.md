# Tarefa 1.2: Docker Compose para Ambiente Local

## Objetivo
Criar configuração completa do Docker Compose com todos os serviços necessários para rodar o sistema localmente.

## Prioridade
Alta

## Estimativa
3 dias

## Responsável
DevOps/Backend

---

## Instruções de Implementação

### 1. Criar Dockerfile para Aplicação Principal

#### Criar arquivo `Dockerfile` na raiz:
```dockerfile
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
```

### 2. Criar docker-compose.yml

#### Criar arquivo `docker-compose.yml` na raiz:
```yaml
version: '3.8'

services:
  # Aplicação Principal
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: rfp-agents-app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/rfp_agents
      - REDIS_URL=redis://:${REDIS_PASSWORD:-redis_password}@redis:6379/0
      - REDIS_PASSWORD=${REDIS_PASSWORD:-redis_password}
      - MILVUS_HOST=milvus
      - MILVUS_PORT=19530
      - MILVUS_USERNAME=${MILVUS_USERNAME:-root}
      - MILVUS_PASSWORD=${MILVUS_PASSWORD:-Milvus}
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
      - LANGFUSE_URL=http://langfuse:3000
      - LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}
      - LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - PROMETHEUS_PORT=9090
    volumes:
      - ./src:/app/src
      - ./alembic:/app/alembic
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      milvus:
        condition: service_started
      etcd:
        condition: service_started
      minio:
        condition: service_started
    networks:
      - rfp-network
    restart: unless-stopped

  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: rfp-agents-postgres
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=rfp_agents
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sh:/docker-entrypoint-initdb.d/init-db.sh
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - rfp-network
    restart: unless-stopped

  # Redis
  redis:
    image: redis:7-alpine
    container_name: rfp-agents-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    command: redis-server --requirepass ${REDIS_PASSWORD:-redis_password} --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "--no-auth-warning", "-a", "${REDIS_PASSWORD:-redis_password}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - rfp-network

  # Milvus Dependencies - etcd
  etcd:
    image: quay.io/coreos/etcd:v3.5.5
    container_name: rfp-agents-etcd
    restart: unless-stopped
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000
      - ETCD_QUOTA_BACKEND_BYTES=4294967296
      - ETCD_SNAPSHOT_COUNT=50000
    command: >
      etcd
      --name milvus-etcd
      --data-dir /etcd
      --listen-peer-urls http://0.0.0.0:2380
      --listen-client-urls http://0.0.0.0:2379
      --advertise-client-urls http://etcd:2379
      --initial-advertise-peer-urls http://etcd:2380
      --initial-cluster milvus-etcd=http://etcd:2380
      --initial-cluster-state new
    volumes:
      - etcd_data:/etcd
    networks:
      - rfp-network

  # Milvus Dependencies - MinIO
  minio:
    image: minio/minio:RELEASE.2023-07-21T21-12-44Z
    container_name: rfp-agents-minio
    restart: unless-stopped
    environment:
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    networks:
      - rfp-network

  # Milvus (Vector Database)
  milvus:
    image: milvusdb/milvus:v2.3.3
    container_name: rfp-agents-milvus
    restart: unless-stopped
    command: ["milvus", "run", "standalone"]
    environment:
      - ETCD_ENDPOINTS=etcd:2379
      - MINIO_ADDRESS=minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
      - MILVUS_USERNAME=${MILVUS_USERNAME:-root}
      - MILVUS_PASSWORD=${MILVUS_PASSWORD:-Milvus}
      - MILVUS_ENABLE_RBAC=true
    ports:
      - "19530:19530"
      - "9091:9091"
    volumes:
      - milvus_data:/var/lib/milvus
    depends_on:
      - etcd
      - minio
    networks:
      - rfp-network

  # Langfuse
  langfuse:
    image: langfuse/langfuse:latest
    container_name: rfp-agents-langfuse
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@langfuse-db:5432/langfuse
      - NEXTAUTH_SECRET=${LANGFUSE_SECRET_KEY}
      - SALT=${LANGFUSE_SECRET_KEY}
      - LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES=true
    depends_on:
      - langfuse-db
    networks:
      - rfp-network
    restart: unless-stopped

  langfuse-db:
    image: postgres:15-alpine
    container_name: rfp-agents-langfuse-db
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=langfuse
    volumes:
      - langfuse_db_data:/var/lib/postgresql/data
    networks:
      - rfp-network
    restart: unless-stopped

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: rfp-agents-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./docker/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - rfp-network
    restart: unless-stopped

  # Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: rfp-agents-grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./docker/grafana/provisioning:/etc/grafana/provisioning
      - ./docker/grafana/dashboards:/var/lib/grafana/dashboards
    depends_on:
      - prometheus
    networks:
      - rfp-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  milvus_data:
  etcd_data:
  minio_data:
  langfuse_db_data:
  prometheus_data:
  grafana_data:

networks:
  rfp-network:
    driver: bridge
```

### 3. Criar .env.example

#### Criar arquivo `.env.example`:
```env
# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Langfuse
LANGFUSE_SECRET_KEY=your-secret-key-here
LANGFUSE_PUBLIC_KEY=your-public-key-here

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=rfp_agents

# Redis
REDIS_PASSWORD=redis_password
REDIS_URL=redis://:redis_password@redis:6379/0

# Milvus
MILVUS_HOST=milvus
MILVUS_PORT=19530
MILVUS_USERNAME=root
MILVUS_PASSWORD=Milvus

# MinIO
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 4. Criar prometheus.yml

#### Criar arquivo `docker/prometheus/prometheus.yml`:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'app'
    static_configs:
      - targets: ['app:9090']
    metrics_path: '/metrics'
```

### 5. Configurar Grafana Provisioning

#### Criar `docker/grafana/provisioning/datasources/prometheus.yml`:
```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
```

#### Criar `docker/grafana/provisioning/dashboards/dashboard.yml`:
```yaml
apiVersion: 1

providers:
  - name: 'Default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
```

### 6. Criar Script de Inicialização do Banco

#### Criar `scripts/init-db.sh`:
```bash
#!/bin/bash
set -e

echo "Initializing database..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Criar extensões necessárias
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "vector";
    
    -- Tabelas serão criadas via Alembic
    -- Este script apenas prepara o ambiente
EOSQL

echo "Database initialized successfully!"
```

#### Tornar executável:
```bash
chmod +x scripts/init-db.sh
```

### 7. Criar docker-compose.override.yml (Opcional)

#### Criar `docker-compose.override.yml`:
```yaml
version: '3.8'

services:
  app:
    volumes:
      - ./src:/app/src:cached
    environment:
      - LOG_LEVEL=DEBUG
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 8. Documentar Comandos Docker Compose

#### Adicionar ao README.md:
```markdown
## Docker Compose

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

### Acessos

- API: http://localhost:8000
- Langfuse: http://localhost:3000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
```

---

## Checklist de Validação

- [ ] Dockerfile criado e testado
- [ ] docker-compose.yml criado com todos os serviços
- [ ] .env.example criado com todas as variáveis
- [ ] prometheus.yml configurado
- [ ] Grafana provisioning configurado
- [ ] init-db.sh criado e executável
- [ ] docker-compose.override.yml criado (opcional)
- [ ] README atualizado com comandos
- [ ] Testar: `docker-compose up -d` deve subir todos os serviços
- [ ] Validar: Todos os serviços devem estar healthy
- [ ] Validar: Comunicação entre serviços funcionando

---

## Comandos de Teste

```bash
# Subir ambiente
docker-compose up -d

# Verificar saúde dos serviços
docker-compose ps

# Ver logs
docker-compose logs -f

# Testar conexão com PostgreSQL
docker-compose exec postgres psql -U postgres -d rfp_agents -c "SELECT 1;"

# Testar conexão com Redis
docker-compose exec redis redis-cli --no-auth-warning -a redis_password ping

# Testar conexão com Milvus
docker-compose exec milvus milvus health

# Testar API
curl http://localhost:8000/health
```

---

## Próximos Passos
Após completar esta tarefa, seguir para: **Tarefa 1.3: Instalação e Configuração de Dependências**


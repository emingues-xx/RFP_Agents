#!/bin/bash
set -e

echo "Initializing database..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Criar extensões necessárias
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";   
    -- Tabelas serão criadas via Alembic ou LangChain
    -- Este script apenas prepara o ambiente
EOSQL

# Criar índices para chat_history (se tabela já existir)
if psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -c "\d chat_history" > /dev/null 2>&1; then
    echo "Creating indexes for chat_history..."
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/create_memory_tables.sql 2>/dev/null || echo "Indexes will be created when table exists"
fi

echo "Database initialized successfully!"


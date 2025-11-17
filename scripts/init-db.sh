#!/bin/bash
set -e

echo "Initializing database..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Criar extensões necessárias
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";   
    -- Tabelas serão criadas via Alembic
    -- Este script apenas prepara o ambiente
EOSQL

echo "Database initialized successfully!"


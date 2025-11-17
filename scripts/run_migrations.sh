#!/bin/bash
# Script para rodar migrações Alembic

set -e

echo "🔄 Rodando migrações do banco de dados..."

cd /app

# Usar DATABASE_URL do ambiente
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@postgres:5432/rfp_agents}"

# Rodar migrações
alembic upgrade head

echo "✅ Migrações concluídas!"


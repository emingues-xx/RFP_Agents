#!/usr/bin/env python
"""Script para rodar migrações Alembic."""
import os
import sys
from pathlib import Path

# Adicionar /app ao path
if '/app' not in sys.path:
    sys.path.insert(0, '/app')

from alembic import command
from alembic.config import Config
from src.config.settings import get_settings

def main():
    """Rodar migrações."""
    print("🔄 Rodando migrações do banco de dados...")
    
    # Obter DATABASE_URL
    settings = get_settings()
    database_url = settings.database_url
    
    # Configurar Alembic
    alembic_cfg = Config('/app/alembic.ini')
    
    # Substituir URL no config
    alembic_cfg.set_main_option('sqlalchemy.url', database_url)
    
    # Rodar migrações
    try:
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrações concluídas!")
    except Exception as e:
        print(f"❌ Erro ao rodar migrações: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


"""Script para popular base de conhecimento."""
import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.ingestion_pipeline import IngestionPipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Função principal."""
    logger.info("Iniciando seed da base de conhecimento")
    
    pipeline = IngestionPipeline()
    
    # Diretórios de conhecimento (criar se não existirem)
    base_dir = Path("docs/knowledge")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Ingerir documentos iniciais por categoria
    categories = {
        "técnico": base_dir / "technical",
        "segurança": base_dir / "security",
        "compliance": base_dir / "compliance",
        "jurídico": base_dir / "legal"
    }
    
    total_files = 0
    for category, path in categories.items():
        if path.exists() and path.is_dir():
            logger.info(f"Ingerindo categoria '{category}' de {path}")
            results = pipeline.ingest_directory(str(path), category=category)
            file_count = len(results)
            total_files += file_count
            logger.info(f"  {file_count} arquivos processados")
        else:
            logger.warning(f"Diretório não encontrado: {path} (criando diretório vazio)")
            path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Seed concluído: {total_files} arquivos totais processados")
    
    if total_files == 0:
        logger.warning("Nenhum arquivo foi ingerido. Adicione documentos em docs/knowledge/")
        logger.info("Estrutura esperada:")
        for category, path in categories.items():
            logger.info(f"  {path}/")


if __name__ == "__main__":
    main()


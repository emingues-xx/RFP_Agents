"""Pipeline de ingestão de documentos."""
from typing import List, Dict, Any, Optional
from pathlib import Path
from src.rag.document_processor import DocumentProcessor
from src.rag.vector_store import VectorStoreManager
import logging

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Pipeline de ingestão."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        collection_name: str = "rfp_knowledge",
        embedding_provider: Optional[str] = None
    ):
        """Inicializar pipeline.
        
        Args:
            chunk_size: Tamanho dos chunks
            chunk_overlap: Overlap entre chunks
            collection_name: Nome da coleção no Milvus
            embedding_provider: Provider de embeddings
        """
        self.processor = DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.vector_store = VectorStoreManager(
            collection_name=collection_name,
            embedding_provider=embedding_provider
        )
        logger.info("IngestionPipeline inicializado")
    
    def ingest_document(
        self,
        file_path: str,
        category: str = "geral",
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Ingerir documento.
        
        Args:
            file_path: Caminho do arquivo
            category: Categoria do documento
            metadata: Metadados adicionais
        
        Returns:
            Lista de IDs dos chunks adicionados
        """
        logger.info(f"Ingerindo documento: {file_path} (categoria: {category})")
        
        # Preparar metadados
        doc_metadata = metadata.copy() if metadata else {}
        doc_metadata["category"] = category
        
        # Processar documento
        chunks = self.processor.process_document(file_path, doc_metadata)
        
        if not chunks:
            logger.warning(f"Nenhum chunk criado para {file_path}")
            return []
        
        # Adicionar categoria aos metadados de cada chunk (já deve estar, mas garantir)
        for chunk in chunks:
            chunk.metadata["category"] = category
        
        # Inserir no vector store
        ids = self.vector_store.add_documents(chunks)
        
        logger.info(f"Documento {file_path} ingerido: {len(chunks)} chunks, {len(ids)} IDs")
        return ids
    
    def ingest_text(
        self,
        text: str,
        category: str = "geral",
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Ingerir texto direto.
        
        Args:
            text: Texto para ingerir
            category: Categoria do texto
            metadata: Metadados adicionais
        
        Returns:
            Lista de IDs dos chunks adicionados
        """
        logger.info(f"Ingerindo texto ({len(text)} caracteres, categoria: {category})")
        
        # Preparar metadados
        doc_metadata = metadata.copy() if metadata else {}
        doc_metadata["category"] = category
        
        # Processar texto
        chunks = self.processor.process_text(text, doc_metadata)
        
        if not chunks:
            logger.warning("Nenhum chunk criado do texto")
            return []
        
        # Adicionar categoria
        for chunk in chunks:
            chunk.metadata["category"] = category
        
        # Inserir no vector store
        ids = self.vector_store.add_documents(chunks)
        
        logger.info(f"Texto ingerido: {len(chunks)} chunks, {len(ids)} IDs")
        return ids
    
    def ingest_directory(
        self,
        directory: str,
        category: str = "geral",
        file_extensions: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """Ingerir diretório completo.
        
        Args:
            directory: Caminho do diretório
            category: Categoria para todos os arquivos
            file_extensions: Extensões de arquivo aceitas (None = todas)
        
        Returns:
            Dicionário mapeando caminho do arquivo para lista de IDs
        """
        logger.info(f"Ingerindo diretório: {directory} (categoria: {category})")
        
        results = {}
        path = Path(directory)
        
        if not path.exists():
            logger.error(f"Diretório não existe: {directory}")
            return results
        
        # Extensões suportadas
        if file_extensions is None:
            file_extensions = [".pdf", ".docx", ".txt", ".md", ".xlsx", ".xls", ".csv"]
        
        file_count = 0
        for file_path in path.rglob("*"):
            if file_path.is_file():
                # Verificar extensão
                if file_path.suffix.lower() not in file_extensions:
                    logger.debug(f"Pulando arquivo (extensão não suportada): {file_path}")
                    continue
                
                try:
                    ids = self.ingest_document(str(file_path), category)
                    results[str(file_path)] = ids
                    file_count += 1
                except Exception as e:
                    logger.error(f"Erro ao ingerir {file_path}: {e}")
        
        logger.info(f"Diretório ingerido: {file_count} arquivos processados")
        return results


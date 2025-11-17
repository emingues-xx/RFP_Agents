"""Processador de documentos para RAG."""
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processador de documentos para ingestão."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Inicializar processador."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        logger.info(f"DocumentProcessor inicializado (chunk_size={chunk_size}, overlap={chunk_overlap})")
    
    def process_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """Processar documento e criar chunks."""
        logger.info(f"Processando documento: {file_path}")
        
        # Extrair texto (usar ParserAgent)
        from src.agents.parser import ParserAgent
        from src.utils.llm_factory import LLMFactory
        
        # Criar LLM temporário (não será usado para extração)
        factory = LLMFactory()
        llm = factory.get_default_llm()
        parser = ParserAgent(llm=llm)
        
        try:
            raw_text = parser.extract_from_file(file_path)
            
            if not raw_text or len(raw_text.strip()) == 0:
                logger.warning(f"Documento {file_path} está vazio ou não pôde ser extraído")
                return []
            
            # Preparar metadados base
            base_metadata = metadata.copy() if metadata else {}
            base_metadata["source"] = str(file_path)
            base_metadata["file_name"] = Path(file_path).name
            
            # Criar chunks
            chunks = self.text_splitter.create_documents(
                [raw_text],
                metadatas=[base_metadata]
            )
            
            # Adicionar metadados adicionais a cada chunk
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk.page_content)
                })
            
            logger.info(f"Documento {file_path} processado: {len(chunks)} chunks criados")
            return chunks
            
        except Exception as e:
            logger.error(f"Erro ao processar documento {file_path}: {e}")
            raise
    
    def process_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """Processar texto direto e criar chunks."""
        logger.debug(f"Processando texto ({len(text)} caracteres)")
        
        base_metadata = metadata.copy() if metadata else {}
        
        # Criar chunks
        chunks = self.text_splitter.create_documents(
            [text],
            metadatas=[base_metadata]
        )
        
        # Adicionar metadados adicionais
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_size": len(chunk.page_content)
            })
        
        logger.info(f"Texto processado: {len(chunks)} chunks criados")
        return chunks


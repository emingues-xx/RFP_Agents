"""Retriever otimizado para RAG."""
from typing import List, Optional, Dict, Any
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from src.rag.vector_store import VectorStoreManager
import logging

logger = logging.getLogger(__name__)


class OptimizedRetriever(BaseRetriever):
    """Retriever otimizado com re-ranking."""
    
    def __init__(
        self,
        vector_store_manager: VectorStoreManager,
        top_k: int = 10,
        final_k: int = 5
    ):
        """Inicializar retriever.
        
        Args:
            vector_store_manager: Gerenciador de vector store
            top_k: Número inicial de documentos a recuperar
            final_k: Número final de documentos a retornar após re-ranking
        """
        super().__init__()
        self.vector_store_manager = vector_store_manager
        self.top_k = top_k
        self.final_k = final_k
        logger.info(f"OptimizedRetriever inicializado (top_k={top_k}, final_k={final_k})")
    
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None,
        category: Optional[str] = None
    ) -> List[Document]:
        """Recuperar documentos relevantes.
        
        Args:
            query: Query de busca
            run_manager: Callback manager (não usado)
            category: Categoria opcional para filtrar
        
        Returns:
            Lista de documentos relevantes
        """
        logger.debug(f"Recuperando documentos para query: {query[:50]}... (categoria: {category})")
        
        # Busca inicial
        filter_dict = {"category": category} if category else None
        docs = self.vector_store_manager.similarity_search(
            query,
            k=self.top_k,
            filter=filter_dict
        )
        
        logger.debug(f"Recuperados {len(docs)} documentos iniciais")
        
        # Re-ranking simples (por enquanto, apenas limitar)
        # TODO: Implementar re-ranking com modelo dedicado
        final_docs = docs[:self.final_k]
        
        logger.info(f"Retornando {len(final_docs)} documentos após re-ranking")
        return final_docs
    
    def get_relevant_documents(
        self,
        query: str,
        category: Optional[str] = None
    ) -> List[Document]:
        """Método público para recuperar documentos.
        
        Args:
            query: Query de busca
            category: Categoria opcional
        
        Returns:
            Lista de documentos relevantes
        """
        return self._get_relevant_documents(query, category=category)


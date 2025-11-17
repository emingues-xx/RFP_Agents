"""Gerenciador de vector store."""
from typing import List, Optional, Dict, Any
from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document
from langchain_milvus import Milvus
from src.rag.embeddings import EmbeddingFactory
from src.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class VectorStoreManager:
    """Gerenciador de vector store."""
    
    def __init__(self, collection_name: str = "rfp_knowledge", embedding_provider: Optional[str] = None):
        """Inicializar gerenciador.
        
        Args:
            collection_name: Nome da coleção no Milvus
            embedding_provider: Provider de embeddings ("openai" ou "huggingface")
        """
        self.collection_name = collection_name
        self.embeddings = EmbeddingFactory.create_embeddings(embedding_provider)
        self.vector_store: Optional[Milvus] = None
        self._create_vector_store()
        logger.info(f"VectorStoreManager inicializado com coleção: {collection_name}")
    
    def _create_vector_store(self) -> None:
        """Criar instância do vector store."""
        try:
            self.vector_store = Milvus(
                embedding_function=self.embeddings,
                connection_args={
                    "host": settings.milvus_host,
                    "port": settings.milvus_port,
                    "user": settings.milvus_username,
                    "password": settings.milvus_password
                },
                collection_name=self.collection_name,
                auto_id=True
            )
            logger.info(f"Vector store criado: {self.collection_name}")
        except Exception as e:
            logger.error(f"Erro ao criar vector store: {e}")
            raise
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Adicionar documentos ao vector store.
        
        Args:
            documents: Lista de documentos para adicionar
        
        Returns:
            Lista de IDs dos documentos adicionados
        """
        if not documents:
            logger.warning("Nenhum documento para adicionar")
            return []
        
        try:
            ids = self.vector_store.add_documents(documents)
            logger.info(f"Adicionados {len(documents)} documentos ao vector store {self.collection_name}")
            return ids
        except Exception as e:
            logger.error(f"Erro ao adicionar documentos: {e}")
            raise
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """Buscar documentos similares.
        
        Args:
            query: Query de busca
            k: Número de resultados a retornar
            filter: Filtros opcionais (ex: {"category": "técnico"})
        
        Returns:
            Lista de documentos relevantes
        """
        try:
            if filter:
                # Milvus usa expressões de filtro específicas
                # Por enquanto, fazer busca sem filtro e filtrar depois
                # TODO: Implementar filtros nativos do Milvus
                results = self.vector_store.similarity_search(query, k=k * 2)
                # Filtrar resultados
                filtered_results = []
                for doc in results:
                    doc_metadata = doc.metadata
                    match = True
                    for key, value in filter.items():
                        if doc_metadata.get(key) != value:
                            match = False
                            break
                    if match:
                        filtered_results.append(doc)
                        if len(filtered_results) >= k:
                            break
                return filtered_results
            else:
                results = self.vector_store.similarity_search(query, k=k)
                return results
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple[Document, float]]:
        """Buscar documentos similares com scores.
        
        Args:
            query: Query de busca
            k: Número de resultados a retornar
            filter: Filtros opcionais
        
        Returns:
            Lista de tuplas (Document, score)
        """
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            logger.error(f"Erro na busca com score: {e}")
            return []
    
    def create_collection_for_category(self, category: str) -> Milvus:
        """Criar coleção específica para categoria.
        
        Args:
            category: Categoria da coleção
        
        Returns:
            Instância de Milvus para a coleção
        """
        collection_name = f"{self.collection_name}_{category}"
        logger.info(f"Criando coleção para categoria: {collection_name}")
        
        return Milvus(
            embedding_function=self.embeddings,
            connection_args={
                "host": settings.milvus_host,
                "port": settings.milvus_port,
                "user": settings.milvus_username,
                "password": settings.milvus_password
            },
            collection_name=collection_name,
            auto_id=True
        )
    
    def delete_collection(self, collection_name: Optional[str] = None) -> None:
        """Deletar coleção.
        
        Args:
            collection_name: Nome da coleção (usa self.collection_name se None)
        """
        collection = collection_name or self.collection_name
        try:
            # Milvus não tem método direto para deletar via LangChain
            # Isso precisaria ser feito via pymilvus diretamente
            logger.warning(f"Deleção de coleção {collection} requer acesso direto ao Milvus")
        except Exception as e:
            logger.error(f"Erro ao deletar coleção: {e}")
            raise


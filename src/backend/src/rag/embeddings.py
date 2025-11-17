"""Geração de embeddings."""
from typing import Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from src.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingFactory:
    """Factory para criação de embeddings."""
    
    @staticmethod
    def create_embeddings(provider: Optional[str] = None) -> Embeddings:
        """Criar instância de embeddings.
        
        Args:
            provider: Provider de embeddings ("openai" ou "huggingface").
                     Se None, usa OPENAI se disponível, senão HuggingFace.
        
        Returns:
            Instância de Embeddings
        """
        # Determinar provider se não especificado
        if provider is None:
            if settings.openai_api_key:
                provider = "openai"
                logger.info("Usando OpenAI embeddings (API key disponível)")
            else:
                provider = "huggingface"
                logger.info("Usando HuggingFace embeddings (fallback)")
        
        if provider == "openai":
            if not settings.openai_api_key:
                logger.warning("OpenAI API key não configurada, usando HuggingFace como fallback")
                return EmbeddingFactory.create_embeddings("huggingface")
            
            embeddings = OpenAIEmbeddings(
                openai_api_key=settings.openai_api_key,
                model="text-embedding-3-small"  # Modelo mais eficiente
            )
            logger.info("OpenAI embeddings criado")
            return embeddings
            
        elif provider == "huggingface":
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},  # Usar CPU por padrão
                encode_kwargs={"normalize_embeddings": True}
            )
            logger.info("HuggingFace embeddings criado")
            return embeddings
            
        else:
            raise ValueError(f"Provider desconhecido: {provider}. Use 'openai' ou 'huggingface'")


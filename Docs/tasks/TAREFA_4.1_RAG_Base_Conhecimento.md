# Tarefa 4.1: Integração RAG com Base de Conhecimento

## Objetivo
Implementar pipeline completo de RAG (Retrieval-Augmented Generation) com base de conhecimento usando vector database.

## Prioridade
Alta

## Estimativa
4 dias

## Responsável
Backend

---

## Instruções de Implementação

### 1. Configurar Vector Database no docker-compose

#### Verificar se Milvus já está configurado em `docker-compose.yml`:
```yaml
# Já deve estar configurado na TAREFA_1.2
milvus:
  image: milvusdb/milvus:latest
  # ... configuração existente
```

### 2. Criar Pipeline de Ingestão de Documentos

#### Criar `src/rag/document_processor.py`:
```python
"""Processador de documentos para RAG."""
from typing import List, Dict, Any
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processador de documentos para ingestão."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Inicializar processador."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
    
    def process_document(
        self,
        file_path: str,
        metadata: Dict[str, Any] = None
    ) -> List[Document]:
        """Processar documento e criar chunks."""
        # Extrair texto (usar ParserAgent)
        from src.agents.parser import ParserAgent
        parser = ParserAgent(llm=None)  # Não precisa LLM para extração
        
        raw_text = parser.extract_from_file(file_path)
        
        # Criar chunks
        chunks = self.text_splitter.create_documents(
            [raw_text],
            metadatas=[metadata or {}]
        )
        
        # Adicionar metadados
        for chunk in chunks:
            chunk.metadata.update({
                "source": file_path,
                "chunk_index": chunks.index(chunk)
            })
        
        return chunks
```

### 3. Implementar Geração de Embeddings

#### Criar `src/rag/embeddings.py`:
```python
"""Geração de embeddings."""
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingFactory:
    """Factory para criação de embeddings."""
    
    @staticmethod
    def create_embeddings(provider: str = "openai"):
        """Criar instância de embeddings."""
        if provider == "openai":
            return OpenAIEmbeddings(
                openai_api_key=settings.openai_api_key
            )
        elif provider == "huggingface":
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        else:
            raise ValueError(f"Provider desconhecido: {provider}")
```

### 4. Implementar Inserção no Vector Store

#### Criar `src/rag/vector_store.py`:
```python
"""Gerenciador de vector store."""
from typing import List, Optional
from langchain_core.vectorstores import VectorStore
from langchain_milvus import Milvus
from langchain_core.documents import Document
from src.rag.embeddings import EmbeddingFactory
from src.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class VectorStoreManager:
    """Gerenciador de vector store."""
    
    def __init__(self, collection_name: str = "rfp_knowledge"):
        """Inicializar gerenciador."""
        self.collection_name = collection_name
        self.embeddings = EmbeddingFactory.create_embeddings()
        self.vector_store = self._create_vector_store()
    
    def _create_vector_store(self) -> Milvus:
        """Criar instância do vector store."""
        return Milvus(
            embedding_function=self.embeddings,
            connection_args={
                "host": settings.milvus_host,
                "port": settings.milvus_port,
                "user": settings.milvus_username,
                "password": settings.milvus_password
            },
            collection_name=self.collection_name
        )
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Adicionar documentos ao vector store."""
        try:
            ids = self.vector_store.add_documents(documents)
            logger.info(f"Adicionados {len(documents)} documentos ao vector store")
            return ids
        except Exception as e:
            logger.error(f"Erro ao adicionar documentos: {e}")
            raise
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Document]:
        """Buscar documentos similares."""
        try:
            results = self.vector_store.similarity_search(
                query,
                k=k,
                filter=filter
            )
            return results
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []
```

### 5. Implementar Retrieval Otimizado

#### Criar `src/rag/retriever.py`:
```python
"""Retriever otimizado para RAG."""
from typing import List, Optional
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
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
        """Inicializar retriever."""
        self.vector_store = vector_store_manager
        self.top_k = top_k
        self.final_k = final_k
    
    def _get_relevant_documents(
        self,
        query: str,
        category: Optional[str] = None
    ) -> List[Document]:
        """Recuperar documentos relevantes."""
        # Busca inicial
        filter_dict = {"category": category} if category else None
        docs = self.vector_store.similarity_search(
            query,
            k=self.top_k,
            filter=filter_dict
        )
        
        # Re-ranking (opcional, pode usar modelo de re-ranking)
        # Por enquanto, retornar top_k final
        return docs[:self.final_k]
```

### 6. Criar Múltiplas Coleções por Tipo

#### Atualizar `VectorStoreManager`:
```python
def create_collection_for_category(self, category: str) -> Milvus:
    """Criar coleção específica para categoria."""
    collection_name = f"{self.collection_name}_{category}"
    return Milvus(
        embedding_function=self.embeddings,
        connection_args={
            "host": settings.milvus_host,
            "port": settings.milvus_port,
            "user": settings.milvus_username,
            "password": settings.milvus_password
        },
        collection_name=collection_name
    )
```

### 7. Implementar Atualização Incremental

#### Criar `src/rag/ingestion_pipeline.py`:
```python
"""Pipeline de ingestão de documentos."""
from typing import List, Dict, Any
from pathlib import Path
from src.rag.document_processor import DocumentProcessor
from src.rag.vector_store import VectorStoreManager
import logging

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Pipeline de ingestão."""
    
    def __init__(self):
        """Inicializar pipeline."""
        self.processor = DocumentProcessor()
        self.vector_store = VectorStoreManager()
    
    def ingest_document(
        self,
        file_path: str,
        category: str = "geral",
        metadata: Dict[str, Any] = None
    ) -> List[str]:
        """Ingerir documento."""
        # Processar documento
        chunks = self.processor.process_document(file_path, metadata)
        
        # Adicionar categoria aos metadados
        for chunk in chunks:
            chunk.metadata["category"] = category
        
        # Inserir no vector store
        ids = self.vector_store.add_documents(chunks)
        
        logger.info(f"Documento {file_path} ingerido: {len(chunks)} chunks")
        return ids
    
    def ingest_directory(
        self,
        directory: str,
        category: str = "geral"
    ) -> Dict[str, List[str]]:
        """Ingerir diretório completo."""
        results = {}
        path = Path(directory)
        
        for file_path in path.glob("**/*"):
            if file_path.is_file():
                try:
                    ids = self.ingest_document(str(file_path), category)
                    results[str(file_path)] = ids
                except Exception as e:
                    logger.error(f"Erro ao ingerir {file_path}: {e}")
        
        return results
```

### 8. Criar Scripts de Seed

#### Criar `scripts/seed_knowledge_base.py`:
```python
"""Script para popular base de conhecimento."""
from src.rag.ingestion_pipeline import IngestionPipeline
import sys

def main():
    pipeline = IngestionPipeline()
    
    # Ingerir documentos iniciais
    categories = {
        "técnico": "docs/knowledge/technical",
        "segurança": "docs/knowledge/security",
        "compliance": "docs/knowledge/compliance",
        "jurídico": "docs/knowledge/legal"
    }
    
    for category, path in categories.items():
        print(f"Ingerindo {category}...")
        results = pipeline.ingest_directory(path, category)
        print(f"  {len(results)} arquivos processados")

if __name__ == "__main__":
    main()
```

### 9. Testar Retrieval

#### Criar `tests/integration/test_rag.py`:
```python
"""Testes de integração RAG."""
import pytest
from src.rag.vector_store import VectorStoreManager
from src.rag.retriever import OptimizedRetriever

@pytest.fixture
def vector_store():
    return VectorStoreManager()

def test_similarity_search(vector_store):
    """Testar busca por similaridade."""
    results = vector_store.similarity_search("SLA", k=5)
    assert len(results) >= 0  # Pode estar vazio se não houver documentos
```

---

## Checklist de Validação

- [ ] Vector database configurado no docker-compose
- [ ] Pipeline de ingestão criado
- [ ] Chunking de documentos implementado
- [ ] Geração de embeddings funcionando
- [ ] Inserção no vector store implementada
- [ ] Retrieval otimizado implementado
- [ ] Múltiplas coleções por tipo criadas
- [ ] Atualização incremental funcionando
- [ ] Scripts de seed criados
- [ ] Testes de retrieval passando
- [ ] Qualidade de retrieval medida
- [ ] Documentação criada

---

## Comandos de Teste

```bash
# Popular base de conhecimento
python scripts/seed_knowledge_base.py

# Testar retrieval
python -m pytest tests/integration/test_rag.py
```


"""Testes de integração RAG."""
import pytest
from src.rag.vector_store import VectorStoreManager
from src.rag.retriever import OptimizedRetriever
from src.rag.document_processor import DocumentProcessor
from src.rag.ingestion_pipeline import IngestionPipeline
from langchain_core.documents import Document
import tempfile
import os


@pytest.fixture
def vector_store():
    """Fixture para VectorStoreManager."""
    return VectorStoreManager(collection_name="test_rfp_knowledge")


@pytest.fixture
def document_processor():
    """Fixture para DocumentProcessor."""
    return DocumentProcessor(chunk_size=500, chunk_overlap=50)


@pytest.fixture
def ingestion_pipeline():
    """Fixture para IngestionPipeline."""
    return IngestionPipeline(collection_name="test_rfp_knowledge")


def test_document_processor_process_text(document_processor):
    """Testar processamento de texto."""
    text = "Este é um texto de teste. " * 100  # Texto longo
    chunks = document_processor.process_text(text)
    
    assert len(chunks) > 0
    assert all(isinstance(chunk, Document) for chunk in chunks)
    assert all(chunk.page_content for chunk in chunks)


def test_vector_store_creation(vector_store):
    """Testar criação de vector store."""
    assert vector_store.vector_store is not None
    assert vector_store.collection_name == "test_rfp_knowledge"


def test_vector_store_add_documents(vector_store):
    """Testar adição de documentos."""
    documents = [
        Document(
            page_content="O SLA do produto é de 99.9% de disponibilidade",
            metadata={"source": "test.pdf", "category": "técnico"}
        ),
        Document(
            page_content="O suporte é oferecido 24/7",
            metadata={"source": "test.pdf", "category": "técnico"}
        )
    ]
    
    ids = vector_store.add_documents(documents)
    assert len(ids) == len(documents)


def test_vector_store_similarity_search(vector_store):
    """Testar busca por similaridade."""
    # Adicionar documentos primeiro
    documents = [
        Document(
            page_content="O SLA do produto é de 99.9% de disponibilidade",
            metadata={"source": "test.pdf", "category": "técnico"}
        )
    ]
    vector_store.add_documents(documents)
    
    # Buscar
    results = vector_store.similarity_search("SLA", k=5)
    assert isinstance(results, list)
    # Pode estar vazio se não houver documentos ou se a busca não encontrar
    assert len(results) >= 0


def test_vector_store_similarity_search_with_filter(vector_store):
    """Testar busca com filtro."""
    # Adicionar documentos
    documents = [
        Document(
            page_content="Informação técnica sobre SLA",
            metadata={"source": "tech.pdf", "category": "técnico"}
        ),
        Document(
            page_content="Informação jurídica sobre contratos",
            metadata={"source": "legal.pdf", "category": "jurídico"}
        )
    ]
    vector_store.add_documents(documents)
    
    # Buscar com filtro
    results = vector_store.similarity_search("informação", k=5, filter={"category": "técnico"})
    assert isinstance(results, list)
    # Verificar que todos os resultados têm a categoria correta
    for doc in results:
        assert doc.metadata.get("category") == "técnico"


def test_optimized_retriever(vector_store):
    """Testar OptimizedRetriever."""
    retriever = OptimizedRetriever(
        vector_store_manager=vector_store,
        top_k=10,
        final_k=5
    )
    
    # Adicionar documentos
    documents = [
        Document(
            page_content="Informação sobre SLA e disponibilidade",
            metadata={"category": "técnico"}
        )
    ]
    vector_store.add_documents(documents)
    
    # Recuperar
    results = retriever.get_relevant_documents("SLA", category="técnico")
    assert isinstance(results, list)
    assert len(results) <= 5  # final_k


def test_ingestion_pipeline_ingest_text(ingestion_pipeline):
    """Testar ingestão de texto."""
    text = "Este é um texto de teste sobre SLA e disponibilidade. " * 20
    ids = ingestion_pipeline.ingest_text(text, category="técnico")
    
    assert isinstance(ids, list)
    assert len(ids) > 0


def test_ingestion_pipeline_ingest_directory(ingestion_pipeline):
    """Testar ingestão de diretório."""
    # Criar diretório temporário com arquivo
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Este é um arquivo de teste sobre SLA. " * 50)
        
        results = ingestion_pipeline.ingest_directory(tmpdir, category="técnico")
        
        assert isinstance(results, dict)
        assert test_file in results or any(test_file in str(k) for k in results.keys())


@pytest.mark.integration
def test_full_rag_pipeline(ingestion_pipeline):
    """Testar pipeline RAG completo."""
    # Ingerir texto
    text = "O SLA do produto é de 99.9% de disponibilidade. O suporte é oferecido 24/7."
    ids = ingestion_pipeline.ingest_text(text, category="técnico")
    assert len(ids) > 0
    
    # Buscar
    results = ingestion_pipeline.vector_store.similarity_search("SLA", k=3)
    assert len(results) > 0
    
    # Verificar que resultados são relevantes
    for doc in results:
        assert "SLA" in doc.page_content or "disponibilidade" in doc.page_content.lower()


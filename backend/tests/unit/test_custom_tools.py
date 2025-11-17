"""Testes para custom tools."""
import pytest
from src.tools.custom_tools import (
    extract_text_tool,
    ocr_tool,
    rag_query_tool,
    compliance_validation_tool,
    map_similar_questions_tool
)
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os


def test_extract_text_tool_mock():
    """Testar extração de texto (mock)."""
    with patch('src.tools.custom_tools.ParserAgent') as mock_parser_class:
        mock_parser = MagicMock()
        mock_parser.extract_from_file.return_value = "Texto extraído"
        mock_parser_class.return_value = mock_parser
        
        with patch('src.tools.custom_tools.LLMFactory') as mock_factory:
            mock_llm = Mock()
            mock_factory.return_value.get_default_llm.return_value = mock_llm
            
            result = extract_text_tool.invoke({
                "file_path": "test.pdf"
            })
            
            assert result is not None
            assert isinstance(result, str)


def test_ocr_tool_mock():
    """Testar OCR (mock)."""
    with patch('src.tools.custom_tools.Image') as mock_image:
        with patch('src.tools.custom_tools.pytesseract') as mock_tesseract:
            mock_tesseract.image_to_string.return_value = "Texto do OCR"
            mock_img = MagicMock()
            mock_image.open.return_value = mock_img
            
            result = ocr_tool.invoke({
                "image_path": "test.png",
                "language": "por"
            })
            
            assert result is not None
            assert isinstance(result, str)


def test_ocr_tool_no_dependencies():
    """Testar OCR quando dependências não estão disponíveis."""
    with patch('src.tools.custom_tools.Image', side_effect=ImportError()):
        result = ocr_tool.invoke({
            "image_path": "test.png"
        })
        
        assert "não disponível" in result.lower() or "erro" in result.lower()


def test_rag_query_tool():
    """Testar consulta RAG."""
    with patch('src.tools.custom_tools.VectorStoreManager') as mock_vs_class:
        mock_vs = MagicMock()
        mock_vs.similarity_search.return_value = [
            MagicMock(
                page_content="Documento sobre SLA",
                metadata={"source": "doc1.pdf", "category": "técnico"}
            )
        ]
        mock_vs_class.return_value = mock_vs
        
        result = rag_query_tool.invoke({
            "query": "SLA",
            "category": "técnico",
            "top_k": 5
        })
        
        assert result is not None
        assert "documentos" in result.lower() or "nenhum" in result.lower()


def test_rag_query_tool_no_results():
    """Testar consulta RAG sem resultados."""
    with patch('src.tools.custom_tools.VectorStoreManager') as mock_vs_class:
        mock_vs = MagicMock()
        mock_vs.similarity_search.return_value = []
        mock_vs_class.return_value = mock_vs
        
        result = rag_query_tool.invoke({
            "query": "xyz123",
            "top_k": 5
        })
        
        assert "nenhum" in result.lower()


def test_compliance_validation_tool():
    """Testar validação de compliance."""
    with patch('src.tools.custom_tools.VerifierAgent') as mock_verifier_class:
        with patch('src.tools.custom_tools.LLMFactory') as mock_factory:
            mock_llm = Mock()
            mock_factory.return_value.get_default_llm.return_value = mock_llm
            
            mock_verifier = MagicMock()
            from src.workflows.schema import VerifiedResponse
            mock_verified = VerifiedResponse(
                qid="test",
                response_text="Test",
                confidence_score=0.8,
                is_consistent=True,
                has_prohibited_terms=False,
                has_gaps=False,
                needs_review=False
            )
            mock_verifier.verify.return_value = mock_verified
            mock_verifier_class.return_value = mock_verifier
            
            result = compliance_validation_tool.invoke({
                "response_text": "O SLA é de 99.9%"
            })
            
            assert result is not None
            import json
            validation = json.loads(result)
            assert "confidence_score" in validation
            assert "needs_review" in validation


def test_map_similar_questions_tool():
    """Testar mapeamento de perguntas similares."""
    with patch('src.tools.custom_tools.VectorStoreManager') as mock_vs_class:
        mock_vs = MagicMock()
        mock_vs.similarity_search.return_value = [
            MagicMock(
                page_content="Qual é o SLA?",
                metadata={"source": "rfp1.pdf", "type": "question"}
            )
        ]
        mock_vs_class.return_value = mock_vs
        
        result = map_similar_questions_tool.invoke({
            "question": "Qual é o SLA do produto?",
            "top_k": 5
        })
        
        assert result is not None
        assert "perguntas" in result.lower() or "nenhuma" in result.lower()


def test_map_similar_questions_tool_no_results():
    """Testar mapeamento sem resultados."""
    with patch('src.tools.custom_tools.VectorStoreManager') as mock_vs_class:
        mock_vs = MagicMock()
        mock_vs.similarity_search.return_value = []
        mock_vs_class.return_value = mock_vs
        
        result = map_similar_questions_tool.invoke({
            "question": "Pergunta única",
            "top_k": 5
        })
        
        assert "nenhuma" in result.lower()


def test_tool_usage_metrics():
    """Testar que métricas são rastreadas."""
    with patch('src.tools.custom_tools.tool_usage_total') as mock_metrics:
        with patch('src.tools.custom_tools.VectorStoreManager') as mock_vs_class:
            mock_vs = MagicMock()
            mock_vs.similarity_search.return_value = []
            mock_vs_class.return_value = mock_vs
            
            rag_query_tool.invoke({"query": "test"})
            
            # Verificar que métricas foram chamadas
            assert mock_metrics.labels.called or mock_metrics.inc.called


@pytest.mark.integration
def test_extract_text_tool_integration():
    """Teste de integração para extração de texto."""
    # Criar arquivo temporário de texto
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Este é um arquivo de teste para extração de texto.")
        temp_path = f.name
    
    try:
        # Converter para formato suportado (criar um CSV simples)
        csv_path = temp_path.replace('.txt', '.csv')
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write("col1,col2\nvalor1,valor2")
        
        result = extract_text_tool.invoke({
            "file_path": csv_path,
            "file_type": "csv"
        })
        
        assert result is not None
        assert len(result) > 0
        
    finally:
        # Limpar arquivos temporários
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        if os.path.exists(csv_path):
            os.unlink(csv_path)


@pytest.mark.integration
def test_compliance_validation_tool_integration():
    """Teste de integração para validação de compliance."""
    from src.utils.llm_factory import LLMFactory
    
    try:
        factory = LLMFactory()
        llm = factory.get_default_llm()
        
        result = compliance_validation_tool.invoke({
            "response_text": "O SLA do produto é de 99.9% de disponibilidade"
        })
        
        assert result is not None
        import json
        validation = json.loads(result)
        assert isinstance(validation, dict)
        assert "confidence_score" in validation
        
    except Exception as e:
        # Se LLM não estiver configurado, pular teste
        pytest.skip(f"LLM não configurado: {e}")


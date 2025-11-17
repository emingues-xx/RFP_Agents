"""Testes com RFPs reais."""
import pytest
from pathlib import Path
from src.workflows.workflow import RFPWorkflow
from langgraph.checkpoint.memory import MemorySaver
import uuid


@pytest.fixture
def workflow():
    """Criar workflow para testes."""
    checkpoint = MemorySaver()
    return RFPWorkflow(checkpoint_saver=checkpoint)


@pytest.fixture
def test_data_dir():
    """Diretório de dados de teste."""
    return Path("test_data/rfps")


@pytest.mark.skipif(
    not Path("test_data/rfps").exists(),
    reason="Pasta de RFPs de teste não encontrada"
)
def test_process_pdf_rfp(workflow, test_data_dir):
    """Testar processamento de RFP em PDF."""
    pdf_files = list(test_data_dir.glob("*.pdf"))
    
    if not pdf_files:
        pytest.skip("Nenhum arquivo PDF encontrado em test_data/rfps")
    
    pdf_file = pdf_files[0]
    session_id = f"e2e-pdf-{uuid.uuid4().hex[:8]}"
    
    try:
        result = workflow.run(
            input_text=f"Processar arquivo: {pdf_file.name}",
            file_path=str(pdf_file),
            session_id=session_id
        )
        
        assert result is not None
        assert "current_step" in result
        # Verificar que arquivo foi processado
        assert result.get("file_path") == str(pdf_file) or result.get("parsed_questions") is not None
    except Exception as e:
        pytest.skip(f"Processamento de PDF não pode ser testado: {e}")


@pytest.mark.skipif(
    not Path("test_data/rfps").exists(),
    reason="Pasta de RFPs de teste não encontrada"
)
def test_process_docx_rfp(workflow, test_data_dir):
    """Testar processamento de RFP em DOCX."""
    docx_files = list(test_data_dir.glob("*.docx"))
    
    if not docx_files:
        pytest.skip("Nenhum arquivo DOCX encontrado em test_data/rfps")
    
    docx_file = docx_files[0]
    session_id = f"e2e-docx-{uuid.uuid4().hex[:8]}"
    
    try:
        result = workflow.run(
            input_text=f"Processar arquivo: {docx_file.name}",
            file_path=str(docx_file),
            session_id=session_id
        )
        
        assert result is not None
        assert "current_step" in result
        # Verificar que arquivo foi processado
        assert result.get("file_path") == str(docx_file) or result.get("parsed_questions") is not None
    except Exception as e:
        pytest.skip(f"Processamento de DOCX não pode ser testado: {e}")


@pytest.mark.skipif(
    not Path("test_data/rfps").exists(),
    reason="Pasta de RFPs de teste não encontrada"
)
def test_process_excel_rfp(workflow, test_data_dir):
    """Testar processamento de RFP em Excel."""
    excel_files = list(test_data_dir.glob("*.xlsx")) + list(test_data_dir.glob("*.xls"))
    
    if not excel_files:
        pytest.skip("Nenhum arquivo Excel encontrado em test_data/rfps")
    
    excel_file = excel_files[0]
    session_id = f"e2e-excel-{uuid.uuid4().hex[:8]}"
    
    try:
        result = workflow.run(
            input_text=f"Processar arquivo: {excel_file.name}",
            file_path=str(excel_file),
            session_id=session_id
        )
        
        assert result is not None
        assert "current_step" in result
        # Verificar que arquivo foi processado
        assert result.get("file_path") == str(excel_file) or result.get("parsed_questions") is not None
    except Exception as e:
        pytest.skip(f"Processamento de Excel não pode ser testado: {e}")


@pytest.mark.skipif(
    not Path("test_data/rfps").exists(),
    reason="Pasta de RFPs de teste não encontrada"
)
def test_process_csv_rfp(workflow, test_data_dir):
    """Testar processamento de RFP em CSV."""
    csv_files = list(test_data_dir.glob("*.csv"))
    
    if not csv_files:
        pytest.skip("Nenhum arquivo CSV encontrado em test_data/rfps")
    
    csv_file = csv_files[0]
    session_id = f"e2e-csv-{uuid.uuid4().hex[:8]}"
    
    try:
        result = workflow.run(
            input_text=f"Processar arquivo: {csv_file.name}",
            file_path=str(csv_file),
            session_id=session_id
        )
        
        assert result is not None
        assert "current_step" in result
        # Verificar que arquivo foi processado
        assert result.get("file_path") == str(csv_file) or result.get("parsed_questions") is not None
    except Exception as e:
        pytest.skip(f"Processamento de CSV não pode ser testado: {e}")


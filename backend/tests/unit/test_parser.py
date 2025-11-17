"""Testes para Agente Parser."""
import pytest
from src.agents.parser import ParserAgent
from src.workflows.schema import ParsedQuestion
from unittest.mock import Mock, MagicMock, patch
from langchain_core.messages import AIMessage
import json
import tempfile
from pathlib import Path


@pytest.fixture
def mock_llm():
    """Mock do LLM."""
    llm = Mock()
    
    def mock_invoke(messages):
        # Simular resposta JSON do LLM
        response_data = [
            {
                "qid": "Q001",
                "category": "técnico",
                "question_text": "Qual é o SLA do produto?",
                "requirements": ["SLA", "disponibilidade"],
                "expected_format": "texto"
            },
            {
                "qid": "Q002",
                "category": "comercial",
                "question_text": "Qual é o preço?",
                "requirements": ["preço"],
                "expected_format": "número"
            }
        ]
        return AIMessage(content=json.dumps(response_data))
    
    llm.invoke = Mock(side_effect=mock_invoke)
    return llm


@pytest.fixture
def parser_agent(mock_llm):
    """Fixture para ParserAgent."""
    return ParserAgent(llm=mock_llm)


def test_extract_from_docx(parser_agent):
    """Testar extração de DOCX."""
    # Criar arquivo DOCX temporário de teste
    # Por enquanto, apenas verificar que o método existe
    assert hasattr(parser_agent, 'extract_from_docx')


def test_extract_from_csv(parser_agent):
    """Testar extração de CSV."""
    # Criar CSV temporário
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("Pergunta,Resposta\n")
        f.write("Qual é o SLA?,99.9%\n")
        f.write("Qual é o preço?,R$ 1000\n")
        temp_path = f.name
    
    try:
        text = parser_agent.extract_from_csv(temp_path)
        assert "SLA" in text or "preço" in text
    finally:
        Path(temp_path).unlink()


def test_normalize_questions(parser_agent):
    """Testar normalização."""
    raw_text = """
    Pergunta 1: Qual é o SLA do produto?
    Pergunta 2: Qual é o preço?
    """
    
    questions = parser_agent.normalize_questions(raw_text)
    
    assert len(questions) > 0
    assert all(isinstance(q, ParsedQuestion) for q in questions)
    assert all(q.qid for q in questions)
    assert all(q.category for q in questions)
    assert all(q.question_text for q in questions)


def test_normalize_questions_empty_text(parser_agent):
    """Testar normalização com texto vazio."""
    questions = parser_agent.normalize_questions("")
    # Deve retornar lista vazia ou tratar erro graciosamente
    assert isinstance(questions, list)


def test_map_to_historical(parser_agent):
    """Testar mapeamento para histórico."""
    questions = [
        ParsedQuestion(
            qid="Q001",
            category="técnico",
            question_text="Qual é o SLA?",
            requirements=["SLA"],
            expected_format="texto"
        )
    ]
    
    mapped = parser_agent.map_to_historical(questions)
    
    assert len(mapped) == 1
    assert mapped[0]["qid"] == "Q001"
    assert "mapping_confidence" in mapped[0]


def test_extract_from_file_pdf(parser_agent):
    """Testar extração de arquivo PDF."""
    # Por enquanto, apenas verificar que o método existe
    assert hasattr(parser_agent, 'extract_from_file')


def test_extract_from_file_docx(parser_agent):
    """Testar extração de arquivo DOCX."""
    # Por enquanto, apenas verificar que o método existe
    assert hasattr(parser_agent, 'extract_from_file')


def test_process_with_text(parser_agent):
    """Testar processamento com texto."""
    input_text = "Pergunta 1: Qual é o SLA?\nPergunta 2: Qual é o preço?"
    
    questions = parser_agent.process(input_text)
    
    assert isinstance(questions, list)
    assert len(questions) > 0


def test_process_with_file(parser_agent):
    """Testar processamento com arquivo."""
    # Criar CSV temporário
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("Pergunta\n")
        f.write("Qual é o SLA?\n")
        temp_path = f.name
    
    try:
        questions = parser_agent.process("", file_path=temp_path)
        assert isinstance(questions, list)
    finally:
        Path(temp_path).unlink()


@patch('src.agents.parser.OCR_AVAILABLE', False)
def test_extract_from_pdf_no_ocr(parser_agent):
    """Testar extração de PDF sem OCR disponível."""
    # Verificar que não quebra quando OCR não está disponível
    assert hasattr(parser_agent, 'extract_from_pdf')


def test_parser_agent_initialization(parser_agent):
    """Testar inicialização do ParserAgent."""
    assert parser_agent.llm is not None
    assert parser_agent.system_prompt is not None
    assert "Parser" in parser_agent.system_prompt


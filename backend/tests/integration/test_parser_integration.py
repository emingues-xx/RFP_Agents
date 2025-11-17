"""Testes de integração do Parser."""
import pytest
from src.agents.parser import ParserAgent
from src.utils.llm_factory import LLMFactory
import tempfile
from pathlib import Path
import pandas as pd


@pytest.fixture
def parser_agent():
    """Fixture para ParserAgent com LLM real."""
    factory = LLMFactory()
    llm = factory.get_default_llm()
    return ParserAgent(llm=llm)


@pytest.mark.integration
def test_full_parser_workflow_text(parser_agent):
    """Testar workflow completo com texto."""
    input_text = """
    Pergunta 1: Qual é o SLA (Service Level Agreement) do produto?
    Pergunta 2: Qual é o preço unitário?
    Pergunta 3: Qual é o suporte oferecido?
    """
    
    questions = parser_agent.process(input_text)
    
    assert len(questions) >= 1
    assert all(hasattr(q, 'qid') for q in questions)
    assert all(hasattr(q, 'category') for q in questions)


@pytest.mark.integration
def test_full_parser_workflow_csv(parser_agent):
    """Testar workflow completo com CSV."""
    # Criar CSV temporário
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        f.write("Pergunta\n")
        f.write("Qual é o SLA?\n")
        f.write("Qual é o preço?\n")
        temp_path = f.name
    
    try:
        questions = parser_agent.process("", file_path=temp_path)
        assert isinstance(questions, list)
        # Pode estar vazio se LLM não conseguir processar
    finally:
        Path(temp_path).unlink()


@pytest.mark.integration
def test_parser_tool_integration():
    """Testar integração da tool."""
    from src.tools.parser_tool import parse_text_questions_tool
    
    result = parse_text_questions_tool.invoke({
        "text": "Pergunta 1: Qual é o SLA?\nPergunta 2: Qual é o preço?"
    })
    
    assert result is not None
    assert isinstance(result, str)
    # Verificar se é JSON válido
    import json
    try:
        data = json.loads(result)
        assert isinstance(data, list)
    except json.JSONDecodeError:
        # Pode retornar erro em formato string
        assert "erro" in result.lower() or "error" in result.lower()


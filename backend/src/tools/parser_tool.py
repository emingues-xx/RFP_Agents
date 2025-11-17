"""Tool do LangChain para Parser Agent."""
from langchain_core.tools import tool
from typing import Optional
from src.agents.parser import ParserAgent
from src.utils.llm_factory import LLMFactory
import logging

logger = logging.getLogger(__name__)

# Instância global do parser (lazy initialization)
_parser_agent: Optional[ParserAgent] = None


def _get_parser_agent() -> ParserAgent:
    """Obter instância do ParserAgent (singleton)."""
    global _parser_agent
    if _parser_agent is None:
        factory = LLMFactory()
        llm = factory.get_default_llm()
        _parser_agent = ParserAgent(llm=llm)
    return _parser_agent


@tool
def parse_questionnaire_tool(file_path: str, use_ocr: bool = False) -> str:
    """Extrair e normalizar perguntas de questionário a partir de arquivo.
    
    Args:
        file_path: Caminho do arquivo (PDF, DOCX, Excel, CSV)
        use_ocr: Se True, usa OCR para PDFs escaneados (mais lento)
    
    Returns:
        JSON string com perguntas normalizadas
    """
    try:
        parser = _get_parser_agent()
        parsed_questions = parser.process(input_data="", file_path=file_path)
        
        # Converter para JSON string
        import json
        questions_dict = [q.model_dump() for q in parsed_questions]
        return json.dumps(questions_dict, indent=2, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Erro na tool parse_questionnaire: {e}")
        return f"Erro ao processar arquivo: {str(e)}"


@tool
def parse_text_questions_tool(text: str) -> str:
    """Extrair e normalizar perguntas a partir de texto.
    
    Args:
        text: Texto contendo perguntas
    
    Returns:
        JSON string com perguntas normalizadas
    """
    try:
        parser = _get_parser_agent()
        parsed_questions = parser.process(input_data=text)
        
        # Converter para JSON string
        import json
        questions_dict = [q.model_dump() for q in parsed_questions]
        return json.dumps(questions_dict, indent=2, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Erro na tool parse_text_questions: {e}")
        return f"Erro ao processar texto: {str(e)}"


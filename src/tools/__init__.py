"""Ferramentas customizadas para os agentes"""
from src.tools.parser_tool import (
    parse_questionnaire_tool,
    parse_text_questions_tool
)
from src.tools.knowledge_tool import (
    knowledge_query_tool
)
from src.tools.verifier_tool import (
    verify_response_tool
)
from src.tools.custom_tools import (
    extract_text_tool,
    ocr_tool,
    rag_query_tool,
    compliance_validation_tool,
    map_similar_questions_tool
)

__all__ = [
    "parse_questionnaire_tool",
    "parse_text_questions_tool",
    "knowledge_query_tool",
    "verify_response_tool",
    "extract_text_tool",
    "ocr_tool",
    "rag_query_tool",
    "compliance_validation_tool",
    "map_similar_questions_tool"
]

# Lista de todas as tools
ALL_TOOLS = [
    parse_questionnaire_tool,
    parse_text_questions_tool,
    knowledge_query_tool,
    verify_response_tool,
    extract_text_tool,
    ocr_tool,
    rag_query_tool,
    compliance_validation_tool,
    map_similar_questions_tool
]
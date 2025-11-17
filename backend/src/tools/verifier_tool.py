"""Tool do LangChain para Verifier Agent."""
from langchain_core.tools import tool
from typing import Optional
from src.agents.verifier import VerifierAgent
from src.workflows.schema import GeneratedResponse
from src.utils.llm_factory import LLMFactory
import json
import logging

logger = logging.getLogger(__name__)

# Instância global do verifier agent (lazy initialization)
_verifier_agent: Optional[VerifierAgent] = None


def _get_verifier_agent() -> VerifierAgent:
    """Obter instância do VerifierAgent (singleton)."""
    global _verifier_agent
    if _verifier_agent is None:
        factory = LLMFactory()
        llm = factory.get_default_llm()
        _verifier_agent = VerifierAgent(llm=llm)
    return _verifier_agent


@tool
def verify_response_tool(question: str, response: str, qid: Optional[str] = None) -> str:
    """Verificar qualidade e compliance de resposta.
    
    Args:
        question: Pergunta original
        response: Texto da resposta a ser verificada
        qid: ID opcional da pergunta
    
    Returns:
        JSON string com resultado da verificação
    """
    try:
        agent = _get_verifier_agent()
        
        # Criar GeneratedResponse temporário para verificação
        generated_response = GeneratedResponse(
            qid=qid or "unknown",
            response_text=response,
            confidence_score=0.8  # Score padrão, será recalculado
        )
        
        verified = agent.verify(
            question=question,
            response=generated_response,
            expected_format=None
        )
        
        # Converter para JSON string
        return json.dumps(verified.model_dump(), indent=2, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Erro na tool verify_response: {e}")
        return json.dumps({
            "error": f"Erro ao verificar resposta: {str(e)}",
            "qid": qid or "unknown"
        }, indent=2)


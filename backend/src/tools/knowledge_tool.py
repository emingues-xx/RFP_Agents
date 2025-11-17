"""Tool do LangChain para Knowledge Agent."""
from langchain_core.tools import tool
from typing import Optional
from src.agents.knowledge import KnowledgeAgent
from src.utils.llm_factory import LLMFactory
import logging

logger = logging.getLogger(__name__)

# Instância global do knowledge agent (lazy initialization)
_knowledge_agent: Optional[KnowledgeAgent] = None


def _get_knowledge_agent(vector_store=None) -> KnowledgeAgent:
    """Obter instância do KnowledgeAgent (singleton)."""
    global _knowledge_agent
    if _knowledge_agent is None:
        factory = LLMFactory()
        llm = factory.get_default_llm()
        _knowledge_agent = KnowledgeAgent(llm=llm, vector_store=vector_store)
    return _knowledge_agent


@tool
def knowledge_query_tool(question: str, category: Optional[str] = None) -> str:
    """Consultar base de conhecimento e gerar resposta.
    
    Args:
        question: Pergunta a ser respondida
        category: Categoria opcional (técnico, segurança, compliance, jurídico)
    
    Returns:
        JSON string com resposta gerada
    """
    try:
        agent = _get_knowledge_agent()
        response = agent.generate_response(
            question=question,
            context={"category": category} if category else None
        )
        
        # Converter para JSON string
        import json
        return json.dumps(response.model_dump(), indent=2, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Erro na tool knowledge_query: {e}")
        return f"Erro ao consultar conhecimento: {str(e)}"


"""Tratamento de erros entre agentes."""
from typing import Dict, Any, Optional
import logging
import traceback

logger = logging.getLogger(__name__)


class AgentErrorHandler:
    """Gerenciador de erros entre agentes."""
    
    # Agentes críticos que devem parar o workflow
    CRITICAL_AGENTS = {"orchestrator"}
    
    # Agentes que podem ter fallback
    FALLBACK_AGENTS = {"parser", "knowledge", "verifier"}
    
    @staticmethod
    def handle_agent_error(
        agent_name: str,
        error: Exception,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Tratar erro de agente."""
        logger.error(f"Erro no agente {agent_name}: {error}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        
        if "errors" not in state:
            state["errors"] = []
        
        error_info = {
            "agent": agent_name,
            "error": str(error),
            "type": type(error).__name__,
            "traceback": traceback.format_exc()
        }
        state["errors"].append(error_info)
        
        # Decidir se deve continuar ou parar
        if agent_name in AgentErrorHandler.CRITICAL_AGENTS:
            logger.error(f"Agente crítico {agent_name} falhou, parando workflow")
            state["current_step"] = "error"
        elif agent_name in AgentErrorHandler.FALLBACK_AGENTS:
            # Outros agentes podem ter fallback
            logger.warning(f"Agente {agent_name} falhou, marcando como erro mas continuando")
            state["current_step"] = f"{agent_name}_error"
        else:
            # Agente desconhecido, tratar como erro crítico
            logger.error(f"Agente desconhecido {agent_name} falhou")
            state["current_step"] = "error"
        
        return state
    
    @staticmethod
    def can_continue_after_error(agent_name: str) -> bool:
        """Verificar se workflow pode continuar após erro."""
        return agent_name not in AgentErrorHandler.CRITICAL_AGENTS
    
    @staticmethod
    def get_error_summary(state: Dict[str, Any]) -> Dict[str, Any]:
        """Obter resumo de erros do estado."""
        errors = state.get("errors", [])
        
        if not errors:
            return {"has_errors": False, "errors": []}
        
        summary = {
            "has_errors": True,
            "total_errors": len(errors),
            "errors_by_agent": {},
            "errors_by_type": {},
            "errors": errors
        }
        
        for error in errors:
            agent = error.get("agent", "unknown")
            error_type = error.get("type", "unknown")
            
            summary["errors_by_agent"][agent] = summary["errors_by_agent"].get(agent, 0) + 1
            summary["errors_by_type"][error_type] = summary["errors_by_type"].get(error_type, 0) + 1
        
        return summary


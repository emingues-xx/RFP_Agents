"""Workflow principal usando LangGraph."""
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver
from src.workflows.state import WorkflowState
from src.workflows.nodes import (
    entry_node, orchestrator_node, exit_node,
    parser_node, knowledge_node, verifier_node
)
from src.workflows.edges import route_after_orchestrator, route_after_verification
from src.agents.orchestrator import OrchestratorAgent
from src.agents.parser import ParserAgent
from src.agents.knowledge import KnowledgeAgent
from src.agents.verifier import VerifierAgent
from src.utils.llm_factory import LLMFactory
from src.workflows.checkpoint import create_checkpoint_saver
from src.utils.metrics import (
    agent_executions_total,
    agent_execution_duration_seconds
)
import time
import logging

logger = logging.getLogger(__name__)


class RFPWorkflow:
    """Workflow principal para processamento de RFPs."""
    
    def __init__(self, checkpoint_saver: Optional[BaseCheckpointSaver] = None):
        """Inicializar workflow."""
        self.checkpoint_saver = checkpoint_saver or create_checkpoint_saver()
        self.graph = self._build_graph()
        self.app = self.graph.compile(checkpointer=self.checkpoint_saver)
        logger.info("RFPWorkflow inicializado")
    
    def _build_graph(self) -> StateGraph:
        """Construir grafo do workflow."""
        # Criar factory e agentes
        factory = LLMFactory()
        llm = factory.get_default_llm(session_id="workflow-init")
        
        orchestrator = OrchestratorAgent(
            llm=llm,
            session_id="workflow-init"
        )
        parser_agent = ParserAgent(llm=llm)
        knowledge_agent = KnowledgeAgent(llm=llm)
        verifier_agent = VerifierAgent(llm=llm)
        
        # Criar grafo
        workflow = StateGraph(WorkflowState)
        
        # Adicionar nodes
        workflow.add_node("entry", entry_node)
        workflow.add_node("orchestrator", lambda state: orchestrator_node(state, orchestrator))
        workflow.add_node("parser", lambda state: parser_node(state, parser_agent))
        workflow.add_node("knowledge", lambda state: knowledge_node(state, knowledge_agent))
        workflow.add_node("verifier", lambda state: verifier_node(state, verifier_agent))
        workflow.add_node("exit", exit_node)
        
        # Adicionar edges
        workflow.set_entry_point("entry")
        workflow.add_edge("entry", "orchestrator")
        workflow.add_conditional_edges(
            "orchestrator",
            route_after_orchestrator,
            {
                "single_question": "knowledge",
                "questionnaire": "parser",
                "error": "exit"
            }
        )
        workflow.add_edge("parser", "knowledge")
        workflow.add_edge("knowledge", "verifier")
        workflow.add_conditional_edges(
            "verifier",
            route_after_verification,
            {
                "approval": "exit",
                "error": "exit"
            }
        )
        workflow.add_edge("exit", END)
        
        logger.info("Grafo do workflow construído com todos os agentes integrados")
        return workflow
    
    def run(self, input_text: str, session_id: str, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Executar workflow com métricas."""
        start_time = time.time()
        
        initial_state: WorkflowState = {
            "input_text": input_text,
            "input_type": None,
            "file_path": None,
            "context": {},
            "messages": [],
            "parsed_questions": None,
            "generated_responses": None,
            "verified_responses": None,
            "session_id": session_id,
            "workflow_id": f"wf-{session_id}",
            "current_step": "entry",
            "errors": [],
            "requires_approval": False,
            "approval_status": None,
            "coordination_plan": None
        }
        
        config = config or {}
        config["configurable"] = {"thread_id": session_id}
        
        try:
            logger.info(f"Iniciando workflow para sessão: {session_id}")
            result = self.app.invoke(initial_state, config=config)
            
            # Coletar métricas
            duration = time.time() - start_time
            agent_executions_total.labels(
                agent_name="workflow",
                status="success"
            ).inc()
            agent_execution_duration_seconds.labels(
                agent_name="workflow"
            ).observe(duration)
            
            logger.info(f"Workflow concluído em {duration:.2f}s")
            return result
            
        except Exception as e:
            # Métricas de erro
            duration = time.time() - start_time
            agent_executions_total.labels(
                agent_name="workflow",
                status="error"
            ).inc()
            agent_execution_duration_seconds.labels(
                agent_name="workflow"
            ).observe(duration)
            
            logger.error(f"Erro ao executar workflow: {e}")
            raise


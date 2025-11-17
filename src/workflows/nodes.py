"""Nodes do workflow LangGraph."""
from typing import Dict, Any
from src.workflows.state import WorkflowState
from src.agents.orchestrator import OrchestratorAgent
from src.agents.parser import ParserAgent
from src.agents.knowledge import KnowledgeAgent
from src.agents.verifier import VerifierAgent
from src.agents.error_handler import AgentErrorHandler
from src.workflows.schema import GeneratedResponse
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)


def entry_node(state: WorkflowState) -> WorkflowState:
    """Node de entrada do workflow."""
    logger.info(f"Workflow iniciado: {state['workflow_id']}")
    state["current_step"] = "entry"
    return state


def orchestrator_node(state: WorkflowState, orchestrator: OrchestratorAgent) -> WorkflowState:
    """Node do Agente Orquestrador."""
    logger.info("Executando Agente Orquestrador")
    
    try:
        # Identificar tipo de input
        input_type = orchestrator.identify_input_type(state["input_text"])
        state["input_type"] = input_type.type
        
        # Coletar contexto
        context = orchestrator.collect_context(state["input_text"])
        state["context"] = context.model_dump()
        
        # Coordenar próximos passos
        coordination_plan = orchestrator.coordinate_agents(
            input_type,
            context,
            state["input_text"]
        )
        state["coordination_plan"] = coordination_plan
        
        state["current_step"] = "orchestrator_complete"
        logger.info(f"Orquestração completa: {state['input_type']}")
        
    except Exception as e:
        logger.error(f"Erro no Agente Orquestrador: {e}")
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Orchestrator error: {str(e)}")
        state["current_step"] = "error"
    
    return state


def parser_node(
    state: WorkflowState,
    parser_agent: ParserAgent
) -> WorkflowState:
    """Node do Agente Parser."""
    workflow_id = state.get("workflow_id", "unknown")
    logger.info(f"[A2A] Parser iniciado para workflow {workflow_id}")
    
    try:
        input_data = state.get("input_text") or state.get("file_path")
        if not input_data:
            raise ValueError("Input data não encontrado")
        
        # Extrair e normalizar perguntas
        if state.get("file_path"):
            logger.debug(f"Extraindo texto de arquivo: {state['file_path']}")
            raw_text = parser_agent.extract_from_file(state["file_path"])
        else:
            raw_text = input_data
        
        logger.debug(f"Normalizando perguntas do texto ({len(raw_text)} caracteres)")
        parsed_questions = parser_agent.normalize_questions(raw_text)
        state["parsed_questions"] = [q.model_dump() for q in parsed_questions]
        
        # Mapear para histórico
        mapped = parser_agent.map_to_historical(parsed_questions)
        
        # Garantir que coordination_plan existe
        if "coordination_plan" not in state or state["coordination_plan"] is None:
            state["coordination_plan"] = {}
        state["coordination_plan"]["parser_results"] = mapped
        
        state["current_step"] = "parser_complete"
        logger.info(f"[A2A] Parser concluído, enviando {len(parsed_questions)} perguntas para Knowledge")
        
    except Exception as e:
        logger.error(f"Erro no Agente Parser: {e}")
        state = AgentErrorHandler.handle_agent_error("parser", e, state)
    
    return state


def knowledge_node(
    state: WorkflowState,
    knowledge_agent: KnowledgeAgent
) -> WorkflowState:
    """Node do Agente Conhecimento."""
    workflow_id = state.get("workflow_id", "unknown")
    logger.info(f"[A2A] Knowledge iniciado para workflow {workflow_id}")
    
    try:
        responses = []
        
        # Se tem perguntas parseadas, processar todas
        if state.get("parsed_questions"):
            logger.debug(f"Processando {len(state['parsed_questions'])} perguntas parseadas")
            for q_data in state["parsed_questions"]:
                question = q_data.get("question_text", "")
                qid = q_data.get("qid", "")
                category = q_data.get("category", "")
                
                context = state.get("context", {})
                if category:
                    context["category"] = category
                
                logger.debug(f"Gerando resposta para {qid}: {question[:50]}...")
                response = knowledge_agent.generate_response(
                    question=question,
                    context=context,
                    qid=qid
                )
                responses.append(response.model_dump())
        else:
            # Pergunta única
            question = state.get("input_text", "")
            logger.debug(f"Gerando resposta para pergunta única: {question[:50]}...")
            response = knowledge_agent.generate_response(
                question=question,
                context=state.get("context", {})
            )
            responses.append(response.model_dump())
        
        state["generated_responses"] = responses
        state["current_step"] = "knowledge_complete"
        logger.info(f"[A2A] Knowledge concluído, enviando {len(responses)} respostas para Verifier")
        
    except Exception as e:
        logger.error(f"Erro no Agente Conhecimento: {e}")
        state = AgentErrorHandler.handle_agent_error("knowledge", e, state)
    
    return state


def verifier_node(
    state: WorkflowState,
    verifier_agent: VerifierAgent
) -> WorkflowState:
    """Node do Agente Verificador."""
    workflow_id = state.get("workflow_id", "unknown")
    logger.info(f"[A2A] Verifier iniciado para workflow {workflow_id}")
    
    try:
        verified_responses = []
        generated_responses = state.get("generated_responses", [])
        parsed_questions = state.get("parsed_questions", [])
        
        if not generated_responses:
            logger.warning("Nenhuma resposta gerada para verificar")
            state["verified_responses"] = []
            state["current_step"] = "verifier_complete"
            return state
        
        # Criar mapeamento QID -> pergunta
        question_map = {q.get("qid"): q.get("question_text", "") for q in parsed_questions}
        
        # Converter todas as respostas para GeneratedResponse
        all_responses = [GeneratedResponse(**r) for r in generated_responses]
        
        logger.debug(f"Verificando {len(generated_responses)} respostas")
        for resp_data in generated_responses:
            response = GeneratedResponse(**resp_data)
            question = question_map.get(response.qid, state.get("input_text", ""))
            
            # Obter expected_format se disponível
            expected_format = None
            for q_data in parsed_questions:
                if q_data.get("qid") == response.qid:
                    expected_format = q_data.get("expected_format")
                    break
            
            verified = verifier_agent.verify(
                question=question,
                response=response,
                all_responses=all_responses,
                expected_format=expected_format
            )
            verified_responses.append(verified.model_dump())
        
        state["verified_responses"] = verified_responses
        state["current_step"] = "verifier_complete"
        logger.info(f"[A2A] Verifier concluído: {len(verified_responses)} respostas verificadas")
        
    except Exception as e:
        logger.error(f"Erro no Agente Verificador: {e}")
        state = AgentErrorHandler.handle_agent_error("verifier", e, state)
    
    return state


def exit_node(state: WorkflowState) -> WorkflowState:
    """Node de saída do workflow."""
    workflow_id = state.get("workflow_id", "unknown")
    logger.info(f"[A2A] Workflow finalizado: {workflow_id}")
    state["current_step"] = "completed"
    return state


# Wrappers com retry logic
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def parser_node_with_retry(state: WorkflowState, parser_agent: ParserAgent) -> WorkflowState:
    """Parser node com retry."""
    return parser_node(state, parser_agent)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def knowledge_node_with_retry(state: WorkflowState, knowledge_agent: KnowledgeAgent) -> WorkflowState:
    """Knowledge node com retry."""
    return knowledge_node(state, knowledge_agent)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def verifier_node_with_retry(state: WorkflowState, verifier_agent: VerifierAgent) -> WorkflowState:
    """Verifier node com retry."""
    return verifier_node(state, verifier_agent)


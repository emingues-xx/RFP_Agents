# Tarefa 3.4: Integração entre Agentes

## Objetivo
Integrar todos os agentes especialistas no LangGraph StateGraph e implementar comunicação A2A (Agent-to-Agent).

## Prioridade
Alta

## Estimativa
3 dias

## Responsável
Backend

---

## Instruções de Implementação

### 1. Integrar Agentes no LangGraph StateGraph

#### Atualizar `src/workflows/nodes.py`:
```python
from src.agents.parser import ParserAgent
from src.agents.knowledge import KnowledgeAgent
from src.agents.verifier import VerifierAgent

def parser_node(
    state: WorkflowState,
    parser_agent: ParserAgent
) -> WorkflowState:
    """Node do Agente Parser."""
    logger.info("Executando Agente Parser")
    
    try:
        input_data = state.get("input_text") or state.get("file_path")
        if not input_data:
            raise ValueError("Input data não encontrado")
        
        # Extrair e normalizar perguntas
        if state.get("file_path"):
            raw_text = parser_agent.extract_from_file(state["file_path"])
        else:
            raw_text = input_data
        
        parsed_questions = parser_agent.normalize_questions(raw_text)
        state["parsed_questions"] = [q.model_dump() for q in parsed_questions]
        
        # Mapear para histórico
        mapped = parser_agent.map_to_historical(parsed_questions)
        state["coordination_plan"]["parser_results"] = mapped
        
        state["current_step"] = "parser_complete"
        logger.info(f"Parser completo: {len(parsed_questions)} perguntas processadas")
        
    except Exception as e:
        logger.error(f"Erro no Agente Parser: {e}")
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Parser error: {str(e)}")
        state["current_step"] = "error"
    
    return state


def knowledge_node(
    state: WorkflowState,
    knowledge_agent: KnowledgeAgent
) -> WorkflowState:
    """Node do Agente Conhecimento."""
    logger.info("Executando Agente Conhecimento")
    
    try:
        responses = []
        
        # Se tem perguntas parseadas, processar todas
        if state.get("parsed_questions"):
            for q_data in state["parsed_questions"]:
                question = q_data.get("question_text", "")
                qid = q_data.get("qid", "")
                category = q_data.get("category", "")
                
                response = knowledge_agent.generate_response(
                    question=question,
                    context=state.get("context", {}),
                    qid=qid
                )
                responses.append(response.model_dump())
        else:
            # Pergunta única
            question = state.get("input_text", "")
            response = knowledge_agent.generate_response(
                question=question,
                context=state.get("context", {})
            )
            responses.append(response.model_dump())
        
        state["generated_responses"] = responses
        state["current_step"] = "knowledge_complete"
        logger.info(f"Knowledge completo: {len(responses)} respostas geradas")
        
    except Exception as e:
        logger.error(f"Erro no Agente Conhecimento: {e}")
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Knowledge error: {str(e)}")
        state["current_step"] = "error"
    
    return state


def verifier_node(
    state: WorkflowState,
    verifier_agent: VerifierAgent
) -> WorkflowState:
    """Node do Agente Verificador."""
    logger.info("Executando Agente Verificador")
    
    try:
        verified_responses = []
        generated_responses = state.get("generated_responses", [])
        parsed_questions = state.get("parsed_questions", [])
        
        # Criar mapeamento QID -> pergunta
        question_map = {q.get("qid"): q.get("question_text", "") for q in parsed_questions}
        
        for resp_data in generated_responses:
            from src.workflows.schema import GeneratedResponse
            response = GeneratedResponse(**resp_data)
            question = question_map.get(response.qid, state.get("input_text", ""))
            
            verified = verifier_agent.verify(
                question=question,
                response=response,
                all_responses=[GeneratedResponse(**r) for r in generated_responses]
            )
            verified_responses.append(verified.model_dump())
        
        state["verified_responses"] = verified_responses
        state["current_step"] = "verifier_complete"
        logger.info(f"Verifier completo: {len(verified_responses)} respostas verificadas")
        
    except Exception as e:
        logger.error(f"Erro no Agente Verificador: {e}")
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Verifier error: {str(e)}")
        state["current_step"] = "error"
    
    return state
```

### 2. Atualizar Workflow com Novos Nodes

#### Atualizar `src/workflows/workflow.py`:
```python
from src.workflows.nodes import (
    entry_node, orchestrator_node, exit_node,
    parser_node, knowledge_node, verifier_node
)
from src.agents.parser import ParserAgent
from src.agents.knowledge import KnowledgeAgent
from src.agents.verifier import VerifierAgent

def _build_graph(self) -> StateGraph:
    """Construir grafo do workflow."""
    # Criar factory e agentes
    factory = LLMFactory()
    llm = factory.get_default_llm(session_id="workflow-init")
    
    orchestrator = OrchestratorAgent(llm=llm, session_id="workflow-init")
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
    workflow.add_edge("verifier", "exit")
    workflow.add_edge("exit", END)
    
    return workflow
```

### 3. Implementar Comunicação A2A

#### Criar `src/agents/a2a_communication.py`:
```python
"""Comunicação Agent-to-Agent."""
from typing import Dict, Any, Optional
from langchain_core.messages import BaseMessage
import logging

logger = logging.getLogger(__name__)


class A2AMessage:
    """Mensagem entre agentes."""
    def __init__(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        payload: Dict[str, Any]
    ):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.payload = payload


class A2ACommunicator:
    """Gerenciador de comunicação A2A."""
    
    def __init__(self):
        self.message_queue = []
        self.message_history = []
    
    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        payload: Dict[str, Any]
    ) -> None:
        """Enviar mensagem entre agentes."""
        message = A2AMessage(from_agent, to_agent, message_type, payload)
        self.message_queue.append(message)
        self.message_history.append(message)
        logger.debug(f"Mensagem A2A: {from_agent} -> {to_agent} ({message_type})")
    
    def get_messages_for_agent(self, agent_name: str) -> List[A2AMessage]:
        """Obter mensagens para um agente."""
        messages = [m for m in self.message_queue if m.to_agent == agent_name]
        self.message_queue = [m for m in self.message_queue if m.to_agent != agent_name]
        return messages
```

### 4. Implementar Execução Paralela

#### Atualizar `src/agents/agent_coordinator.py`:
```python
async def coordinate_parallel(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Coordenar execução paralela de tarefas."""
    # Já implementado, apenas garantir que funciona com novos agentes
    pass
```

### 5. Adicionar Tratamento de Erros entre Agentes

#### Criar `src/agents/error_handler.py`:
```python
"""Tratamento de erros entre agentes."""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AgentErrorHandler:
    """Gerenciador de erros entre agentes."""
    
    @staticmethod
    def handle_agent_error(
        agent_name: str,
        error: Exception,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Tratar erro de agente."""
        logger.error(f"Erro no agente {agent_name}: {error}")
        
        if "errors" not in state:
            state["errors"] = []
        
        state["errors"].append({
            "agent": agent_name,
            "error": str(error),
            "type": type(error).__name__
        })
        
        # Decidir se deve continuar ou parar
        if agent_name == "orchestrator":
            state["current_step"] = "error"
        else:
            # Outros agentes podem ter fallback
            state["current_step"] = f"{agent_name}_error"
        
        return state
```

### 6. Implementar Retry Logic

#### Adicionar retry em nodes:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def parser_node_with_retry(state, parser_agent):
    """Parser node com retry."""
    return parser_node(state, parser_agent)
```

### 7. Adicionar Logging de Interações

#### Atualizar nodes para logging detalhado:
```python
def parser_node(state, parser_agent):
    logger.info(f"[A2A] Parser iniciado para workflow {state['workflow_id']}")
    # ... código ...
    logger.info(f"[A2A] Parser concluído, enviando {len(parsed_questions)} perguntas para Knowledge")
    return state
```

### 8. Testar Fluxo Completo End-to-End

#### Criar `tests/integration/test_agents_integration.py`:
```python
"""Testes de integração entre agentes."""
import pytest
from src.workflows.workflow import RFPWorkflow
from langgraph.checkpoint.memory import MemorySaver

@pytest.fixture
def workflow():
    checkpoint = MemorySaver()
    return RFPWorkflow(checkpoint_saver=checkpoint)

def test_full_workflow_questionnaire(workflow):
    """Testar fluxo completo com questionário."""
    input_text = """
    Pergunta 1: Qual é o SLA?
    Pergunta 2: Qual é o suporte oferecido?
    """
    result = workflow.run(input_text, session_id="test-integration-1")
    
    assert result["parsed_questions"] is not None
    assert result["generated_responses"] is not None
    assert result["verified_responses"] is not None
```

---

## Checklist de Validação

- [ ] Todos os agentes integrados no LangGraph StateGraph
- [ ] Comunicação A2A implementada
- [ ] Fluxo de dados entre agentes funcionando
- [ ] Execução paralela quando possível
- [ ] Tratamento de erros entre agentes implementado
- [ ] Retry logic implementado
- [ ] Logging de interações adicionado
- [ ] Testes end-to-end passando
- [ ] Performance otimizada
- [ ] Documentação de padrões de comunicação criada

---

## Comandos de Teste

```bash
# Testar integração completa
python -m pytest tests/integration/test_agents_integration.py

# Testar fluxo end-to-end
python -m pytest tests/integration/test_agents_integration.py::test_full_workflow_questionnaire
```


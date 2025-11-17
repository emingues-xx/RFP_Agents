# Tarefa 2.2: Criação do Workflow Base com LangGraph

## Objetivo
Criar o workflow base usando LangGraph StateGraph com nodes, edges e checkpoint para persistência.

## Prioridade
Alta

## Estimativa
4 dias

## Responsável
Backend

---

## Instruções de Implementação

### 1. Definir Estrutura do StateGraph

#### Criar `src/workflows/state.py`:
```python
"""Estado compartilhado do workflow."""
from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage


class WorkflowState(TypedDict):
    """Estado do workflow."""
    # Input
    input_text: str
    input_type: Optional[str]  # "single_question" ou "questionnaire"
    file_path: Optional[str]
    
    # Contexto
    context: Dict[str, Any]  # cliente, produto, prazos
    
    # Mensagens
    messages: List[BaseMessage]
    
    # Resultados dos agentes
    parsed_questions: Optional[List[Dict[str, Any]]]
    generated_responses: Optional[List[Dict[str, Any]]]
    verified_responses: Optional[List[Dict[str, Any]]]
    
    # Metadados
    session_id: str
    workflow_id: str
    current_step: str
    errors: List[str]
    
    # Aprovação
    requires_approval: bool
    approval_status: Optional[str]  # "pending", "approved", "rejected"
```

### 2. Criar Schema de Estado Compartilhado

#### Criar `src/workflows/schema.py`:
```python
"""Schema para validação de estado."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage


class ParsedQuestion(BaseModel):
    """Pergunta parseada e normalizada."""
    qid: str
    category: str
    question_text: str
    requirements: List[str]
    expected_format: str
    similar_questions: List[str] = Field(default_factory=list)


class GeneratedResponse(BaseModel):
    """Resposta gerada."""
    qid: str
    response_text: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    citations: List[str] = Field(default_factory=list)
    requires_human_input: bool = False
    human_input_fields: List[str] = Field(default_factory=list)


class VerifiedResponse(BaseModel):
    """Resposta verificada."""
    qid: str
    response_text: str
    confidence_score: float
    is_consistent: bool
    has_prohibited_terms: bool
    has_gaps: bool
    validation_errors: List[str] = Field(default_factory=list)
    needs_review: bool
```

### 3. Implementar Nodes Básicos

#### Criar `src/workflows/nodes.py`:
```python
"""Nodes do workflow LangGraph."""
from typing import Dict, Any
from src.workflows.state import WorkflowState
from src.agents.orchestrator import OrchestratorAgent
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
        state["context"] = context.dict()
        
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
        state["errors"].append(f"Orchestrator error: {str(e)}")
        state["current_step"] = "error"
    
    return state


def exit_node(state: WorkflowState) -> WorkflowState:
    """Node de saída do workflow."""
    logger.info(f"Workflow finalizado: {state['workflow_id']}")
    state["current_step"] = "completed"
    return state
```

### 4. Implementar Edges Básicos

#### Criar `src/workflows/edges.py`:
```python
"""Edges (rotas) do workflow LangGraph."""
from typing import Literal
from src.workflows.state import WorkflowState
import logging

logger = logging.getLogger(__name__)


def route_after_orchestrator(state: WorkflowState) -> Literal["single_question", "questionnaire", "error"]:
    """Roteamento após orquestrador."""
    input_type = state.get("input_type")
    
    if not input_type:
        logger.error("Tipo de input não identificado")
        return "error"
    
    if input_type == "single_question":
        return "single_question"
    elif input_type == "questionnaire":
        return "questionnaire"
    else:
        return "error"


def route_after_verification(state: WorkflowState) -> Literal["approval", "error"]:
    """Roteamento após verificação."""
    if state.get("errors"):
        return "error"
    
    # Sempre requer aprovação
    state["requires_approval"] = True
    return "approval"
```

### 5. Configurar Checkpoint para Persistência

#### Criar `src/workflows/checkpoint.py`:
```python
"""Checkpoint para persistência de estado."""
from typing import Any, Dict
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.base import BaseCheckpointSaver
from sqlalchemy import create_engine
from src.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


def create_checkpoint_saver() -> BaseCheckpointSaver:
    """Criar checkpoint saver usando PostgreSQL."""
    try:
        # Criar engine
        engine = create_engine(settings.database_url)
        
        # Criar PostgresSaver
        checkpoint_saver = PostgresSaver(engine)
        
        # Criar tabelas se não existirem
        checkpoint_saver.setup()
        
        logger.info("Checkpoint saver configurado com sucesso")
        return checkpoint_saver
        
    except Exception as e:
        logger.error(f"Erro ao configurar checkpoint: {e}")
        # Fallback para memória (não persistente)
        from langgraph.checkpoint.memory import MemorySaver
        logger.warning("Usando MemorySaver como fallback")
        return MemorySaver()
```

### 6. Integrar com LangGraph StateGraph

#### Criar `src/workflows/workflow.py`:
```python
"""Workflow principal usando LangGraph."""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver
from src.workflows.state import WorkflowState
from src.workflows.nodes import entry_node, orchestrator_node, exit_node
from src.workflows.edges import route_after_orchestrator, route_after_verification
from src.agents.orchestrator import OrchestratorAgent
from src.utils.llm_factory import LLMFactory
from src.workflows.checkpoint import create_checkpoint_saver
import logging

logger = logging.getLogger(__name__)


class RFPWorkflow:
    """Workflow principal para processamento de RFPs."""
    
    def __init__(self, checkpoint_saver: BaseCheckpointSaver = None):
        """Inicializar workflow."""
        self.checkpoint_saver = checkpoint_saver or create_checkpoint_saver()
        self.graph = self._build_graph()
        self.app = self.graph.compile(checkpointer=self.checkpoint_saver)
    
    def _build_graph(self) -> StateGraph:
        """Construir grafo do workflow."""
        # Criar factory e orquestrador
        factory = LLMFactory()
        llm = factory.get_default_llm()
        orchestrator = OrchestratorAgent(llm=llm)
        
        # Criar grafo
        workflow = StateGraph(WorkflowState)
        
        # Adicionar nodes
        workflow.add_node("entry", entry_node)
        workflow.add_node("orchestrator", lambda state: orchestrator_node(state, orchestrator))
        workflow.add_node("exit", exit_node)
        
        # Adicionar edges
        workflow.set_entry_point("entry")
        workflow.add_edge("entry", "orchestrator")
        workflow.add_conditional_edges(
            "orchestrator",
            route_after_orchestrator,
            {
                "single_question": "exit",  # TODO: adicionar node de conhecimento
                "questionnaire": "exit",  # TODO: adicionar node de parser
                "error": "exit"
            }
        )
        workflow.add_edge("exit", END)
        
        return workflow
    
    def run(self, input_text: str, session_id: str, config: Dict = None) -> Dict:
        """Executar workflow."""
        initial_state = {
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
            "approval_status": None
        }
        
        config = config or {}
        config["configurable"] = {"thread_id": session_id}
        
        try:
            result = self.app.invoke(initial_state, config=config)
            return result
        except Exception as e:
            logger.error(f"Erro ao executar workflow: {e}")
            raise
```

### 7. Testar Workflow Básico End-to-End

#### Criar `tests/integration/test_workflow.py`:
```python
"""Testes de integração do workflow."""
import pytest
from src.workflows.workflow import RFPWorkflow
from langgraph.checkpoint.memory import MemorySaver


@pytest.fixture
def workflow():
    """Fixture para workflow."""
    checkpoint = MemorySaver()
    return RFPWorkflow(checkpoint_saver=checkpoint)


def test_workflow_entry(workflow):
    """Testar entrada do workflow."""
    result = workflow.run(
        input_text="Qual é o SLA?",
        session_id="test-session-1"
    )
    assert result is not None
    assert "current_step" in result


def test_workflow_single_question(workflow):
    """Testar workflow com pergunta única."""
    result = workflow.run(
        input_text="Qual é o tempo de resposta do sistema?",
        session_id="test-session-2"
    )
    assert result["input_type"] in ["single_question", "questionnaire", "unknown"]


def test_workflow_questionnaire(workflow):
    """Testar workflow com questionário."""
    input_text = """
    Pergunta 1: Qual é o SLA?
    Pergunta 2: Qual é o suporte oferecido?
    Pergunta 3: Qual é o preço?
    """
    result = workflow.run(
        input_text=input_text,
        session_id="test-session-3"
    )
    assert result["input_type"] in ["single_question", "questionnaire", "unknown"]
```

### 8. Adicionar Métricas de Execução

#### Atualizar `src/workflows/workflow.py`:
```python
from src.utils.metrics import (
    agent_executions_total,
    agent_execution_duration_seconds
)
import time

class RFPWorkflow:
    def run(self, input_text: str, session_id: str, config: Dict = None) -> Dict:
        """Executar workflow com métricas."""
        start_time = time.time()
        
        try:
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
            
            return result
        except Exception as e:
            # Métricas de erro
            agent_executions_total.labels(
                agent_name="workflow",
                status="error"
            ).inc()
            raise
```

### 9. Documentar Estrutura do Workflow

#### Criar `docs/workflows/workflow.md`:
```markdown
# Workflow LangGraph

## Estrutura

```
Entry → Orchestrator → [Branching] → Exit
```

## Nodes

1. **entry**: Ponto de entrada
2. **orchestrator**: Agente Orquestrador
3. **exit**: Ponto de saída

## Estado

O estado é compartilhado entre todos os nodes e inclui:
- Input e contexto
- Resultados dos agentes
- Metadados do workflow
- Status de aprovação

## Uso

```python
from src.workflows.workflow import RFPWorkflow

workflow = RFPWorkflow()
result = workflow.run(
    input_text="Qual é o SLA?",
    session_id="session-123"
)
```
```

---

## Checklist de Validação

- [ ] Estrutura do StateGraph definida
- [ ] Schema de estado criado
- [ ] Nodes básicos implementados
- [ ] Edges básicos implementados
- [ ] Checkpoint configurado
- [ ] Workflow integrado com LangGraph
- [ ] Testes end-to-end criados e passando
- [ ] Métricas adicionadas
- [ ] Documentação criada

---

## Próximos Passos
Após completar esta tarefa, seguir para: **Tarefa 2.3: Implementação de Branching Básico**


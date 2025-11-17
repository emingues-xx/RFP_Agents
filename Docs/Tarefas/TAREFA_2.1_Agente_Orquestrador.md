# Tarefa 2.1: Implementação do Agente Orquestrador

## Objetivo
Implementar o Agente Orquestrador que coordena todo o fluxo do sistema, identifica tipos de input e gerencia a comunicação entre agentes.

## Prioridade
Alta

## Estimativa
3 dias

## Responsável
Backend

---

## Instruções de Implementação

### 1. Criar Classe Base do Agente Orquestrador

#### Criar `src/agents/orchestrator.py`:
```python
"""Agente Orquestrador - Coordena todo o fluxo do sistema."""
from typing import Dict, Any, Literal, Optional
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.memory import BaseMemory
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class InputType(BaseModel):
    """Tipo de input identificado."""
    type: Literal["single_question", "questionnaire", "unknown"]
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Context(BaseModel):
    """Contexto coletado para processamento."""
    client: Optional[str] = None
    product: Optional[str] = None
    deadlines: Optional[str] = None
    additional_info: Dict[str, Any] = Field(default_factory=dict)


class OrchestratorAgent:
    """Agente Orquestrador principal."""
    
    def __init__(
        self,
        llm: BaseChatModel,
        memory: Optional[BaseMemory] = None,
    ):
        """Inicializar Agente Orquestrador."""
        self.llm = llm
        self.memory = memory
        self._setup_system_prompt()
    
    def _setup_system_prompt(self) -> None:
        """Configurar prompt do sistema."""
        self.system_prompt = """Você é um Agente Orquestrador responsável por:
1. Identificar o tipo de input recebido (pergunta única ou questionário)
2. Coletar contexto adicional necessário (cliente, produto, prazos)
3. Coordenar agentes especialistas para processar o input
4. Gerenciar o fluxo de trabalho e estado

Sempre responda em formato JSON estruturado."""
    
    def identify_input_type(self, input_text: str) -> InputType:
        """Identificar tipo de input (pergunta única vs. questionário)."""
        prompt = f"""Analise o seguinte input e identifique se é:
- "single_question": Uma pergunta única e direta
- "questionnaire": Um questionário com múltiplas perguntas
- "unknown": Não é possível determinar

Input: {input_text}

Responda em JSON:
{{"type": "single_question|questionnaire|unknown", "confidence": 0.0-1.0, "metadata": {{}}}}"""
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            # Parse JSON response
            import json
            result = json.loads(response.content)
            return InputType(**result)
        except Exception as e:
            logger.error(f"Erro ao identificar tipo de input: {e}")
            return InputType(type="unknown", confidence=0.0)
    
    def collect_context(self, input_text: str) -> Context:
        """Coletar contexto adicional (cliente, produto, prazos)."""
        prompt = f"""Extraia informações de contexto do seguinte input:
- Cliente (se mencionado)
- Produto (se mencionado)
- Prazos (se mencionado)
- Outras informações relevantes

Input: {input_text}

Responda em JSON:
{{"client": "...", "product": "...", "deadlines": "...", "additional_info": {{}}}}"""
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            import json
            result = json.loads(response.content)
            return Context(**result)
        except Exception as e:
            logger.error(f"Erro ao coletar contexto: {e}")
            return Context()
    
    def coordinate_agents(
        self,
        input_type: InputType,
        context: Context,
        input_data: str
    ) -> Dict[str, Any]:
        """Coordenar agentes especialistas baseado no tipo de input."""
        coordination_plan = {
            "input_type": input_type.type,
            "context": context.dict(),
            "next_steps": []
        }
        
        if input_type.type == "single_question":
            coordination_plan["next_steps"] = [
                {
                    "agent": "knowledge",
                    "action": "generate_response",
                    "input": input_data
                }
            ]
        elif input_type.type == "questionnaire":
            coordination_plan["next_steps"] = [
                {
                    "agent": "parser",
                    "action": "extract_and_normalize",
                    "input": input_data
                },
                {
                    "agent": "knowledge",
                    "action": "generate_responses",
                    "depends_on": "parser"
                },
                {
                    "agent": "verifier",
                    "action": "validate_responses",
                    "depends_on": "knowledge"
                }
            ]
        
        logger.info(f"Plano de coordenação: {coordination_plan}")
        return coordination_plan
    
    def manage_workflow_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Gerenciar estado do workflow."""
        # Adicionar metadados ao estado
        state["orchestrator"] = {
            "last_update": str(datetime.now()),
            "version": "1.0"
        }
        return state
```

### 2. Implementar Identificação de Tipo de Input

#### Adicionar método melhorado em `orchestrator.py`:
```python
def identify_input_type_enhanced(self, input_text: str, file_path: Optional[str] = None) -> InputType:
    """Identificação melhorada com suporte a arquivos."""
    # Heurísticas simples
    question_count = input_text.count('?')
    line_count = len(input_text.split('\n'))
    
    # Se tem arquivo, provavelmente é questionário
    if file_path:
        return InputType(
            type="questionnaire",
            confidence=0.9,
            metadata={"source": "file", "file_path": file_path}
        )
    
    # Se tem múltiplas perguntas, é questionário
    if question_count > 1 or line_count > 5:
        return InputType(
            type="questionnaire",
            confidence=0.8,
            metadata={"question_count": question_count}
        )
    
    # Caso contrário, usar LLM para decidir
    return self.identify_input_type(input_text)
```

### 3. Implementar Coleta de Contexto

#### Melhorar método `collect_context`:
```python
def collect_context_interactive(self, input_text: str) -> Context:
    """Coletar contexto com possibilidade de perguntas adicionais."""
    context = self.collect_context(input_text)
    
    # Se contexto está incompleto, preparar perguntas
    if not context.client or not context.product:
        context.additional_info["needs_clarification"] = True
        context.additional_info["questions"] = []
        
        if not context.client:
            context.additional_info["questions"].append("Qual é o nome do cliente?")
        if not context.product:
            context.additional_info["questions"].append("Qual produto está sendo proposto?")
    
    return context
```

### 4. Implementar Interface com Humano (Memória Persistente)

#### Criar `src/agents/memory_manager.py`:
```python
"""Gerenciador de memória persistente."""
from typing import List, Optional
from langchain.memory import ConversationBufferMemory
from langchain.memory.postgres import PostgresChatMessageHistory
from sqlalchemy import create_engine
from src.config.settings import get_settings

settings = get_settings()


class PersistentMemoryManager:
    """Gerenciador de memória persistente."""
    
    def __init__(self, session_id: str):
        """Inicializar gerenciador."""
        self.session_id = session_id
        self.memory = self._create_memory()
    
    def _create_memory(self) -> ConversationBufferMemory:
        """Criar memória persistente."""
        connection_string = settings.database_url
        
        # Criar histórico no PostgreSQL
        message_history = PostgresChatMessageHistory(
            connection_string=connection_string,
            session_id=self.session_id,
            table_name="chat_history"
        )
        
        # Criar memória com histórico
        memory = ConversationBufferMemory(
            chat_memory=message_history,
            return_messages=True,
            memory_key="chat_history"
        )
        
        return memory
    
    def save_context(self, input_str: str, output_str: str) -> None:
        """Salvar contexto na memória."""
        self.memory.save_context({"input": input_str}, {"output": output_str})
    
    def load_memory_variables(self) -> dict:
        """Carregar variáveis da memória."""
        return self.memory.load_memory_variables({})
    
    def clear(self) -> None:
        """Limpar memória."""
        self.memory.clear()
```

#### Integrar no Orchestrator:
```python
from src.agents.memory_manager import PersistentMemoryManager

class OrchestratorAgent:
    def __init__(
        self,
        llm: BaseChatModel,
        session_id: str,
        memory_manager: Optional[PersistentMemoryManager] = None,
    ):
        self.llm = llm
        self.memory_manager = memory_manager or PersistentMemoryManager(session_id)
        # ... resto do código
```

### 5. Implementar Coordenação de Agentes Especialistas

#### Criar `src/agents/agent_coordinator.py`:
```python
"""Coordenador de agentes especialistas."""
from typing import Dict, Any, List
from src.agents.parser import ParserAgent
from src.agents.knowledge import KnowledgeAgent
from src.agents.verifier import VerifierAgent
import asyncio
import logging

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """Coordenador de agentes."""
    
    def __init__(
        self,
        parser_agent: ParserAgent,
        knowledge_agent: KnowledgeAgent,
        verifier_agent: VerifierAgent,
    ):
        """Inicializar coordenador."""
        self.parser_agent = parser_agent
        self.knowledge_agent = knowledge_agent
        self.verifier_agent = verifier_agent
    
    async def coordinate_parallel(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Coordenar execução paralela de tarefas."""
        results = {}
        
        # Agrupar tarefas por dependências
        independent_tasks = [t for t in tasks if "depends_on" not in t]
        dependent_tasks = [t for t in tasks if "depends_on" in t]
        
        # Executar tarefas independentes em paralelo
        if independent_tasks:
            parallel_results = await asyncio.gather(*[
                self._execute_task(task) for task in independent_tasks
            ])
            for task, result in zip(independent_tasks, parallel_results):
                results[task["agent"]] = result
        
        # Executar tarefas dependentes sequencialmente
        for task in dependent_tasks:
            dependency = task["depends_on"]
            if dependency in results:
                task["input"] = results[dependency]
                result = await self._execute_task(task)
                results[task["agent"]] = result
        
        return results
    
    async def _execute_task(self, task: Dict[str, Any]) -> Any:
        """Executar tarefa individual."""
        agent_name = task["agent"]
        action = task["action"]
        input_data = task.get("input")
        
        if agent_name == "parser":
            return await self.parser_agent.process(input_data)
        elif agent_name == "knowledge":
            return await self.knowledge_agent.generate_response(input_data)
        elif agent_name == "verifier":
            return await self.verifier_agent.verify(input_data)
        else:
            raise ValueError(f"Agente desconhecido: {agent_name}")
```

### 6. Integrar com LangChain Memory

#### Atualizar `orchestrator.py`:
```python
def get_conversation_history(self) -> List[BaseMessage]:
    """Obter histórico de conversa da memória."""
    if self.memory_manager:
        memory_vars = self.memory_manager.load_memory_variables()
        return memory_vars.get("chat_history", [])
    return []

def add_to_memory(self, user_input: str, agent_response: str) -> None:
    """Adicionar interação à memória."""
    if self.memory_manager:
        self.memory_manager.save_context(user_input, agent_response)
```

### 7. Adicionar Logging Detalhado

#### Adicionar logging em pontos-chave:
```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class OrchestratorAgent:
    def identify_input_type(self, input_text: str) -> InputType:
        logger.info(f"Iniciando identificação de tipo de input")
        logger.debug(f"Input recebido: {input_text[:100]}...")
        
        result = # ... código de identificação
        
        logger.info(f"Tipo identificado: {result.type} (confiança: {result.confidence})")
        return result
```

### 8. Criar Testes Unitários

#### Criar `tests/unit/test_orchestrator.py`:
```python
"""Testes para Agente Orquestrador."""
import pytest
from src.agents.orchestrator import OrchestratorAgent, InputType, Context
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_llm():
    """Mock do LLM."""
    llm = Mock()
    llm.invoke = Mock(return_value=MagicMock(content='{"type": "single_question", "confidence": 0.9}'))
    return llm


@pytest.fixture
def orchestrator(mock_llm):
    """Fixture para Orchestrator."""
    return OrchestratorAgent(llm=mock_llm)


def test_identify_single_question(orchestrator):
    """Testar identificação de pergunta única."""
    input_text = "Qual é o SLA do produto?"
    result = orchestrator.identify_input_type(input_text)
    assert result.type in ["single_question", "questionnaire", "unknown"]
    assert 0.0 <= result.confidence <= 1.0


def test_identify_questionnaire(orchestrator):
    """Testar identificação de questionário."""
    input_text = "Pergunta 1: ...\nPergunta 2: ...\nPergunta 3: ..."
    result = orchestrator.identify_input_type(input_text)
    assert result.type in ["single_question", "questionnaire", "unknown"]


def test_collect_context(orchestrator):
    """Testar coleta de contexto."""
    input_text = "Cliente: ABC Corp, Produto: Cloud Services, Prazo: 30 dias"
    context = orchestrator.collect_context(input_text)
    assert isinstance(context, Context)


def test_coordinate_agents_single_question(orchestrator):
    """Testar coordenação para pergunta única."""
    input_type = InputType(type="single_question", confidence=0.9)
    context = Context()
    plan = orchestrator.coordinate_agents(input_type, context, "Test question")
    assert "next_steps" in plan
    assert len(plan["next_steps"]) > 0
```

### 9. Documentar API e Uso

#### Criar `docs/agents/orchestrator.md`:
```markdown
# Agente Orquestrador

## Visão Geral
O Agente Orquestrador é responsável por coordenar todo o fluxo do sistema.

## Funcionalidades
- Identificação de tipo de input
- Coleta de contexto
- Coordenação de agentes
- Gerenciamento de estado

## Uso
```python
from src.agents.orchestrator import OrchestratorAgent
from src.utils.llm_factory import LLMFactory

factory = LLMFactory()
llm = factory.get_default_llm()
orchestrator = OrchestratorAgent(llm=llm, session_id="session-123")

# Identificar tipo
input_type = orchestrator.identify_input_type("Qual é o SLA?")

# Coletar contexto
context = orchestrator.collect_context("Cliente: ABC Corp")

# Coordenar agentes
plan = orchestrator.coordinate_agents(input_type, context, "input data")
```
```

---

## Checklist de Validação

- [ ] Classe base do Agente Orquestrador criada
- [ ] Identificação de tipo de input implementada
- [ ] Coleta de contexto implementada
- [ ] Interface com memória persistente implementada
- [ ] Coordenação de agentes implementada
- [ ] Integração com LangChain Memory funcionando
- [ ] Logging detalhado adicionado
- [ ] Testes unitários criados e passando
- [ ] Documentação criada

---

## Próximos Passos
Após completar esta tarefa, seguir para: **Tarefa 2.2: Criação do Workflow Base com LangGraph**


# Agente Orquestrador

## Visão Geral
O Agente Orquestrador é responsável por coordenar todo o fluxo do sistema. Ele identifica tipos de input, coleta contexto adicional e coordena a execução dos agentes especialistas.

## Funcionalidades

### 1. Identificação de Tipo de Input
- Identifica se o input é uma pergunta única ou um questionário
- Suporta heurísticas simples e análise via LLM
- Suporta identificação a partir de arquivos

### 2. Coleta de Contexto
- Extrai informações relevantes (cliente, produto, prazos)
- Identifica quando informações adicionais são necessárias
- Prepara perguntas de clarificação quando necessário

### 3. Coordenação de Agentes
- Cria planos de execução baseados no tipo de input
- Gerencia dependências entre agentes
- Suporta execução paralela e sequencial

### 4. Gerenciamento de Estado
- Mantém estado do workflow
- Adiciona metadados de controle
- Rastreia sessões

### 5. Memória Persistente
- Integra com PostgreSQL para histórico de conversas
- Mantém contexto entre interações
- Suporta múltiplas sessões

## Uso

### Exemplo Básico

```python
from src.agents.orchestrator import OrchestratorAgent
from src.agents.memory_manager import PersistentMemoryManager
from src.utils.llm_factory import LLMFactory

# Criar factory e LLM
factory = LLMFactory()
llm = factory.get_default_llm(session_id="session-123")

# Criar memory manager (opcional)
memory_manager = PersistentMemoryManager(session_id="session-123")

# Criar orchestrator
orchestrator = OrchestratorAgent(
    llm=llm,
    session_id="session-123",
    memory_manager=memory_manager
)

# Identificar tipo de input
input_text = "Qual é o SLA do produto?"
input_type = orchestrator.identify_input_type(input_text)
print(f"Tipo: {input_type.type}, Confiança: {input_type.confidence}")

# Coletar contexto
context = orchestrator.collect_context("Cliente: ABC Corp, Produto: Cloud Services")
print(f"Cliente: {context.client}, Produto: {context.product}")

# Coordenar agentes
plan = orchestrator.coordinate_agents(input_type, context, input_text)
print(f"Próximos passos: {plan['next_steps']}")
```

### Exemplo com Identificação Melhorada

```python
# Identificação com heurísticas
input_type = orchestrator.identify_input_type_enhanced(
    input_text="Pergunta 1?\nPergunta 2?\nPergunta 3?",
    file_path=None
)

# Com arquivo
input_type = orchestrator.identify_input_type_enhanced(
    input_text="...",
    file_path="/path/to/questionnaire.pdf"
)
```

### Exemplo com Contexto Interativo

```python
# Coletar contexto com perguntas de clarificação
context = orchestrator.collect_context_interactive("Produto: Cloud Services")

if context.additional_info.get("needs_clarification"):
    questions = context.additional_info.get("questions", [])
    for question in questions:
        print(f"Pergunta: {question}")
```

### Exemplo com Memória

```python
# Adicionar interação à memória
orchestrator.add_to_memory(
    user_input="Qual é o SLA?",
    agent_response="O SLA é de 99.9% de uptime."
)

# Obter histórico
history = orchestrator.get_conversation_history()
print(f"Histórico com {len(history)} mensagens")
```

## Classes

### InputType
Modelo Pydantic que representa o tipo de input identificado.

**Campos:**
- `type`: Literal["single_question", "questionnaire", "unknown"]
- `confidence`: float (0.0 a 1.0)
- `metadata`: Dict[str, Any]

### Context
Modelo Pydantic que representa o contexto coletado.

**Campos:**
- `client`: Optional[str]
- `product`: Optional[str]
- `deadlines`: Optional[str]
- `additional_info`: Dict[str, Any]

## Integração com Outros Agentes

O Orchestrator coordena os seguintes agentes:
- **ParserAgent**: Extrai e normaliza perguntas de questionários
- **KnowledgeAgent**: Gera respostas baseadas em conhecimento
- **VerifierAgent**: Valida respostas geradas

## Logging

O Orchestrator usa logging detalhado em todos os métodos principais:
- `logger.info()`: Operações principais
- `logger.debug()`: Detalhes de execução
- `logger.warning()`: Avisos
- `logger.error()`: Erros

## Tratamento de Erros

- Erros de parsing JSON são capturados e retornam valores padrão
- Erros de LLM são logados e não interrompem o fluxo
- Memória persistente tem fallback para memória em memória

## Próximos Passos

1. Integrar com LangGraph para workflows mais complexos
2. Adicionar suporte a retry automático
3. Implementar cache de identificação de tipos
4. Adicionar métricas de performance


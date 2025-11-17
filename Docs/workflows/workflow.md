# Workflow LangGraph

## Visão Geral

O workflow principal do sistema é implementado usando LangGraph StateGraph, permitindo coordenação de agentes especialistas com estado compartilhado e checkpoint para persistência.

## Estrutura

```
Entry → Orchestrator → [Branching] → Exit
```

### Fluxo Básico

1. **Entry**: Ponto de entrada do workflow
2. **Orchestrator**: Agente Orquestrador identifica tipo de input e coordena agentes
3. **Branching**: Roteamento baseado no tipo de input identificado
   - `single_question`: Pergunta única
   - `questionnaire`: Questionário com múltiplas perguntas
   - `error`: Erro na identificação
4. **Exit**: Ponto de saída do workflow

## Nodes

### entry_node
- **Função**: Inicializar workflow
- **Ações**: Define `current_step` como "entry"
- **Saída**: Estado inicializado

### orchestrator_node
- **Função**: Executar Agente Orquestrador
- **Ações**:
  - Identifica tipo de input
  - Coleta contexto (cliente, produto, prazos)
  - Cria plano de coordenação
- **Saída**: Estado com `input_type`, `context` e `coordination_plan`

### exit_node
- **Função**: Finalizar workflow
- **Ações**: Define `current_step` como "completed"
- **Saída**: Estado final

## Estado

O estado (`WorkflowState`) é compartilhado entre todos os nodes e inclui:

### Input
- `input_text`: Texto de entrada
- `input_type`: Tipo identificado ("single_question", "questionnaire", "unknown")
- `file_path`: Caminho do arquivo (opcional)

### Contexto
- `context`: Dicionário com informações de contexto (cliente, produto, prazos)

### Mensagens
- `messages`: Lista de mensagens LangChain

### Resultados dos Agentes
- `parsed_questions`: Perguntas parseadas (opcional)
- `generated_responses`: Respostas geradas (opcional)
- `verified_responses`: Respostas verificadas (opcional)

### Metadados
- `session_id`: ID da sessão
- `workflow_id`: ID do workflow
- `current_step`: Passo atual
- `errors`: Lista de erros

### Aprovação
- `requires_approval`: Se requer aprovação humana
- `approval_status`: Status da aprovação ("pending", "approved", "rejected")

### Coordenação
- `coordination_plan`: Plano de coordenação criado pelo orquestrador

## Checkpoint

O workflow suporta checkpoint para persistência de estado:

- **PostgreSQL**: Usa `PostgresSaver` quando disponível
- **Memória**: Fallback para `MemorySaver` se PostgreSQL não estiver disponível

O checkpoint permite:
- Retomar workflows interrompidos
- Histórico de execuções
- Debugging de estados intermediários

## Uso

### Exemplo Básico

```python
from src.workflows.workflow import RFPWorkflow

# Criar workflow
workflow = RFPWorkflow()

# Executar workflow
result = workflow.run(
    input_text="Qual é o SLA?",
    session_id="session-123"
)

# Verificar resultado
print(f"Tipo identificado: {result['input_type']}")
print(f"Contexto: {result['context']}")
print(f"Passo atual: {result['current_step']}")
```

### Exemplo com Configuração Customizada

```python
from langgraph.checkpoint.memory import MemorySaver

# Usar checkpoint em memória
checkpoint = MemorySaver()
workflow = RFPWorkflow(checkpoint_saver=checkpoint)

# Executar com configuração customizada
config = {
    "configurable": {
        "thread_id": "custom-session-id",
        "recursion_limit": 50
    }
}

result = workflow.run(
    input_text="Pergunta 1?\nPergunta 2?\nPergunta 3?",
    session_id="session-456",
    config=config
)
```

### Exemplo com Retry

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def run_workflow_with_retry(workflow, input_text, session_id):
    return workflow.run(input_text, session_id)

result = run_workflow_with_retry(
    workflow,
    input_text="Qual é o SLA?",
    session_id="session-789"
)
```

## Métricas

O workflow coleta métricas automaticamente:

- `agent_executions_total`: Total de execuções (sucesso/erro)
- `agent_execution_duration_seconds`: Duração de execução

Métricas são expostas via Prometheus em `/metrics`.

## Próximos Passos

1. Adicionar nodes para agentes especialistas:
   - `parser_node`: Para processar questionários
   - `knowledge_node`: Para gerar respostas
   - `verifier_node`: Para verificar respostas

2. Implementar Human-in-the-Loop:
   - Node de aprovação
   - Integração com interface web

3. Adicionar suporte a streaming:
   - Streaming de respostas intermediárias
   - WebSocket para atualizações em tempo real

4. Melhorar tratamento de erros:
   - Retry automático
   - Fallback strategies
   - Error recovery

## Troubleshooting

### Erro: "Tipo de input não identificado"
- Verifique se o LLM está configurado corretamente
- Verifique logs do orchestrator_node
- Tente usar `identify_input_type_enhanced` com heurísticas

### Erro: "Checkpoint não configurado"
- Verifique conexão com PostgreSQL
- Use MemorySaver como fallback para desenvolvimento

### Workflow não finaliza
- Verifique logs para identificar node travado
- Verifique se há erros no estado
- Use `current_step` para identificar onde parou


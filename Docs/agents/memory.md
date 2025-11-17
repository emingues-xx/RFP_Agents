# Memória Persistente

Este documento descreve o sistema de memória persistente usando LangChain Memory com PostgreSQL.

## Visão Geral

O sistema de memória persistente permite manter contexto de conversas entre sessões, armazenando histórico de mensagens no PostgreSQL. Isso permite que o sistema "lembre" de interações anteriores e mantenha contexto ao longo do tempo.

## Tipos de Memória

### ConversationBufferMemory

Armazena todas as mensagens da conversa. Ideal para sessões curtas ou quando contexto completo é necessário.

```python
from src.agents.memory_manager import PersistentMemoryManager

memory = PersistentMemoryManager(
    session_id="session-123",
    use_summary=False
)
```

### ConversationSummaryMemory

Resume conversas longas para economizar tokens. Ideal para sessões muito longas.

```python
from src.agents.memory_manager import PersistentMemoryManager
from src.utils.llm_factory import LLMFactory

factory = LLMFactory()
llm = factory.get_default_llm()

memory = PersistentMemoryManager(
    session_id="session-123",
    use_summary=True,
    llm=llm
)
```

## Uso Básico

### Salvar Contexto

```python
from src.agents.memory_manager import PersistentMemoryManager

memory = PersistentMemoryManager(session_id="session-123")

# Salvar interação
memory.save_context(
    input_str="Qual é o SLA?",
    output_str="O SLA é de 99.9% de disponibilidade"
)
```

### Carregar Histórico

```python
# Carregar histórico completo
history = memory.load_memory_variables()
messages = history.get("chat_history", [])

for msg in messages:
    print(f"{msg.type}: {msg.content}")
```

### Obter Resumo

```python
# Obter resumo textual da conversa
summary = memory.get_conversation_summary()
print(summary)
```

### Contar Mensagens

```python
# Obter número de mensagens
count = memory.get_message_count()
print(f"Total de mensagens: {count}")
```

### Limpar Memória

```python
# Limpar toda a memória da sessão
memory.clear()
```

## Persistência entre Sessões

A memória persiste automaticamente no PostgreSQL:

```python
# Sessão 1
memory1 = PersistentMemoryManager(session_id="session-123")
memory1.save_context("Pergunta 1", "Resposta 1")

# Sessão 2 (nova instância, mesmo session_id)
memory2 = PersistentMemoryManager(session_id="session-123")
history = memory2.load_memory_variables()

# Histórico da sessão 1 está disponível!
assert len(history["chat_history"]) > 0
```

## Múltiplas Sessões

Cada `session_id` mantém sua própria memória isolada:

```python
# Sessão do cliente A
memory_a = PersistentMemoryManager(session_id="client-a")
memory_a.save_context("Q1", "A1")

# Sessão do cliente B
memory_b = PersistentMemoryManager(session_id="client-b")
memory_b.save_context("Q2", "A2")

# Memórias são independentes
hist_a = memory_a.load_memory_variables()
hist_b = memory_b.load_memory_variables()

assert hist_a["chat_history"][0].content != hist_b["chat_history"][0].content
```

## Limpeza de Memória

### Limpeza Automática

Limpar mensagens antigas automaticamente:

```python
from src.agents.memory_cleanup import MemoryCleanup

# Limpar mensagens com mais de 90 dias (padrão)
cleanup = MemoryCleanup(retention_days=90)
deleted = cleanup.cleanup_old_sessions()

print(f"Removidos {deleted} registros antigos")
```

### Limpeza de Sessão Específica

```python
cleanup = MemoryCleanup()
deleted = cleanup.cleanup_by_session("session-123")
print(f"Removidos {deleted} registros da sessão")
```

### Estatísticas

```python
cleanup = MemoryCleanup()

# Número de sessões
session_count = cleanup.get_session_count()
print(f"Total de sessões: {session_count}")

# Número de mensagens
message_count = cleanup.get_message_count()
print(f"Total de mensagens: {message_count}")

# Listar sessões antigas
old_sessions = cleanup.get_old_sessions(days=30)
print(f"Sessões com mais de 30 dias: {len(old_sessions)}")
```

## Integração com Agentes

### Orchestrator Agent

```python
from src.agents.orchestrator import OrchestratorAgent
from src.agents.memory_manager import PersistentMemoryManager
from src.utils.llm_factory import LLMFactory

factory = LLMFactory()
llm = factory.get_default_llm()
session_id = "workflow-123"

memory_manager = PersistentMemoryManager(session_id)
orchestrator = OrchestratorAgent(
    llm=llm,
    session_id=session_id,
    memory_manager=memory_manager
)

# Adicionar à memória
orchestrator.add_to_memory("User input", "Agent response")

# Obter histórico
history = orchestrator.get_conversation_history()
```

## Schema do Banco de Dados

A tabela `chat_history` é criada automaticamente pelo `PostgresChatMessageHistory`. Estrutura:

```sql
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR NOT NULL,
    message JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX idx_chat_history_session_id ON chat_history(session_id);
CREATE INDEX idx_chat_history_created_at ON chat_history(created_at);
CREATE INDEX idx_chat_history_session_created ON chat_history(session_id, created_at);
```

## Métricas

As seguintes métricas são coletadas automaticamente:

- `memory_sessions_total`: Total de sessões ativas (Gauge)
- `memory_messages_total`: Total de mensagens salvas (Counter)

Acesse via Prometheus em `/metrics`.

## Configuração

### Variáveis de Ambiente

```bash
# URL do banco de dados PostgreSQL
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/rfp_agents
```

### Criar Índices

Execute o script SQL para criar índices:

```bash
# Via Docker
docker exec -i rfp-agents-postgres psql -U postgres -d rfp_agents < scripts/create_memory_tables.sql

# Ou diretamente
psql -U postgres -d rfp_agents -f scripts/create_memory_tables.sql
```

## Boas Práticas

1. **Session IDs Únicos**: Use IDs únicos por cliente/projeto/sessão
2. **Limpeza Regular**: Configure limpeza automática de mensagens antigas
3. **Summary Memory**: Use para sessões muito longas (>100 mensagens)
4. **Monitoramento**: Monitore uso de memória via métricas Prometheus
5. **Backup**: Considere backup regular do banco de dados

## Troubleshooting

### Erro: "Tabela chat_history não existe"

**Solução**: A tabela é criada automaticamente na primeira chamada. Se necessário, execute:

```python
from langchain.memory.postgres import PostgresChatMessageHistory
from src.config.settings import get_settings

settings = get_settings()
history = PostgresChatMessageHistory(
    connection_string=settings.database_url,
    session_id="init",
    table_name="chat_history"
)
# Tabela será criada automaticamente
```

### Erro: "Memória muito lenta"

**Solução**: 
1. Verifique se índices foram criados
2. Considere usar ConversationSummaryMemory para sessões longas
3. Execute limpeza de mensagens antigas

### Erro: "Memória não persiste"

**Solução**:
1. Verifique conexão com PostgreSQL
2. Verifique se `DATABASE_URL` está correto
3. Verifique logs para erros de conexão

## Próximos Passos

- Implementar cache de memória em Redis
- Adicionar compressão de mensagens antigas
- Suporte a memória distribuída
- Integração com sistema de backup automático


# Tarefa 4.4: Memória Persistente

## Objetivo
Implementar memória persistente completa usando LangChain Memory com PostgreSQL para manter contexto entre sessões.

## Prioridade
Alta

## Estimativa
3 dias

## Responsável
Backend

---

## Instruções de Implementação

### 1. Implementar Integração com LangChain Memory

#### Verificar `src/agents/memory_manager.py` (já implementado na TAREFA_2.1):
```python
# Já existe PersistentMemoryManager
# Verificar se está completo
```

### 2. Configurar ConversationBufferMemory ou ConversationSummaryMemory

#### Atualizar `src/agents/memory_manager.py`:
```python
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.memory.postgres import PostgresChatMessageHistory

def _create_memory(self, use_summary: bool = False) -> ConversationBufferMemory:
    """Criar memória persistente."""
    try:
        connection_string = settings.database_url
        
        message_history = PostgresChatMessageHistory(
            connection_string=connection_string,
            session_id=self.session_id,
            table_name="chat_history"
        )
        
        if use_summary:
            # Usar summary memory para sessões longas
            memory = ConversationSummaryMemory(
                llm=self.llm,  # Precisa LLM para resumo
                chat_memory=message_history,
                return_messages=True,
                memory_key="chat_history"
            )
        else:
            memory = ConversationBufferMemory(
                chat_memory=message_history,
                return_messages=True,
                memory_key="chat_history"
            )
        
        return memory
    except Exception as e:
        logger.error(f"Erro ao criar memória: {e}")
        # Fallback
        return ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
```

### 3. Implementar Persistência em PostgreSQL

#### Verificar schema de tabela:
```sql
-- Criar tabela se não existir (PostgresChatMessageHistory cria automaticamente)
-- Verificar se tabela chat_history existe
```

#### Criar `scripts/create_memory_tables.sql`:
```sql
-- Tabela será criada automaticamente pelo PostgresChatMessageHistory
-- Mas podemos criar índices para performance

CREATE INDEX IF NOT EXISTS idx_chat_history_session_id 
ON chat_history(session_id);

CREATE INDEX IF NOT EXISTS idx_chat_history_created_at 
ON chat_history(created_at);
```

### 4. Implementar Recuperação de Contexto por Sessão

#### Adicionar método em `PersistentMemoryManager`:
```python
def get_conversation_summary(self) -> str:
    """Obter resumo da conversa."""
    try:
        memory_vars = self.memory.load_memory_variables({})
        messages = memory_vars.get("chat_history", [])
        
        if not messages:
            return "Nenhuma conversa anterior."
        
        # Criar resumo
        summary = f"Histórico com {len(messages)} mensagens:\n"
        for msg in messages[-5:]:  # Últimas 5 mensagens
            summary += f"- {msg.content[:100]}...\n"
        
        return summary
    except Exception as e:
        logger.error(f"Erro ao obter resumo: {e}")
        return ""
```

### 5. Implementar Limpeza Automática de Memória Antiga

#### Criar `src/agents/memory_cleanup.py`:
```python
"""Limpeza automática de memória antiga."""
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from src.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class MemoryCleanup:
    """Gerenciador de limpeza de memória."""
    
    def __init__(self, retention_days: int = 90):
        """Inicializar limpeza."""
        self.retention_days = retention_days
        self.engine = create_engine(settings.database_url)
    
    def cleanup_old_sessions(self) -> int:
        """Limpar sessões antigas."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        DELETE FROM chat_history 
                        WHERE created_at < :cutoff_date
                    """),
                    {"cutoff_date": cutoff_date}
                )
                deleted = result.rowcount
                conn.commit()
                
                logger.info(f"Limpeza concluída: {deleted} registros removidos")
                return deleted
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")
            return 0
```

### 6. Testar Persistência entre Sessões

#### Criar `tests/integration/test_memory_persistence.py`:
```python
"""Testes de persistência de memória."""
import pytest
from src.agents.memory_manager import PersistentMemoryManager

def test_memory_persistence():
    """Testar persistência entre sessões."""
    session_id = "test-persistence-123"
    
    # Criar memória e salvar
    memory1 = PersistentMemoryManager(session_id)
    memory1.save_context("Pergunta 1", "Resposta 1")
    
    # Criar nova instância e verificar
    memory2 = PersistentMemoryManager(session_id)
    history = memory2.load_memory_variables()
    
    assert len(history.get("chat_history", [])) > 0
```

### 7. Testar Múltiplas Sessões Simultâneas

#### Adicionar teste:
```python
def test_multiple_sessions():
    """Testar múltiplas sessões simultâneas."""
    session1 = PersistentMemoryManager("session-1")
    session2 = PersistentMemoryManager("session-2")
    
    session1.save_context("Q1", "A1")
    session2.save_context("Q2", "A2")
    
    hist1 = session1.load_memory_variables()
    hist2 = session2.load_memory_variables()
    
    assert len(hist1["chat_history"]) == 1
    assert len(hist2["chat_history"]) == 1
    assert hist1["chat_history"][0].content != hist2["chat_history"][0].content
```

### 8. Adicionar Métricas de Uso de Memória

#### Atualizar métricas:
```python
# Métricas de Memória
memory_sessions_total = Gauge(
    'memory_sessions_total',
    'Total de sessões ativas na memória'
)

memory_messages_total = Counter(
    'memory_messages_total',
    'Total de mensagens salvas na memória'
)
```

### 9. Documentar Gerenciamento de Memória

#### Criar `docs/agents/memory.md`:
```markdown
# Memória Persistente

## Uso

```python
from src.agents.memory_manager import PersistentMemoryManager

memory = PersistentMemoryManager(session_id="session-123")
memory.save_context("Pergunta", "Resposta")
history = memory.load_memory_variables()
```

## Limpeza

```python
from src.agents.memory_cleanup import MemoryCleanup

cleanup = MemoryCleanup(retention_days=90)
deleted = cleanup.cleanup_old_sessions()
```
```

---

## Checklist de Validação

- [ ] Integração com LangChain Memory implementada
- [ ] ConversationBufferMemory configurado
- [ ] ConversationSummaryMemory configurado (opcional)
- [ ] Persistência em PostgreSQL funcionando
- [ ] Recuperação de contexto por sessão implementada
- [ ] Limpeza automática de memória antiga implementada
- [ ] Testes de persistência entre sessões passando
- [ ] Testes de múltiplas sessões simultâneas passando
- [ ] Métricas de uso de memória adicionadas
- [ ] Documentação criada

---

## Comandos de Teste

```bash
# Testar persistência
python -m pytest tests/integration/test_memory_persistence.py

# Executar limpeza
python -c "from src.agents.memory_cleanup import MemoryCleanup; MemoryCleanup().cleanup_old_sessions()"
```


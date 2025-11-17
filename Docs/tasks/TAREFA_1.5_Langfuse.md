# Tarefa 1.5: Setup do Langfuse

## Objetivo
Configurar e integrar Langfuse para observabilidade completa de chamadas LLM.

## Prioridade
Alta

## Estimativa
1 dia

## Responsável
Backend/DevOps

---

## Instruções de Implementação

### 1. Configurar Langfuse no docker-compose

#### Já incluído na Tarefa 1.2, verificar se está correto:
```yaml
langfuse:
  image: langfuse/langfuse:latest
  container_name: rfp-agents-langfuse
  ports:
    - "3000:3000"
  environment:
    - DATABASE_URL=postgresql://postgres:postgres@langfuse-db:5432/langfuse
    - NEXTAUTH_SECRET=${LANGFUSE_SECRET_KEY}
    - SALT=${LANGFUSE_SECRET_KEY}
```

### 2. Configurar Variáveis de Ambiente

#### Adicionar ao `.env.example`:
```env
# Langfuse
LANGFUSE_URL=http://localhost:3000
LANGFUSE_SECRET_KEY=your-secret-key-here
LANGFUSE_PUBLIC_KEY=your-public-key-here
```

#### Obter keys após subir o Langfuse:
```bash
# Acessar http://localhost:3000
# Criar conta e obter keys em Settings > API Keys
```

### 3. Integrar Langfuse SDK na Aplicação

#### Criar `src/utils/langfuse_client.py`:
```python
"""Cliente Langfuse para observabilidade."""
from langfuse import Langfuse
from langfuse.decorators import langfuse_context, observe
from typing import Optional
from src.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class LangfuseClient:
    """Cliente Langfuse singleton."""
    
    _instance: Optional['LangfuseClient'] = None
    _client: Optional[Langfuse] = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializar cliente Langfuse."""
        if self._client is None:
            try:
                self._client = Langfuse(
                    public_key=settings.langfuse_public_key,
                    secret_key=settings.langfuse_secret_key,
                    host=settings.langfuse_url,
                )
                logger.info("Langfuse client inicializado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao inicializar Langfuse: {e}")
                self._client = None
    
    @property
    def client(self) -> Optional[Langfuse]:
        """Obter cliente Langfuse."""
        return self._client
    
    def is_enabled(self) -> bool:
        """Verificar se Langfuse está habilitado."""
        return self._client is not None


# Instância global
langfuse_client = LangfuseClient()
```

#### Adicionar ao `src/config/settings.py`:
```python
class Settings(BaseSettings):
    # ... outras configurações
    
    langfuse_url: str = Field(default="http://localhost:3000", env="LANGFUSE_URL")
    langfuse_public_key: Optional[str] = Field(default=None, env="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: Optional[str] = Field(default=None, env="LANGFUSE_SECRET_KEY")
```

### 4. Criar Wrapper para Rastreamento de Chamadas LLM

#### Criar `src/utils/langfuse_wrapper.py`:
```python
"""Wrapper para rastreamento de chamadas LLM com Langfuse."""
from typing import Optional, Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.callbacks import BaseCallbackHandler
from langfuse.callback import CallbackHandler
from src.utils.langfuse_client import langfuse_client
import logging

logger = logging.getLogger(__name__)


class LangfuseCallbackHandler(CallbackHandler):
    """Callback handler para Langfuse."""
    
    def __init__(self, session_id: Optional[str] = None, **kwargs):
        """Inicializar handler."""
        if langfuse_client.is_enabled():
            super().__init__(
                public_key=langfuse_client.client.public_key,
                secret_key=langfuse_client.client.secret_key,
                host=langfuse_client.client.host,
                session_id=session_id,
                **kwargs
            )
        else:
            logger.warning("Langfuse não está habilitado")
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: list[str], **kwargs) -> None:
        """Chamado quando LLM inicia."""
        if langfuse_client.is_enabled():
            super().on_llm_start(serialized, prompts, **kwargs)
    
    def on_llm_end(self, response, **kwargs) -> None:
        """Chamado quando LLM termina."""
        if langfuse_client.is_enabled():
            super().on_llm_end(response, **kwargs)
    
    def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Chamado quando LLM tem erro."""
        if langfuse_client.is_enabled():
            super().on_llm_error(error, **kwargs)


def get_langfuse_callback(session_id: Optional[str] = None) -> Optional[LangfuseCallbackHandler]:
    """Obter callback handler do Langfuse."""
    if langfuse_client.is_enabled():
        return LangfuseCallbackHandler(session_id=session_id)
    return None
```

#### Criar decorator para rastreamento:
```python
# Adicionar ao langfuse_wrapper.py
from langfuse.decorators import observe, langfuse_context

def track_llm_call(func):
    """Decorator para rastrear chamadas LLM."""
    @observe(name=func.__name__)
    def wrapper(*args, **kwargs):
        # Adicionar metadados
        langfuse_context.update_current_trace(
            name=func.__name__,
            metadata={
                "function": func.__name__,
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys())
            }
        )
        return func(*args, **kwargs)
    return wrapper
```

### 5. Integrar com LLM Factory

#### Atualizar `src/utils/llm_factory.py`:
```python
from src.utils.langfuse_wrapper import get_langfuse_callback

class LLMFactory:
    def create_openai_llm(self, session_id: Optional[str] = None) -> ChatOpenAI:
        """Criar LLM OpenAI com rastreamento."""
        llm = ChatOpenAI(
            model=self.config.openai_model,
            temperature=self.config.openai_temperature,
            max_tokens=self.config.openai_max_tokens,
            api_key=self.config.openai_api_key,
        )
        
        # Adicionar callback do Langfuse
        callback = get_langfuse_callback(session_id=session_id)
        if callback:
            llm.callbacks = [callback]
        
        return llm
```

### 6. Testar Rastreamento Básico

#### Criar `tests/test_langfuse.py`:
```python
"""Testes para integração Langfuse."""
import pytest
from src.utils.langfuse_client import langfuse_client
from src.utils.langfuse_wrapper import get_langfuse_callback
from langchain_core.messages import HumanMessage


def test_langfuse_client_initialization():
    """Testar inicialização do cliente."""
    assert langfuse_client is not None


def test_langfuse_callback_creation():
    """Testar criação de callback."""
    callback = get_langfuse_callback(session_id="test-session")
    # Se Langfuse estiver configurado, callback não deve ser None
    # Se não estiver, callback será None (modo graceful)
    assert callback is None or hasattr(callback, 'on_llm_start')


@pytest.mark.integration
def test_langfuse_tracking():
    """Testar rastreamento de chamada LLM."""
    from src.utils.llm_factory import LLMFactory
    
    factory = LLMFactory()
    llm = factory.create_openai_llm(session_id="test")
    
    messages = [HumanMessage(content="Hello")]
    response = llm.invoke(messages)
    
    assert response is not None
    # Verificar no dashboard do Langfuse se a chamada foi rastreada
```

### 7. Configurar Dashboards Iniciais no Langfuse

#### Após subir o Langfuse:
1. Acessar http://localhost:3000
2. Criar conta/login
3. Ir em **Traces** para ver chamadas
4. Ir em **Scores** para configurar avaliações
5. Ir em **Datasets** para criar datasets de teste

### 8. Documentar Uso e Acesso

#### Adicionar ao README.md:
```markdown
## Langfuse - Observabilidade de LLMs

### Acesso
- URL: http://localhost:3000
- Credenciais: Criar conta na primeira execução

### Configuração
1. Subir serviços: `docker-compose up -d langfuse langfuse-db`
2. Acessar http://localhost:3000
3. Criar conta
4. Obter API keys em Settings > API Keys
5. Adicionar ao `.env`:
```env
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
```

### Uso no Código
```python
from src.utils.llm_factory import LLMFactory

factory = LLMFactory()
llm = factory.create_openai_llm(session_id="session-123")
# Chamadas serão automaticamente rastreadas
```

### Visualizar Traces
- Acessar http://localhost:3000/traces
- Filtrar por session_id, modelo, etc.
- Ver custos, latência, tokens usados
```

---

## Checklist de Validação

- [ ] Langfuse configurado no docker-compose
- [ ] Variáveis de ambiente configuradas
- [ ] Cliente Langfuse criado e testado
- [ ] Wrapper para rastreamento criado
- [ ] Integração com LLM Factory funcionando
- [ ] Testes criados e passando
- [ ] Dashboards acessíveis
- [ ] Documentação atualizada
- [ ] Testar: Chamada LLM deve aparecer no Langfuse

---

## Comandos de Teste

```bash
# Subir Langfuse
docker-compose up -d langfuse langfuse-db

# Ver logs
docker-compose logs -f langfuse

# Testar conexão
curl http://localhost:3000/api/public/health

# Executar teste
pytest tests/test_langfuse.py -v
```

---

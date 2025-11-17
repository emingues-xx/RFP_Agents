# Tarefa 1.4: Configuração de LLM Providers

## Objetivo
Criar módulo de configuração e abstração para múltiplos LLM providers com suporte a fallback.

## Prioridade
Alta

## Estimativa
1 dia

## Responsável
Backend

---

## Instruções de Implementação

### 1. Criar Módulo de Configuração de LLM Providers

#### Criar `src/config/llm_config.py`:
```python
"""Configuração de LLM Providers."""
from typing import Literal, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class LLMConfig(BaseSettings):
    """Configuração de LLM Providers."""
    
    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    openai_max_tokens: int = Field(default=2000, env="OPENAI_MAX_TOKENS")
    
    # Anthropic
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022", env="ANTHROPIC_MODEL")
    anthropic_temperature: float = Field(default=0.7, env="ANTHROPIC_TEMPERATURE")
    anthropic_max_tokens: int = Field(default=2000, env="ANTHROPIC_MAX_TOKENS")
    
    # Provider padrão
    default_provider: Literal["openai", "anthropic"] = Field(
        default="openai", env="DEFAULT_LLM_PROVIDER"
    )
    
    # Fallback
    enable_fallback: bool = Field(default=True, env="ENABLE_LLM_FALLBACK")
    fallback_provider: Literal["openai", "anthropic"] = Field(
        default="anthropic", env="FALLBACK_LLM_PROVIDER"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
```

### 2. Implementar Abstração para Múltiplos Providers

#### Criar `src/utils/llm_factory.py`:
```python
"""Factory para criação de LLMs."""
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from src.config.llm_config import LLMConfig
import logging

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory para criar instâncias de LLM."""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Inicializar factory com configuração."""
        self.config = config or LLMConfig()
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validar configuração dos providers."""
        if self.config.default_provider == "openai" and not self.config.openai_api_key:
            raise ValueError("OpenAI API key não configurada")
        if self.config.default_provider == "anthropic" and not self.config.anthropic_api_key:
            raise ValueError("Anthropic API key não configurada")
    
    def create_openai_llm(self) -> ChatOpenAI:
        """Criar instância do OpenAI LLM."""
        if not self.config.openai_api_key:
            raise ValueError("OpenAI API key não configurada")
        
        return ChatOpenAI(
            model=self.config.openai_model,
            temperature=self.config.openai_temperature,
            max_tokens=self.config.openai_max_tokens,
            api_key=self.config.openai_api_key,
        )
    
    def create_anthropic_llm(self) -> ChatAnthropic:
        """Criar instância do Anthropic LLM."""
        if not self.config.anthropic_api_key:
            raise ValueError("Anthropic API key não configurada")
        
        return ChatAnthropic(
            model=self.config.anthropic_model,
            temperature=self.config.anthropic_temperature,
            max_tokens=self.config.anthropic_max_tokens,
            api_key=self.config.anthropic_api_key,
        )
    
    def get_default_llm(self) -> BaseChatModel:
        """Obter LLM padrão configurado."""
        try:
            if self.config.default_provider == "openai":
                return self.create_openai_llm()
            elif self.config.default_provider == "anthropic":
                return self.create_anthropic_llm()
            else:
                raise ValueError(f"Provider desconhecido: {self.config.default_provider}")
        except Exception as e:
            logger.error(f"Erro ao criar LLM padrão: {e}")
            if self.config.enable_fallback:
                return self.get_fallback_llm()
            raise
    
    def get_fallback_llm(self) -> BaseChatModel:
        """Obter LLM de fallback."""
        try:
            if self.config.fallback_provider == "openai":
                return self.create_openai_llm()
            elif self.config.fallback_provider == "anthropic":
                return self.create_anthropic_llm()
            else:
                raise ValueError(f"Provider de fallback desconhecido: {self.config.fallback_provider}")
        except Exception as e:
            logger.error(f"Erro ao criar LLM de fallback: {e}")
            raise
    
    def get_llm_by_provider(self, provider: str) -> BaseChatModel:
        """Obter LLM por provider específico."""
        if provider == "openai":
            return self.create_openai_llm()
        elif provider == "anthropic":
            return self.create_anthropic_llm()
        else:
            raise ValueError(f"Provider desconhecido: {provider}")
```

### 3. Implementar Fallback Automático

#### Criar `src/utils/llm_with_fallback.py`:
```python
"""Wrapper para LLM com fallback automático."""
from typing import Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult
from src.utils.llm_factory import LLMFactory
import logging

logger = logging.getLogger(__name__)


class LLMWithFallback:
    """Wrapper de LLM com fallback automático."""
    
    def __init__(self, factory: Optional[LLMFactory] = None):
        """Inicializar wrapper."""
        self.factory = factory or LLMFactory()
        self.primary_llm: Optional[BaseChatModel] = None
        self.fallback_llm: Optional[BaseChatModel] = None
        self._initialize_llms()
    
    def _initialize_llms(self) -> None:
        """Inicializar LLMs primário e de fallback."""
        try:
            self.primary_llm = self.factory.get_default_llm()
            logger.info(f"LLM primário configurado: {self.factory.config.default_provider}")
        except Exception as e:
            logger.warning(f"Erro ao configurar LLM primário: {e}")
            self.primary_llm = None
        
        try:
            self.fallback_llm = self.factory.get_fallback_llm()
            logger.info(f"LLM de fallback configurado: {self.factory.config.fallback_provider}")
        except Exception as e:
            logger.warning(f"Erro ao configurar LLM de fallback: {e}")
            self.fallback_llm = None
    
    def invoke(self, messages: list[BaseMessage], **kwargs) -> LLMResult:
        """Invoke com fallback automático."""
        # Tentar LLM primário
        if self.primary_llm:
            try:
                return self.primary_llm.invoke(messages, **kwargs)
            except Exception as e:
                logger.warning(f"Erro no LLM primário: {e}, tentando fallback...")
        
        # Tentar fallback
        if self.fallback_llm:
            try:
                return self.fallback_llm.invoke(messages, **kwargs)
            except Exception as e:
                logger.error(f"Erro no LLM de fallback: {e}")
                raise
        
        raise RuntimeError("Nenhum LLM disponível")
    
    def get_current_llm(self) -> BaseChatModel:
        """Obter LLM atual (primário se disponível, senão fallback)."""
        return self.primary_llm or self.fallback_llm
```

### 4. Criar Sistema de Configuração por Variáveis de Ambiente

#### Atualizar `.env.example`:
```env
# LLM Providers
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_TEMPERATURE=0.7
ANTHROPIC_MAX_TOKENS=2000

# Provider padrão
DEFAULT_LLM_PROVIDER=openai

# Fallback
ENABLE_LLM_FALLBACK=true
FALLBACK_LLM_PROVIDER=anthropic
```

### 5. Testar Conexão com Ambos Providers

#### Criar `tests/test_llm_providers.py`:
```python
"""Testes para LLM Providers."""
import pytest
from src.utils.llm_factory import LLMFactory
from src.utils.llm_with_fallback import LLMWithFallback
from langchain_core.messages import HumanMessage


@pytest.fixture
def llm_factory():
    """Fixture para LLM Factory."""
    return LLMFactory()


@pytest.fixture
def llm_with_fallback():
    """Fixture para LLM com fallback."""
    return LLMWithFallback()


def test_openai_llm_creation(llm_factory):
    """Testar criação de LLM OpenAI."""
    llm = llm_factory.create_openai_llm()
    assert llm is not None
    assert llm.model_name == llm_factory.config.openai_model


def test_anthropic_llm_creation(llm_factory):
    """Testar criação de LLM Anthropic."""
    llm = llm_factory.create_anthropic_llm()
    assert llm is not None
    assert llm.model == llm_factory.config.anthropic_model


def test_default_llm(llm_factory):
    """Testar obtenção de LLM padrão."""
    llm = llm_factory.get_default_llm()
    assert llm is not None


def test_fallback_llm(llm_factory):
    """Testar obtenção de LLM de fallback."""
    llm = llm_factory.get_fallback_llm()
    assert llm is not None


@pytest.mark.asyncio
async def test_llm_invoke(llm_with_fallback):
    """Testar invoke do LLM."""
    messages = [HumanMessage(content="Hello, world!")]
    response = llm_with_fallback.invoke(messages)
    assert response is not None
    assert hasattr(response, 'content')


def test_llm_fallback_on_error(llm_with_fallback):
    """Testar fallback quando LLM primário falha."""
    # Simular erro no primário
    llm_with_fallback.primary_llm = None
    
    messages = [HumanMessage(content="Test")]
    if llm_with_fallback.fallback_llm:
        response = llm_with_fallback.invoke(messages)
        assert response is not None
```

### 6. Documentar Configuração de API Keys

#### Adicionar ao README.md:
```markdown
## Configuração de LLM Providers

### OpenAI
1. Obter API key em: https://platform.openai.com/api-keys
2. Adicionar ao `.env`:
```env
OPENAI_API_KEY=sk-...
```

### Anthropic
1. Obter API key em: https://console.anthropic.com/
2. Adicionar ao `.env`:
```env
ANTHROPIC_API_KEY=sk-ant-...
```

### Configuração de Provider Padrão
```env
DEFAULT_LLM_PROVIDER=openai  # ou anthropic
ENABLE_LLM_FALLBACK=true
FALLBACK_LLM_PROVIDER=anthropic
```

### Uso no Código
```python
from src.utils.llm_factory import LLMFactory
from src.utils.llm_with_fallback import LLMWithFallback

# Criar factory
factory = LLMFactory()

# Obter LLM padrão
llm = factory.get_default_llm()

# Ou usar com fallback automático
llm_wrapper = LLMWithFallback()
response = llm_wrapper.invoke([HumanMessage(content="Hello")])
```
```

---

## Checklist de Validação

- [ ] Módulo de configuração criado (`llm_config.py`)
- [ ] Factory implementado (`llm_factory.py`)
- [ ] Wrapper com fallback implementado (`llm_with_fallback.py`)
- [ ] Variáveis de ambiente documentadas
- [ ] Testes unitários criados
- [ ] README atualizado
- [ ] Testar: Conexão com OpenAI funciona
- [ ] Testar: Conexão com Anthropic funciona
- [ ] Testar: Fallback funciona quando primário falha

---

## Comandos de Teste

```bash
# Testar configuração
python -c "from src.config.llm_config import LLMConfig; c = LLMConfig(); print(c.default_provider)"

# Testar factory
python -c "from src.utils.llm_factory import LLMFactory; f = LLMFactory(); print(f.get_default_llm())"

# Executar testes
pytest tests/test_llm_providers.py -v
```

---


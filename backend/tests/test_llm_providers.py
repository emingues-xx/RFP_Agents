"""Testes para LLM Providers."""
import pytest
from unittest.mock import Mock, patch
from src.utils.llm_factory import LLMFactory
from src.utils.llm_with_fallback import LLMWithFallback
from src.config.llm_config import LLMConfig
from langchain_core.messages import HumanMessage


@pytest.fixture
def mock_openai_key():
    """Fixture para mock de OpenAI API key."""
    return "sk-test-openai-key"


@pytest.fixture
def mock_anthropic_key():
    """Fixture para mock de Anthropic API key."""
    return "sk-ant-test-anthropic-key"


@pytest.fixture
def llm_config_openai(mock_openai_key):
    """Fixture para LLM Config com OpenAI."""
    return LLMConfig(
        openai_api_key=mock_openai_key,
        default_provider="openai",
        enable_fallback=False
    )


@pytest.fixture
def llm_config_anthropic(mock_anthropic_key):
    """Fixture para LLM Config com Anthropic."""
    return LLMConfig(
        anthropic_api_key=mock_anthropic_key,
        default_provider="anthropic",
        enable_fallback=False
    )


@pytest.fixture
def llm_config_with_fallback(mock_openai_key, mock_anthropic_key):
    """Fixture para LLM Config com fallback."""
    return LLMConfig(
        openai_api_key=mock_openai_key,
        anthropic_api_key=mock_anthropic_key,
        default_provider="openai",
        fallback_provider="anthropic",
        enable_fallback=True
    )


@pytest.fixture
def llm_factory_openai(llm_config_openai):
    """Fixture para LLM Factory com OpenAI."""
    with patch('src.utils.llm_factory.ChatOpenAI'):
        return LLMFactory(config=llm_config_openai)


@pytest.fixture
def llm_factory_anthropic(llm_config_anthropic):
    """Fixture para LLM Factory com Anthropic."""
    with patch('src.utils.llm_factory.ChatAnthropic'):
        return LLMFactory(config=llm_config_anthropic)


@pytest.fixture
def llm_factory_with_fallback(llm_config_with_fallback):
    """Fixture para LLM Factory com fallback."""
    with patch('src.utils.llm_factory.ChatOpenAI'), \
         patch('src.utils.llm_factory.ChatAnthropic'):
        return LLMFactory(config=llm_config_with_fallback)


def test_llm_config_defaults():
    """Testar valores padrão da configuração."""
    config = LLMConfig()
    assert config.default_provider == "openai"
    assert config.enable_fallback is True
    assert config.fallback_provider == "anthropic"
    assert config.openai_temperature == 0.7
    assert config.anthropic_temperature == 0.7


def test_llm_config_openai_settings(llm_config_openai):
    """Testar configuração OpenAI."""
    assert llm_config_openai.openai_api_key is not None
    assert llm_config_openai.default_provider == "openai"
    assert llm_config_openai.openai_model == "gpt-4-turbo-preview"


def test_llm_config_anthropic_settings(llm_config_anthropic):
    """Testar configuração Anthropic."""
    assert llm_config_anthropic.anthropic_api_key is not None
    assert llm_config_anthropic.default_provider == "anthropic"
    assert llm_config_anthropic.anthropic_model == "claude-3-5-sonnet-20241022"


@patch('src.utils.llm_factory.ChatOpenAI')
def test_create_openai_llm(mock_chat_openai, llm_config_openai):
    """Testar criação de LLM OpenAI."""
    factory = LLMFactory(config=llm_config_openai)
    llm = factory.create_openai_llm()
    assert llm is not None
    mock_chat_openai.assert_called_once()


@patch('src.utils.llm_factory.ChatAnthropic')
def test_create_anthropic_llm(mock_chat_anthropic, llm_config_anthropic):
    """Testar criação de LLM Anthropic."""
    factory = LLMFactory(config=llm_config_anthropic)
    llm = factory.create_anthropic_llm()
    assert llm is not None
    mock_chat_anthropic.assert_called_once()


def test_create_openai_llm_without_key():
    """Testar erro ao criar OpenAI LLM sem API key."""
    config = LLMConfig(openai_api_key=None)
    factory = LLMFactory(config=config)
    with pytest.raises(ValueError, match="OpenAI API key não configurada"):
        factory.create_openai_llm()


def test_create_anthropic_llm_without_key():
    """Testar erro ao criar Anthropic LLM sem API key."""
    config = LLMConfig(anthropic_api_key=None)
    factory = LLMFactory(config=config)
    with pytest.raises(ValueError, match="Anthropic API key não configurada"):
        factory.create_anthropic_llm()


@patch('src.utils.llm_factory.ChatOpenAI')
def test_get_default_llm_openai(mock_chat_openai, llm_config_openai):
    """Testar obtenção de LLM padrão (OpenAI)."""
    factory = LLMFactory(config=llm_config_openai)
    llm = factory.get_default_llm()
    assert llm is not None
    mock_chat_openai.assert_called_once()


@patch('src.utils.llm_factory.ChatAnthropic')
def test_get_default_llm_anthropic(mock_chat_anthropic, llm_config_anthropic):
    """Testar obtenção de LLM padrão (Anthropic)."""
    factory = LLMFactory(config=llm_config_anthropic)
    llm = factory.get_default_llm()
    assert llm is not None
    mock_chat_anthropic.assert_called_once()


@patch('src.utils.llm_factory.ChatAnthropic')
def test_get_fallback_llm(mock_chat_anthropic, llm_config_with_fallback):
    """Testar obtenção de LLM de fallback."""
    factory = LLMFactory(config=llm_config_with_fallback)
    llm = factory.get_fallback_llm()
    assert llm is not None
    mock_chat_anthropic.assert_called_once()


@patch('src.utils.llm_factory.ChatOpenAI')
def test_get_llm_by_provider_openai(mock_chat_openai, llm_config_with_fallback):
    """Testar obtenção de LLM por provider específico (OpenAI)."""
    factory = LLMFactory(config=llm_config_with_fallback)
    llm = factory.get_llm_by_provider("openai")
    assert llm is not None
    mock_chat_openai.assert_called_once()


@patch('src.utils.llm_factory.ChatAnthropic')
def test_get_llm_by_provider_anthropic(mock_chat_anthropic, llm_config_with_fallback):
    """Testar obtenção de LLM por provider específico (Anthropic)."""
    factory = LLMFactory(config=llm_config_with_fallback)
    llm = factory.get_llm_by_provider("anthropic")
    assert llm is not None
    mock_chat_anthropic.assert_called_once()


def test_get_llm_by_provider_invalid(llm_config_with_fallback):
    """Testar erro ao obter LLM com provider inválido."""
    factory = LLMFactory(config=llm_config_with_fallback)
    with pytest.raises(ValueError, match="Provider desconhecido"):
        factory.get_llm_by_provider("invalid_provider")


@patch('src.utils.llm_factory.LLMFactory')
def test_llm_with_fallback_initialization(mock_factory_class, llm_config_with_fallback):
    """Testar inicialização do LLM com fallback."""
    mock_factory = Mock()
    mock_factory.config = llm_config_with_fallback
    mock_factory.get_default_llm.return_value = Mock()
    mock_factory.get_fallback_llm.return_value = Mock()
    mock_factory_class.return_value = mock_factory
    
    wrapper = LLMWithFallback()
    assert wrapper.factory is not None
    assert wrapper.primary_llm is not None
    assert wrapper.fallback_llm is not None


@patch('src.utils.llm_factory.LLMFactory')
def test_llm_with_fallback_invoke_primary(mock_factory_class, llm_config_with_fallback):
    """Testar invoke usando LLM primário."""
    mock_primary_llm = Mock()
    mock_primary_llm.invoke.return_value = Mock(content="Response from primary")
    
    mock_factory = Mock()
    mock_factory.config = llm_config_with_fallback
    mock_factory.get_default_llm.return_value = mock_primary_llm
    mock_factory.get_fallback_llm.return_value = Mock()
    mock_factory_class.return_value = mock_factory
    
    wrapper = LLMWithFallback()
    messages = [HumanMessage(content="Hello")]
    response = wrapper.invoke(messages)
    
    assert response is not None
    mock_primary_llm.invoke.assert_called_once_with(messages)


@patch('src.utils.llm_factory.LLMFactory')
def test_llm_with_fallback_invoke_fallback(mock_factory_class, llm_config_with_fallback):
    """Testar fallback quando LLM primário falha."""
    mock_primary_llm = Mock()
    mock_primary_llm.invoke.side_effect = Exception("Primary LLM error")
    
    mock_fallback_llm = Mock()
    mock_fallback_llm.invoke.return_value = Mock(content="Response from fallback")
    
    mock_factory = Mock()
    mock_factory.config = llm_config_with_fallback
    mock_factory.get_default_llm.return_value = mock_primary_llm
    mock_factory.get_fallback_llm.return_value = mock_fallback_llm
    mock_factory_class.return_value = mock_factory
    
    wrapper = LLMWithFallback()
    messages = [HumanMessage(content="Hello")]
    response = wrapper.invoke(messages)
    
    assert response is not None
    mock_primary_llm.invoke.assert_called_once()
    mock_fallback_llm.invoke.assert_called_once_with(messages)


@patch('src.utils.llm_factory.LLMFactory')
def test_llm_with_fallback_no_llm_available(mock_factory_class):
    """Testar erro quando nenhum LLM está disponível."""
    mock_factory = Mock()
    mock_factory.get_default_llm.return_value = None
    mock_factory.get_fallback_llm.return_value = None
    mock_factory_class.return_value = mock_factory
    
    wrapper = LLMWithFallback()
    wrapper.primary_llm = None
    wrapper.fallback_llm = None
    
    messages = [HumanMessage(content="Hello")]
    with pytest.raises(RuntimeError, match="Nenhum LLM disponível"):
        wrapper.invoke(messages)


@patch('src.utils.llm_factory.LLMFactory')
def test_get_current_llm(mock_factory_class, llm_config_with_fallback):
    """Testar obtenção de LLM atual."""
    mock_primary_llm = Mock()
    mock_fallback_llm = Mock()
    
    mock_factory = Mock()
    mock_factory.config = llm_config_with_fallback
    mock_factory.get_default_llm.return_value = mock_primary_llm
    mock_factory.get_fallback_llm.return_value = mock_fallback_llm
    mock_factory_class.return_value = mock_factory
    
    wrapper = LLMWithFallback()
    current_llm = wrapper.get_current_llm()
    
    assert current_llm == mock_primary_llm
    
    # Testar quando primário não está disponível
    wrapper.primary_llm = None
    current_llm = wrapper.get_current_llm()
    assert current_llm == mock_fallback_llm


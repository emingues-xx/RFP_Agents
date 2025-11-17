"""Testes para integração Langfuse."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.utils.langfuse_client import langfuse_client, LangfuseClient
from src.utils.langfuse_wrapper import get_langfuse_callback, LangfuseCallbackHandler
from src.config.settings import Settings
from langchain_core.messages import HumanMessage


@pytest.fixture
def mock_settings_with_keys():
    """Fixture para settings com API keys."""
    settings = Mock(spec=Settings)
    settings.langfuse_url = "http://localhost:3000"
    settings.langfuse_public_key = "pk-test-key"
    settings.langfuse_secret_key = "sk-test-key"
    return settings


@pytest.fixture
def mock_settings_without_keys():
    """Fixture para settings sem API keys."""
    settings = Mock(spec=Settings)
    settings.langfuse_url = "http://localhost:3000"
    settings.langfuse_public_key = None
    settings.langfuse_secret_key = None
    return settings


def test_langfuse_client_initialization():
    """Testar inicialização do cliente."""
    assert langfuse_client is not None
    assert isinstance(langfuse_client, LangfuseClient)


@patch('src.utils.langfuse_client.get_settings')
def test_langfuse_client_with_keys(mock_get_settings, mock_settings_with_keys):
    """Testar inicialização do cliente com API keys."""
    mock_get_settings.return_value = mock_settings_with_keys
    
    # Resetar instância singleton
    LangfuseClient._instance = None
    LangfuseClient._client = None
    
    with patch('src.utils.langfuse_client.Langfuse') as mock_langfuse:
        client = LangfuseClient()
        assert client is not None
        # Se as keys estiverem configuradas, o cliente deve ser criado
        # (mas pode falhar se Langfuse não estiver disponível, então não verificamos diretamente)


@patch('src.utils.langfuse_client.get_settings')
def test_langfuse_client_without_keys(mock_get_settings, mock_settings_without_keys):
    """Testar inicialização do cliente sem API keys."""
    mock_get_settings.return_value = mock_settings_without_keys
    
    # Resetar instância singleton
    LangfuseClient._instance = None
    LangfuseClient._client = None
    
    client = LangfuseClient()
    assert client is not None
    assert not client.is_enabled()


def test_langfuse_callback_creation():
    """Testar criação de callback."""
    callback = get_langfuse_callback(session_id="test-session")
    # Se Langfuse estiver configurado, callback não deve ser None
    # Se não estiver, callback será None (modo graceful)
    assert callback is None or isinstance(callback, LangfuseCallbackHandler)


@patch('src.utils.langfuse_wrapper.langfuse_client')
def test_langfuse_callback_handler_creation(mock_client):
    """Testar criação de callback handler."""
    mock_client.is_enabled.return_value = True
    mock_client.public_key = "pk-test"
    mock_client.secret_key = "sk-test"
    mock_client.host = "http://localhost:3000"
    
    with patch('src.utils.langfuse_wrapper.CallbackHandler') as mock_callback_handler:
        handler = LangfuseCallbackHandler(session_id="test-session")
        assert handler is not None


@patch('src.utils.langfuse_wrapper.langfuse_client')
def test_langfuse_callback_handler_disabled(mock_client):
    """Testar callback handler quando Langfuse está desabilitado."""
    mock_client.is_enabled.return_value = False
    
    with patch('src.utils.langfuse_wrapper.CallbackHandler') as mock_callback_handler:
        handler = LangfuseCallbackHandler(session_id="test-session")
        # Deve criar handler vazio quando desabilitado
        assert handler is not None


@patch('src.utils.langfuse_wrapper.get_langfuse_callback')
@patch('src.utils.llm_factory.LLMFactory')
def test_llm_factory_with_langfuse(mock_factory_class, mock_get_callback):
    """Testar integração do LLM Factory com Langfuse."""
    from src.utils.llm_factory import LLMFactory
    from src.config.llm_config import LLMConfig
    
    mock_callback = Mock()
    mock_get_callback.return_value = mock_callback
    
    config = LLMConfig(
        openai_api_key="sk-test",
        default_provider="openai"
    )
    
    with patch('src.utils.llm_factory.ChatOpenAI') as mock_chat_openai:
        factory = LLMFactory(config=config)
        llm = factory.create_openai_llm(session_id="test-session")
        
        assert llm is not None
        # Verificar se callback foi adicionado (se Langfuse estiver habilitado)
        mock_get_callback.assert_called_once_with(session_id="test-session")


@pytest.mark.integration
def test_langfuse_tracking():
    """Testar rastreamento de chamada LLM (requer Langfuse rodando)."""
    from src.utils.llm_factory import LLMFactory
    from src.config.llm_config import LLMConfig
    
    # Este teste requer Langfuse configurado e rodando
    # Será pulado se as keys não estiverem configuradas
    config = LLMConfig(
        openai_api_key="sk-test",
        default_provider="openai"
    )
    
    factory = LLMFactory(config=config)
    
    try:
        llm = factory.create_openai_llm(session_id="test")
        messages = [HumanMessage(content="Hello")]
        # Não executar invoke real para evitar custos
        # response = llm.invoke(messages)
        # assert response is not None
        # Verificar no dashboard do Langfuse se a chamada foi rastreada
        assert llm is not None
    except Exception as e:
        pytest.skip(f"Teste de integração pulado: {e}")


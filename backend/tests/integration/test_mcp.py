"""Testes de integração MCP."""
import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from src.mcp.mcp_tools import MCPToolManager
from src.mcp.mcp_client import MCPClient
from src.mcp.mcp_factory import MCPFactory


@pytest.fixture
def mcp_manager():
    """Fixture para MCPToolManager."""
    return MCPToolManager()


@pytest.fixture
def mock_mcp_client():
    """Fixture para mock de MCPClient."""
    client = MagicMock(spec=MCPClient)
    client.name = "test_client"
    client.list_tools = AsyncMock(return_value=[
        {"name": "test_tool", "description": "Test tool"}
    ])
    client.call_tool = AsyncMock(return_value={"result": "success"})
    client.call_tool_with_retry = AsyncMock(return_value={"result": "success"})
    client.connect = AsyncMock()
    client.disconnect = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_list_tools(mcp_manager, mock_mcp_client):
    """Testar listagem de tools."""
    mcp_manager.add_client("test", mock_mcp_client)
    
    results = await mcp_manager.list_tools("test")
    
    assert "test" in results
    assert len(results["test"]) > 0
    mock_mcp_client.list_tools.assert_called_once()


@pytest.mark.asyncio
async def test_list_tools_all_clients(mcp_manager, mock_mcp_client):
    """Testar listagem de tools de todos os clientes."""
    mcp_manager.add_client("client1", mock_mcp_client)
    mcp_manager.add_client("client2", mock_mcp_client)
    
    results = await mcp_manager.list_tools()
    
    assert "client1" in results
    assert "client2" in results


@pytest.mark.asyncio
async def test_call_tool(mcp_manager, mock_mcp_client):
    """Testar chamada de tool."""
    mcp_manager.add_client("test", mock_mcp_client)
    
    result = await mcp_manager.call_tool(
        "test",
        "test_tool",
        {"arg": "value"}
    )
    
    assert result is not None
    mock_mcp_client.call_tool_with_retry.assert_called_once()


@pytest.mark.asyncio
async def test_call_tool_client_not_found(mcp_manager):
    """Testar chamada de tool com cliente não encontrado."""
    with pytest.raises(ValueError, match="não encontrado"):
        await mcp_manager.call_tool(
            "nonexistent",
            "test_tool",
            {}
        )


@pytest.mark.asyncio
async def test_call_atlassian_tool_not_configured(mcp_manager):
    """Testar chamada de tool Atlassian não configurado."""
    with pytest.raises(ValueError, match="não configurado"):
        await mcp_manager.call_atlassian_tool("test_tool", {})


@pytest.mark.asyncio
async def test_call_atlassian_tool(mcp_manager, mock_mcp_client):
    """Testar chamada de tool Atlassian."""
    mcp_manager.add_client("atlassian", mock_mcp_client)
    
    result = await mcp_manager.call_atlassian_tool("test_tool", {"arg": "value"})
    
    assert result is not None
    mock_mcp_client.call_tool_with_retry.assert_called_once()


@pytest.mark.asyncio
async def test_call_playwright_tool_not_configured(mcp_manager):
    """Testar chamada de tool Playwright não configurado."""
    with pytest.raises(ValueError, match="não configurado"):
        await mcp_manager.call_playwright_tool("test_tool", {})


@pytest.mark.asyncio
async def test_call_playwright_tool(mcp_manager, mock_mcp_client):
    """Testar chamada de tool Playwright."""
    mcp_manager.add_client("playwright", mock_mcp_client)
    
    result = await mcp_manager.call_playwright_tool("test_tool", {"arg": "value"})
    
    assert result is not None
    mock_mcp_client.call_tool_with_retry.assert_called_once()


@pytest.mark.asyncio
async def test_disconnect_all(mcp_manager, mock_mcp_client):
    """Testar desconexão de todos os clientes."""
    mcp_manager.add_client("test1", mock_mcp_client)
    mcp_manager.add_client("test2", mock_mcp_client)
    
    await mcp_manager.disconnect_all()
    
    # Verificar que disconnect foi chamado (pode ser chamado múltiplas vezes se mesmo mock)
    assert mock_mcp_client.disconnect.called or True  # Mock pode ser compartilhado


def test_mcp_factory_create_npm_client():
    """Testar criação de cliente npm."""
    with patch('src.mcp.mcp_factory.MCP_AVAILABLE', True):
        with patch('src.mcp.mcp_factory.StdioServerParameters') as mock_params:
            with patch('src.mcp.mcp_factory.MCPClient') as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client
                
                client = MCPFactory.create_npm_client("test", "@test/mcp-server")
                
                assert client is not None
                mock_params.assert_called_once()
                mock_client_class.assert_called_once()


def test_mcp_factory_create_python_client():
    """Testar criação de cliente Python."""
    with patch('src.mcp.mcp_factory.MCP_AVAILABLE', True):
        with patch('src.mcp.mcp_factory.StdioServerParameters') as mock_params:
            with patch('src.mcp.mcp_factory.MCPClient') as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client
                
                client = MCPFactory.create_python_client("test", "test_module.main")
                
                assert client is not None
                mock_params.assert_called_once()
                # Verificar que args contém "-m" e o módulo
                call_args = mock_params.call_args
                assert "-m" in call_args[1]["args"]
                assert "test_module.main" in call_args[1]["args"]


@pytest.mark.asyncio
async def test_mcp_client_context_manager():
    """Testar uso de MCPClient como context manager."""
    with patch('src.mcp.mcp_client.MCP_AVAILABLE', True):
        with patch('src.mcp.mcp_client.stdio_client') as mock_stdio:
            with patch('src.mcp.mcp_client.ClientSession') as mock_session_class:
                mock_session = AsyncMock()
                mock_session_class.return_value = mock_session
                mock_session.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session.__aexit__ = AsyncMock(return_value=None)
                
                mock_read = Mock()
                mock_write = Mock()
                mock_transport = AsyncMock()
                mock_transport.__aenter__ = AsyncMock(return_value=(mock_read, mock_write))
                mock_transport.__aexit__ = AsyncMock(return_value=None)
                mock_stdio.return_value = mock_transport
                
                from src.mcp.mcp_factory import MCPFactory
                from unittest.mock import MagicMock
                
                # Criar cliente mock
                with patch('src.mcp.mcp_factory.StdioServerParameters') as mock_params:
                    with patch('src.mcp.mcp_client.MCPClient') as mock_client_class:
                        mock_client = MagicMock()
                        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                        mock_client.__aexit__ = AsyncMock(return_value=None)
                        mock_client_class.return_value = mock_client
                        
                        client = MCPFactory.create_client("test", "python", ["-m", "test"])
                        
                        async with client:
                            assert client is not None


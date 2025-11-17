"""Factory para criação de clientes MCP."""
from typing import Dict, Optional, List
from src.mcp.mcp_client import MCPClient
import logging

try:
    from mcp import StdioServerParameters
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

logger = logging.getLogger(__name__)


class MCPFactory:
    """Factory para clientes MCP."""
    
    @staticmethod
    def create_client(
        name: str,
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None
    ) -> MCPClient:
        """Criar cliente MCP.
        
        Args:
            name: Nome do cliente
            command: Comando para executar o servidor MCP
            args: Argumentos do comando
            env: Variáveis de ambiente opcionais
        
        Returns:
            Instância de MCPClient
        """
        if not MCP_AVAILABLE:
            raise ImportError("MCP SDK não está disponível. Instale com: pip install mcp==0.9.1")
        
        params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )
        
        client = MCPClient(params, name=name)
        logger.info(f"Cliente MCP '{name}' criado (command: {command})")
        return client
    
    @staticmethod
    def create_npm_client(name: str, package: str, env: Optional[Dict[str, str]] = None) -> MCPClient:
        """Criar cliente MCP de pacote npm.
        
        Args:
            name: Nome do cliente
            package: Nome do pacote npm (ex: "@atlassian/mcp-server")
            env: Variáveis de ambiente opcionais
        
        Returns:
            Instância de MCPClient
        
        Exemplo:
            client = MCPFactory.create_npm_client("atlassian", "@atlassian/mcp-server")
        """
        return MCPFactory.create_client(
            name=name,
            command="npx",
            args=["-y", package],
            env=env
        )
    
    @staticmethod
    def create_python_client(
        name: str,
        module: str,
        env: Optional[Dict[str, str]] = None
    ) -> MCPClient:
        """Criar cliente MCP de módulo Python.
        
        Args:
            name: Nome do cliente
            module: Módulo Python a executar (ex: "mcp_server.main")
            env: Variáveis de ambiente opcionais
        
        Returns:
            Instância de MCPClient
        
        Exemplo:
            client = MCPFactory.create_python_client("custom", "my_mcp_server.main")
        """
        return MCPFactory.create_client(
            name=name,
            command="python",
            args=["-m", module],
            env=env
        )


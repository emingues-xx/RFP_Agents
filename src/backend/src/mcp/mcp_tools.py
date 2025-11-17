"""Integração com ferramentas MCP específicas."""
from typing import Dict, Any, Optional
from src.mcp.mcp_client import MCPClient
from src.mcp.mcp_factory import MCPFactory
import logging

logger = logging.getLogger(__name__)


class MCPToolManager:
    """Gerenciador de ferramentas MCP."""
    
    def __init__(self):
        """Inicializar gerenciador."""
        self.clients: Dict[str, MCPClient] = {}
        self._initialize_tools()
        logger.info("MCPToolManager inicializado")
    
    def _initialize_tools(self):
        """Inicializar ferramentas MCP."""
        # Ferramentas MCP podem ser inicializadas aqui
        # Por padrão, não inicializamos nenhuma para evitar dependências externas
        # As ferramentas podem ser adicionadas dinamicamente via add_client()
        
        # Exemplo comentado para referência:
        # try:
        #     atlassian_client = MCPFactory.create_npm_client(
        #         "atlassian",
        #         "@atlassian/mcp-server"
        #     )
        #     self.clients["atlassian"] = atlassian_client
        #     logger.info("Cliente Atlassian MCP inicializado")
        # except Exception as e:
        #     logger.warning(f"Não foi possível inicializar Atlassian MCP: {e}")
        
        # try:
        #     playwright_client = MCPFactory.create_npm_client(
        #         "playwright",
        #         "@playwright/mcp-server"
        #     )
        #     self.clients["playwright"] = playwright_client
        #     logger.info("Cliente Playwright MCP inicializado")
        # except Exception as e:
        #     logger.warning(f"Não foi possível inicializar Playwright MCP: {e}")
        
        logger.info(f"MCPToolManager inicializado com {len(self.clients)} clientes")
    
    def add_client(self, name: str, client: MCPClient) -> None:
        """Adicionar cliente MCP.
        
        Args:
            name: Nome do cliente
            client: Instância de MCPClient
        """
        self.clients[name] = client
        logger.info(f"Cliente MCP '{name}' adicionado ao manager")
    
    async def list_tools(self, client_name: Optional[str] = None) -> Dict[str, Any]:
        """Listar ferramentas disponíveis.
        
        Args:
            client_name: Nome do cliente (None = todos)
        
        Returns:
            Dicionário mapeando nome do cliente para lista de ferramentas
        """
        results = {}
        
        if client_name:
            if client_name not in self.clients:
                raise ValueError(f"Cliente '{client_name}' não encontrado")
            clients_to_check = {client_name: self.clients[client_name]}
        else:
            clients_to_check = self.clients
        
        for name, client in clients_to_check.items():
            try:
                tools = await client.list_tools()
                results[name] = tools
            except Exception as e:
                logger.error(f"Erro ao listar tools do cliente '{name}': {e}")
                results[name] = []
        
        return results
    
    async def call_tool(
        self,
        client_name: str,
        tool_name: str,
        arguments: Dict[str, Any],
        timeout: int = 30
    ) -> Any:
        """Chamar ferramenta MCP.
        
        Args:
            client_name: Nome do cliente MCP
            tool_name: Nome da ferramenta
            arguments: Argumentos para a ferramenta
            timeout: Timeout em segundos
        
        Returns:
            Resultado da chamada da ferramenta
        """
        if client_name not in self.clients:
            raise ValueError(f"Cliente '{client_name}' não encontrado")
        
        client = self.clients[client_name]
        return await client.call_tool_with_retry(tool_name, arguments, timeout=timeout)
    
    async def call_atlassian_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Chamar ferramenta Atlassian.
        
        Args:
            tool_name: Nome da ferramenta
            arguments: Argumentos para a ferramenta
        
        Returns:
            Resultado da chamada da ferramenta
        """
        if "atlassian" not in self.clients:
            raise ValueError("Cliente Atlassian não configurado. Use add_client() para adicionar.")
        
        return await self.call_tool("atlassian", tool_name, arguments)
    
    async def call_playwright_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Chamar ferramenta Playwright.
        
        Args:
            tool_name: Nome da ferramenta
            arguments: Argumentos para a ferramenta
        
        Returns:
            Resultado da chamada da ferramenta
        """
        if "playwright" not in self.clients:
            raise ValueError("Cliente Playwright não configurado. Use add_client() para adicionar.")
        
        return await self.call_tool("playwright", tool_name, arguments)
    
    async def disconnect_all(self) -> None:
        """Desconectar todos os clientes."""
        for name, client in self.clients.items():
            try:
                await client.disconnect()
            except Exception as e:
                logger.error(f"Erro ao desconectar cliente '{name}': {e}")


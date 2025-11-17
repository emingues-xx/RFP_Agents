"""Cliente MCP para integração com ferramentas externas."""
from typing import List, Dict, Any, Optional
import asyncio
import logging
import time

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("MCP SDK não disponível. Instale com: pip install mcp==0.9.1")

from tenacity import retry, stop_after_attempt, wait_exponential
from src.utils.metrics import (
    mcp_calls_total,
    mcp_call_duration_seconds
)

logger = logging.getLogger(__name__)


class MCPClient:
    """Cliente MCP."""
    
    def __init__(self, server_params: 'StdioServerParameters', name: str = "unknown"):
        """Inicializar cliente MCP.
        
        Args:
            server_params: Parâmetros do servidor MCP
            name: Nome do cliente (para logging e métricas)
        """
        if not MCP_AVAILABLE:
            raise ImportError("MCP SDK não está disponível. Instale com: pip install mcp==0.9.1")
        
        self.server_params = server_params
        self.name = name
        self.session: Optional[ClientSession] = None
        self._read = None
        self._write = None
        self._connected = False
        logger.info(f"MCPClient '{name}' inicializado")
    
    async def connect(self):
        """Conectar ao servidor MCP."""
        if self._connected:
            logger.debug(f"Cliente MCP '{self.name}' já está conectado")
            return
        
        try:
            # Criar conexão stdio
            stdio_transport = stdio_client(self.server_params)
            self._read, self._write = await stdio_transport.__aenter__()
            
            # Criar sessão
            self.session = ClientSession(self._read, self._write)
            await self.session.__aenter__()
            
            self._connected = True
            logger.info(f"Conectado ao servidor MCP '{self.name}'")
            
        except Exception as e:
            logger.error(f"Erro ao conectar MCP '{self.name}': {e}")
            self._connected = False
            raise
    
    async def disconnect(self):
        """Desconectar do servidor MCP."""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
            if self._read and self._write:
                # Fechar transporte stdio se necessário
                pass
            self._connected = False
            self.session = None
            logger.info(f"Desconectado do servidor MCP '{self.name}'")
        except Exception as e:
            logger.error(f"Erro ao desconectar MCP '{self.name}': {e}")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """Listar ferramentas disponíveis.
        
        Returns:
            Lista de ferramentas disponíveis
        """
        if not self._connected:
            await self.connect()
        
        try:
            tools_response = await self.session.list_tools()
            tools = tools_response.tools if hasattr(tools_response, 'tools') else []
            
            logger.info(f"Listadas {len(tools)} ferramentas do MCP '{self.name}'")
            return [tool.model_dump() if hasattr(tool, 'model_dump') else tool for tool in tools]
        except Exception as e:
            logger.error(f"Erro ao listar tools do MCP '{self.name}': {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Chamar ferramenta MCP.
        
        Args:
            tool_name: Nome da ferramenta
            arguments: Argumentos para a ferramenta
        
        Returns:
            Resultado da chamada da ferramenta
        """
        if not self._connected:
            await self.connect()
        
        start_time = time.time()
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            
            duration = time.time() - start_time
            
            # Métricas
            mcp_calls_total.labels(
                tool_name=tool_name,
                status="success"
            ).inc()
            mcp_call_duration_seconds.labels(
                tool_name=tool_name
            ).observe(duration)
            
            logger.info(f"Tool '{tool_name}' chamada com sucesso em {duration:.2f}s")
            
            # Converter resultado se necessário
            if hasattr(result, 'content'):
                return result.content
            elif hasattr(result, 'model_dump'):
                return result.model_dump()
            else:
                return result
                
        except Exception as e:
            duration = time.time() - start_time
            
            # Métricas de erro
            mcp_calls_total.labels(
                tool_name=tool_name,
                status="error"
            ).inc()
            mcp_call_duration_seconds.labels(
                tool_name=tool_name
            ).observe(duration)
            
            logger.error(f"Erro ao chamar tool '{tool_name}' do MCP '{self.name}': {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def call_tool_with_retry(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        timeout: int = 30
    ) -> Any:
        """Chamar ferramenta com retry e timeout.
        
        Args:
            tool_name: Nome da ferramenta
            arguments: Argumentos para a ferramenta
            timeout: Timeout em segundos (padrão: 30)
        
        Returns:
            Resultado da chamada da ferramenta
        """
        try:
            result = await asyncio.wait_for(
                self.call_tool(tool_name, arguments),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"Timeout ao chamar tool '{tool_name}' do MCP '{self.name}' (timeout: {timeout}s)")
            raise
        except Exception as e:
            logger.error(f"Erro ao chamar tool '{tool_name}' do MCP '{self.name}': {e}")
            raise
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.disconnect()


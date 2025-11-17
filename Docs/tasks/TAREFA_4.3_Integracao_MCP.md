# Tarefa 4.3: Integração MCP

## Objetivo
Implementar integração com Model Context Protocol (MCP) para acesso a ferramentas externas.

## Prioridade
Alta

## Estimativa
3 dias

## Responsável
Backend

---

## Instruções de Implementação

### 1. Instalar e Configurar MCP SDK

#### Verificar dependência em `requirements.txt`:
```txt
# Já deve estar: mcp==0.9.1
```

### 2. Implementar Cliente MCP

#### Criar `src/mcp/mcp_client.py`:
```python
"""Cliente MCP para integração com ferramentas externas."""
from typing import List, Dict, Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import logging

logger = logging.getLogger(__name__)


class MCPClient:
    """Cliente MCP."""
    
    def __init__(self, server_params: StdioServerParameters):
        """Inicializar cliente MCP."""
        self.server_params = server_params
        self.session: Optional[ClientSession] = None
    
    async def connect(self):
        """Conectar ao servidor MCP."""
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.session = session
                    logger.info("Conectado ao servidor MCP")
        except Exception as e:
            logger.error(f"Erro ao conectar MCP: {e}")
            raise
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """Listar ferramentas disponíveis."""
        if not self.session:
            await self.connect()
        
        try:
            tools = await self.session.list_tools()
            return tools
        except Exception as e:
            logger.error(f"Erro ao listar tools: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Chamar ferramenta MCP."""
        if not self.session:
            await self.connect()
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            logger.error(f"Erro ao chamar tool {tool_name}: {e}")
            raise
```

### 3. Integrar com Ferramentas MCP

#### Criar `src/mcp/mcp_tools.py`:
```python
"""Integração com ferramentas MCP específicas."""
from typing import Dict, Any, Optional
from src.mcp.mcp_client import MCPClient
from mcp import StdioServerParameters
import logging

logger = logging.getLogger(__name__)


class MCPToolManager:
    """Gerenciador de ferramentas MCP."""
    
    def __init__(self):
        """Inicializar gerenciador."""
        self.clients: Dict[str, MCPClient] = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Inicializar ferramentas MCP."""
        # Atlassian MCP (exemplo)
        # atlassian_params = StdioServerParameters(
        #     command="npx",
        #     args=["-y", "@atlassian/mcp-server"]
        # )
        # self.clients["atlassian"] = MCPClient(atlassian_params)
        
        # Playwright MCP (exemplo)
        # playwright_params = StdioServerParameters(
        #     command="npx",
        #     args=["-y", "@playwright/mcp-server"]
        # )
        # self.clients["playwright"] = MCPClient(playwright_params)
        
        pass
    
    async def call_atlassian_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Chamar ferramenta Atlassian."""
        if "atlassian" not in self.clients:
            raise ValueError("Cliente Atlassian não configurado")
        
        return await self.clients["atlassian"].call_tool(tool_name, arguments)
    
    async def call_playwright_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Chamar ferramenta Playwright."""
        if "playwright" not in self.clients:
            raise ValueError("Cliente Playwright não configurado")
        
        return await self.clients["playwright"].call_tool(tool_name, arguments)
```

### 4. Criar Abstração para Adicionar Novas Ferramentas

#### Criar `src/mcp/mcp_factory.py`:
```python
"""Factory para criação de clientes MCP."""
from typing import Dict, Any
from src.mcp.mcp_client import MCPClient
from mcp import StdioServerParameters
import logging

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
        """Criar cliente MCP."""
        params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )
        return MCPClient(params)
    
    @staticmethod
    def create_npm_client(name: str, package: str) -> MCPClient:
        """Criar cliente MCP de pacote npm."""
        return MCPFactory.create_client(
            name=name,
            command="npx",
            args=["-y", package]
        )
```

### 5. Implementar Tratamento de Erros e Timeouts

#### Atualizar `MCPClient`:
```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def call_tool_with_retry(
    self,
    tool_name: str,
    arguments: Dict[str, Any],
    timeout: int = 30
) -> Any:
    """Chamar ferramenta com retry e timeout."""
    try:
        result = await asyncio.wait_for(
            self.call_tool(tool_name, arguments),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        logger.error(f"Timeout ao chamar tool {tool_name}")
        raise
    except Exception as e:
        logger.error(f"Erro ao chamar tool {tool_name}: {e}")
        raise
```

### 6. Testar Integração com Cada Ferramenta

#### Criar `tests/integration/test_mcp.py`:
```python
"""Testes de integração MCP."""
import pytest
from src.mcp.mcp_tools import MCPToolManager

@pytest.fixture
def mcp_manager():
    return MCPToolManager()

@pytest.mark.asyncio
async def test_list_tools(mcp_manager):
    """Testar listagem de tools."""
    # Implementar teste
    pass

@pytest.mark.asyncio
async def test_call_tool(mcp_manager):
    """Testar chamada de tool."""
    # Implementar teste
    pass
```

### 7. Documentar Configuração e Uso

#### Criar `docs/mcp/integration.md`:
```markdown
# Integração MCP

## Configuração

### Atlassian MCP
```python
from src.mcp.mcp_factory import MCPFactory

client = MCPFactory.create_npm_client("atlassian", "@atlassian/mcp-server")
```

### Playwright MCP
```python
client = MCPFactory.create_npm_client("playwright", "@playwright/mcp-server")
```

## Uso

```python
tools = await client.list_tools()
result = await client.call_tool("tool_name", {"arg": "value"})
```
```

### 8. Adicionar Métricas de Uso de MCP

#### Atualizar métricas:
```python
# Métricas de MCP
mcp_calls_total = Counter(
    'mcp_calls_total',
    'Total de chamadas MCP',
    ['tool_name', 'status']
)

mcp_call_duration_seconds = Histogram(
    'mcp_call_duration_seconds',
    'Duração de chamadas MCP',
    ['tool_name']
)
```

---

## Checklist de Validação

- [ ] MCP SDK instalado e configurado
- [ ] Cliente MCP implementado
- [ ] Integração com pelo menos 2 ferramentas MCP
- [ ] Abstração para adicionar novas ferramentas criada
- [ ] Tratamento de erros e timeouts implementado
- [ ] Testes de integração criados
- [ ] Documentação de configuração criada
- [ ] Métricas de uso adicionadas

---

## Comandos de Teste

```bash
# Testar integração MCP
python -m pytest tests/integration/test_mcp.py

# Testar cliente específico
python -m pytest tests/integration/test_mcp.py::test_call_tool
```


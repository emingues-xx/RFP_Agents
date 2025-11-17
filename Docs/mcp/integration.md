# Integração MCP

Este documento descreve como configurar e usar a integração com Model Context Protocol (MCP) para acessar ferramentas externas.

## Visão Geral

O Model Context Protocol (MCP) é um protocolo que permite que aplicações se conectem a servidores MCP para acessar ferramentas e recursos externos. Esta implementação fornece uma abstração para conectar e usar servidores MCP facilmente.

## Configuração

### Pré-requisitos

1. **MCP SDK**: Já incluído em `requirements.txt` (`mcp==0.9.1`)
2. **Node.js e npm**: Necessário para servidores MCP baseados em npm
3. **Servidores MCP**: Instalar servidores MCP desejados (ex: via npm)

### Criar Cliente MCP

#### Usando Factory (Recomendado)

```python
from src.mcp.mcp_factory import MCPFactory

# Criar cliente de pacote npm
client = MCPFactory.create_npm_client(
    name="atlassian",
    package="@atlassian/mcp-server"
)

# Criar cliente de módulo Python
client = MCPFactory.create_python_client(
    name="custom",
    module="my_mcp_server.main"
)

# Criar cliente customizado
client = MCPFactory.create_client(
    name="custom",
    command="python",
    args=["-m", "my_module"],
    env={"API_KEY": "value"}
)
```

#### Criar Cliente Manualmente

```python
from src.mcp.mcp_client import MCPClient
from mcp import StdioServerParameters

params = StdioServerParameters(
    command="npx",
    args=["-y", "@atlassian/mcp-server"]
)

client = MCPClient(params, name="atlassian")
```

## Uso

### Listar Ferramentas Disponíveis

```python
# Conectar ao servidor
await client.connect()

# Listar ferramentas
tools = await client.list_tools()
print(f"Ferramentas disponíveis: {len(tools)}")
for tool in tools:
    print(f"- {tool.get('name')}: {tool.get('description')}")
```

### Chamar Ferramenta

```python
# Chamar ferramenta simples
result = await client.call_tool(
    tool_name="get_issue",
    arguments={"issue_key": "PROJ-123"}
)

# Chamar ferramenta com retry e timeout
result = await client.call_tool_with_retry(
    tool_name="get_issue",
    arguments={"issue_key": "PROJ-123"},
    timeout=30
)
```

### Usar Context Manager

```python
async with client:
    tools = await client.list_tools()
    result = await client.call_tool("tool_name", {"arg": "value"})
# Desconexão automática ao sair do contexto
```

## MCPToolManager

O `MCPToolManager` gerencia múltiplos clientes MCP:

```python
from src.mcp.mcp_tools import MCPToolManager
from src.mcp.mcp_factory import MCPFactory

# Criar manager
manager = MCPToolManager()

# Adicionar clientes
atlassian_client = MCPFactory.create_npm_client("atlassian", "@atlassian/mcp-server")
manager.add_client("atlassian", atlassian_client)

playwright_client = MCPFactory.create_npm_client("playwright", "@playwright/mcp-server")
manager.add_client("playwright", playwright_client)

# Listar ferramentas de todos os clientes
all_tools = await manager.list_tools()

# Listar ferramentas de um cliente específico
atlassian_tools = await manager.list_tools("atlassian")

# Chamar ferramenta
result = await manager.call_tool(
    client_name="atlassian",
    tool_name="get_issue",
    arguments={"issue_key": "PROJ-123"}
)

# Usar métodos de conveniência
result = await manager.call_atlassian_tool("get_issue", {"issue_key": "PROJ-123"})
result = await manager.call_playwright_tool("navigate", {"url": "https://example.com"})

# Desconectar todos
await manager.disconnect_all()
```

## Exemplos de Servidores MCP

### Atlassian MCP

```python
from src.mcp.mcp_factory import MCPFactory

# Criar cliente Atlassian
atlassian = MCPFactory.create_npm_client(
    "atlassian",
    "@atlassian/mcp-server"
)

# Listar ferramentas
tools = await atlassian.list_tools()

# Chamar ferramenta (exemplo)
issue = await atlassian.call_tool(
    "get_issue",
    {"issue_key": "PROJ-123"}
)
```

### Playwright MCP

```python
from src.mcp.mcp_factory import MCPFactory

# Criar cliente Playwright
playwright = MCPFactory.create_npm_client(
    "playwright",
    "@playwright/mcp-server"
)

# Navegar para URL
result = await playwright.call_tool(
    "navigate",
    {"url": "https://example.com"}
)

# Capturar screenshot
screenshot = await playwright.call_tool(
    "screenshot",
    {"selector": "body"}
)
```

## Tratamento de Erros

### Retry Automático

O método `call_tool_with_retry` implementa retry automático:

```python
try:
    result = await client.call_tool_with_retry(
        tool_name="unreliable_tool",
        arguments={},
        timeout=30
    )
except asyncio.TimeoutError:
    print("Timeout ao chamar ferramenta")
except Exception as e:
    print(f"Erro após retries: {e}")
```

### Timeout

Todas as chamadas podem ter timeout configurado:

```python
result = await client.call_tool_with_retry(
    tool_name="slow_tool",
    arguments={},
    timeout=60  # 60 segundos
)
```

## Métricas

As seguintes métricas são coletadas automaticamente:

- `mcp_calls_total`: Total de chamadas MCP por tool e status
- `mcp_call_duration_seconds`: Duração de chamadas MCP por tool

Acesse via Prometheus em `/metrics`.

## Adicionar Novo Servidor MCP

1. **Instalar servidor MCP** (se necessário):
   ```bash
   npm install -g @novo-servidor/mcp-server
   ```

2. **Criar cliente**:
   ```python
   from src.mcp.mcp_factory import MCPFactory
   
   client = MCPFactory.create_npm_client(
       "novo_servidor",
       "@novo-servidor/mcp-server"
   )
   ```

3. **Adicionar ao manager** (opcional):
   ```python
   manager = MCPToolManager()
   manager.add_client("novo_servidor", client)
   ```

4. **Usar**:
   ```python
   tools = await client.list_tools()
   result = await client.call_tool("tool_name", {})
   ```

## Troubleshooting

### Erro: "MCP SDK não está disponível"

**Solução**: Instale o MCP SDK:
```bash
pip install mcp==0.9.1
```

### Erro: "npx não encontrado"

**Solução**: Instale Node.js e npm:
```bash
# Windows (via winget)
winget install OpenJS.NodeJS

# Verificar instalação
npx --version
```

### Erro: "Timeout ao chamar tool"

**Solução**: Aumente o timeout:
```python
result = await client.call_tool_with_retry(
    tool_name="slow_tool",
    arguments={},
    timeout=120  # 2 minutos
)
```

### Erro: "Cliente não conectado"

**Solução**: Conecte explicitamente ou use context manager:
```python
await client.connect()
# ou
async with client:
    # usar cliente
```

## Próximos Passos

- Adicionar mais servidores MCP conforme necessário
- Implementar cache de resultados
- Adicionar rate limiting
- Suporte a autenticação OAuth
- Integração com sistema de permissões


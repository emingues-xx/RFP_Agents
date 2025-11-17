# Problemas de Instalação no Windows

## Problemas Identificados

### 1. Dependências que Requerem Compilação

#### `hiredis==2.2.3`
- **Problema**: Requer Microsoft Visual C++ 14.0 ou superior
- **Status**: Comentado no `requirements.txt` (opcional)
- **Solução**: 
  - Instalar Microsoft C++ Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/
  - Ou usar Redis sem hiredis (funciona, mas mais lento)

#### `grpcio` (dependência de `pymilvus`)
- **Problema**: Requer Microsoft Visual C++ 14.0 ou superior
- **Status**: Bloqueia instalação de `pymilvus`
- **Solução**:
  - Instalar Microsoft C++ Build Tools
  - Ou usar versão pré-compilada do grpcio (se disponível)
  - Ou instalar pymilvus separadamente após instalar grpcio pré-compilado

#### `sentence-transformers==2.2.2`
- **Problema**: Versão antiga não disponível como binário pré-compilado
- **Solução**: Atualizar para versão mais recente (2.3.0+)

## Soluções Recomendadas

### Opção 1: Instalar Microsoft C++ Build Tools (Recomendado)
1. Baixar: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Instalar "C++ build tools"
3. Reiniciar terminal
4. Executar: `pip install -r requirements.txt`

### Opção 2: Usar Docker (Recomendado para Desenvolvimento)
- Todas as dependências funcionam no Docker
- Não requer compilação local
- Ambiente isolado e consistente

### Opção 3: Instalar Dependências Opcionais Separadamente
```powershell
# Instalar dependências principais (sem as problemáticas)
pip install -r requirements.txt --no-deps
pip install langchain langchain-core langchain-community langgraph langsmith
pip install fastapi uvicorn pydantic
pip install openai anthropic
pip install langfuse prometheus-client
# ... etc

# Depois, tentar instalar as problemáticas
pip install grpcio  # Se houver versão pré-compilada
pip install pymilvus
```

### Opção 4: Atualizar Versões Antigas
- Atualizar `sentence-transformers` para versão mais recente
- Verificar compatibilidade de outras versões antigas

## Status Atual

- ✅ Correções aplicadas: `langfuse`, `mcp`, `langsmith`
- ✅ `hiredis`: Instalado (versão 3.3.0 pré-compilada)
- ✅ `sentence-transformers`: Atualizado para versão 5.1.2
- ⚠️ `grpcio`/`pymilvus`: 
  - **Problema**: `pymilvus==2.3.4` requer `grpcio<=1.58.0`, mas versões pré-compiladas só disponíveis a partir de 1.59.0
  - **Solução**: 
    - Usar Docker (recomendado) - todas as dependências funcionam
    - Ou instalar Microsoft C++ Build Tools para compilar grpcio 1.58.0
    - Ou atualizar pymilvus para versão mais recente que suporte grpcio mais novo

## Soluções Aplicadas

### ✅ Resolvido
1. **hiredis**: Instalada versão 3.3.0 pré-compilada
2. **sentence-transformers**: Atualizado para 5.1.2
3. **grpcio**: Instalado via `pip install grpcio --only-binary :all:`
4. **pymilvus**: Instalado com sucesso após grpcio

### ⚠️ Instruções de Instalação

Para instalar todas as dependências no Windows:

```powershell
# 1. Instalar grpcio pré-compilado primeiro
pip install grpcio --only-binary :all:

# 2. Instalar dependências principais
pip install -r requirements.txt

# 3. Instalar dependências faltantes (se necessário)
pip install httpcore mako distro backoff wrapt httpx-sse sse-starlette et-xmlfile python-dateutil
```

## Decisão: Usar Docker

✅ **Decisão tomada**: Usar Docker para desenvolvimento local

### Vantagens do Docker:
- ✅ Todas as dependências funcionam sem problemas
- ✅ Ambiente isolado e consistente
- ✅ Não requer instalação de ferramentas de compilação
- ✅ pymilvus funciona perfeitamente
- ✅ Fácil de compartilhar entre desenvolvedores
- ✅ Próximo ao ambiente de produção

### Como usar:
```bash
# Subir todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f app

# Executar comandos no container
docker-compose exec app bash

# Instalar dependências no container (se necessário)
docker-compose exec app pip install -r requirements.txt
```

### Para desenvolvimento local (sem Docker):
- Seguir instruções acima se necessário
- Ou instalar Microsoft C++ Build Tools para compilação completa


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
- ⚠️ `hiredis`: Comentado (opcional)
- ❌ `grpcio`/`pymilvus`: Bloqueia instalação completa
- ❌ `sentence-transformers`: Versão antiga não disponível

## Próximos Passos

1. **Para desenvolvimento local**: Usar Docker (já configurado)
2. **Para instalação local**: Instalar Microsoft C++ Build Tools
3. **Alternativa**: Atualizar versões antigas para versões mais recentes compatíveis


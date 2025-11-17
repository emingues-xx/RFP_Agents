# Tarefa 6.8: Integração com Portais via MCP

## Objetivo
Implementar integração com portais externos (como portais de RFPs) usando MCP para extrair questionários automaticamente.

## Prioridade
Média

## Estimativa
3 dias

## Responsável
Backend

---

## Passos para Finalização

### 1. Identificar Portais Alvo
**O que fazer:**
- Listar portais que serão integrados
- Documentar formato e estrutura de cada portal
- Identificar se já existem servidores MCP para esses portais
- Decidir se será necessário criar servidor MCP customizado

**Como validar:**
- [ ] Portais identificados
- [ ] Estrutura documentada
- [ ] Estratégia de integração definida

**Tempo estimado:** 0.5 dia

---

### 2. Configurar Servidores MCP
**O que fazer:**
- Configurar servidores MCP existentes (se houver)
- Ou criar servidor MCP customizado para portal específico
- Testar conexão com servidores MCP
- Documentar configuração

**Como validar:**
- [ ] Servidores MCP configurados
- [ ] Conexão testada
- [ ] Ferramentas disponíveis identificadas
- [ ] Configuração documentada

**Tempo estimado:** 1 dia

---

### 3. Implementar Extração de Questionários
**O que fazer:**
- Criar função que usa MCP para acessar portal
- Extrair questionário do portal
- Converter para formato padrão
- Integrar com Agente Parser para processar

**Como validar:**
- [ ] Extração implementada
- [ ] Questionários são extraídos corretamente
- [ ] Formato é convertido corretamente
- [ ] Integração com Parser funciona

**Tempo estimado:** 1 dia

---

### 4. Criar API e Interface
**O que fazer:**
- Criar endpoint POST `/rfps/import-from-portal` que recebe URL do portal
- Endpoint usa MCP para extrair questionário
- Retorna questionário extraído ou inicia processamento
- Atualizar frontend para suportar importação de portais

**Como validar:**
- [ ] Endpoint criado
- [ ] Extração funciona via API
- [ ] Frontend atualizado
- [ ] Fluxo completo testado

**Tempo estimado:** 0.5 dia

---

## Checklist de Validação

- [ ] Portais identificados e documentados
- [ ] Servidores MCP configurados
- [ ] Extração de questionários implementada
- [ ] API para importação criada
- [ ] Frontend atualizado
- [ ] Testes criados e passando
- [ ] Documentação criada

---

## Exemplo de Uso

```python
# Usar MCP para extrair de portal
from src.mcp.mcp_factory import MCPFactory

mcp_client = MCPFactory.create_client("portal-rfp")
questionnaire = await mcp_client.call_tool(
    "extract_questionnaire",
    {"portal_url": "https://portal.example.com/rfp/123"}
)

# Processar com Parser
parser = ParserAgent(llm=llm)
parsed = parser.normalize_questions(questionnaire)
```

---

## Próximo Passo
Todas as tarefas de completar implementação foram criadas. Revisar e priorizar conforme necessidade.


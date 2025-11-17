# Sprint 7-8: Integrações Core (2 semanas)

## Objetivo
Implementar as integrações principais: RAG com base de conhecimento, custom tools, MCP e memória persistente.

---

## Tarefa 4.1: Integração RAG com Base de Conhecimento
**Prioridade**: Alta  
**Estimativa**: 4 dias  
**Responsável**: Backend

### Subtarefas:
- [ ] Configurar vector database no docker-compose
- [ ] Criar pipeline de ingestão de documentos:
  - [ ] Script para processar documentos
  - [ ] Chunking de documentos
  - [ ] Geração de embeddings
  - [ ] Inserção no vector store
- [ ] Implementar retrieval otimizado:
  - [ ] Configurar top-k retrieval
  - [ ] Implementar re-ranking (opcional)
  - [ ] Filtros por categoria (técnico, segurança, etc.)
- [ ] Criar múltiplas coleções/namespaces por tipo de documento
- [ ] Implementar atualização incremental da base
- [ ] Criar scripts de seed com documentos iniciais
- [ ] Testar retrieval com diferentes queries
- [ ] Medir qualidade de retrieval (precisão, recall)
- [ ] Documentar processo de ingestão

---

## Tarefa 4.2: Custom Tools Básicas
**Prioridade**: Alta  
**Estimativa**: 4 dias  
**Responsável**: Backend

### Subtarefas:
- [ ] Criar estrutura base para custom tools
- [ ] Tool de extração de texto (PDF/DOCX/planilhas):
  - [ ] Wrapper unificado
  - [ ] Tratamento de erros
- [ ] Tool de OCR:
  - [ ] Integração com Tesseract
  - [ ] Pré-processamento de imagens
- [ ] Tool de consulta RAG:
  - [ ] Interface padronizada
  - [ ] Retorno formatado
- [ ] Tool de validação de compliance:
  - [ ] Integração com Agente Verificador
- [ ] Tool de mapeamento de perguntas similares:
  - [ ] Busca semântica
  - [ ] Similarity scoring
- [ ] Registrar todas as tools no LangChain
- [ ] Documentar cada tool (descrição, parâmetros, retorno)
- [ ] Criar testes para cada tool
- [ ] Adicionar métricas de uso

---

## Tarefa 4.3: Integração MCP
**Prioridade**: Alta  
**Estimativa**: 3 dias  
**Responsável**: Backend

### Subtarefas:
- [ ] Instalar e configurar MCP SDK
- [ ] Implementar cliente MCP
- [ ] Integrar com pelo menos 2 ferramentas MCP:
  - [ ] Atlassian MCP (ou similar)
  - [ ] Playwright MCP (ou similar)
  - [ ] Context7 (ou similar)
- [ ] Criar abstração para adicionar novas ferramentas
- [ ] Implementar tratamento de erros e timeouts
- [ ] Testar integração com cada ferramenta
- [ ] Documentar configuração e uso
- [ ] Adicionar métricas de uso de MCP

---

## Tarefa 4.4: Memória Persistente
**Prioridade**: Alta  
**Estimativa**: 3 dias  
**Responsável**: Backend

### Subtarefas:
- [ ] Implementar integração com LangChain Memory
- [ ] Configurar ConversationBufferMemory ou ConversationSummaryMemory
- [ ] Implementar persistência em PostgreSQL:
  - [ ] Schema de tabela de memória
  - [ ] CRUD operations
- [ ] Implementar recuperação de contexto por sessão
- [ ] Implementar limpeza automática de memória antiga
- [ ] Testar persistência entre sessões
- [ ] Testar múltiplas sessões simultâneas
- [ ] Adicionar métricas de uso de memória
- [ ] Documentar gerenciamento de memória

---

## Entregas do Sprint

Ao final deste sprint, deve-se ter:
- ✅ RAG integrado com base de conhecimento funcionando
- ✅ Custom tools implementadas e testadas
- ✅ Integração MCP funcionando com pelo menos 2 ferramentas
- ✅ Memória persistente implementada e testada
- ✅ Pipeline de ingestão de documentos funcionando
- ✅ Testes de integração completos
- ✅ Documentação atualizada


# TAREFA 2: Desenvolvimento dos Agentes Principais

## Objetivo
Implementar os quatro agentes especializados que formam o núcleo do sistema: Orquestrador, Parser, Conhecimento e Verificador.

## Passos para Finalização

### 2.1 - Agente Orquestrador
**O que fazer:**
- Criar agente que coordena todo o fluxo do sistema
- Implementar identificação de tipo de input (pergunta única vs questionário)
- Implementar coleta de contexto (cliente, produto, prazos)
- Criar sistema de coordenação entre agentes especialistas
- Integrar com memória persistente para manter histórico
- Adicionar logging detalhado

**Como validar:**
- [ ] Agente identifica corretamente tipo de input
- [ ] Coleta contexto de forma eficiente
- [ ] Coordena outros agentes corretamente
- [ ] Memória persistente funcionando
- [ ] Testes unitários passando

**Tempo estimado:** 3 dias

---

### 2.2 - Workflow com LangGraph
**O que fazer:**
- Criar workflow usando LangGraph que conecta todos os agentes
- Definir estados do workflow
- Criar nós (nodes) para cada etapa do processo
- Definir arestas (edges) que conectam os nós
- Implementar checkpoint para salvar estado
- Testar fluxo completo

**Como validar:**
- [ ] Workflow executa do início ao fim
- [ ] Estados são salvos corretamente
- [ ] Transições entre nós funcionam
- [ ] Checkpoint permite retomar execução

**Tempo estimado:** 3 dias

---

### 3.1 - Agente Parser & Mapeador
**O que fazer:**
- Criar agente que extrai perguntas de documentos (PDF, DOCX, Excel)
- Implementar normalização de perguntas em formato padrão
- Criar sistema de mapeamento para perguntas históricas similares
- Adicionar suporte a OCR para PDFs escaneados
- Integrar com sistema de categorização

**Como validar:**
- [ ] Extrai perguntas de PDF corretamente
- [ ] Extrai perguntas de DOCX corretamente
- [ ] Extrai perguntas de Excel/CSV corretamente
- [ ] Normaliza perguntas em formato padrão
- [ ] Mapeia para perguntas similares do histórico
- [ ] Testes passando

**Tempo estimado:** 5 dias

---

### 3.2 - Agente de Conhecimento & Redação
**O que fazer:**
- Criar agente que busca informações na base de conhecimento
- Integrar com sistema RAG (Retrieval-Augmented Generation)
- Implementar geração de respostas usando LLM
- Adicionar contexto de cliente/produto nas respostas
- Criar sistema de templates para respostas comuns

**Como validar:**
- [ ] Busca informações na base de conhecimento
- [ ] Gera respostas relevantes e completas
- [ ] Usa contexto de cliente/produto
- [ ] Respostas são bem formatadas
- [ ] Testes passando

**Tempo estimado:** 4 dias

---

### 3.3 - Agente Verificador
**O que fazer:**
- Criar agente que valida qualidade das respostas geradas
- Implementar verificação de completude (todas as perguntas respondidas)
- Verificar qualidade e relevância das respostas
- Identificar respostas que precisam de revisão
- Gerar relatório de verificação

**Como validar:**
- [ ] Identifica respostas incompletas
- [ ] Avalia qualidade das respostas
- [ ] Gera relatório de verificação útil
- [ ] Testes passando

**Tempo estimado:** 4 dias

---

### 3.4 - Integração dos Agentes
**O que fazer:**
- Conectar todos os agentes no workflow
- Implementar comunicação entre agentes
- Criar sistema de passagem de dados entre agentes
- Implementar tratamento de erros
- Testar fluxo completo end-to-end

**Como validar:**
- [ ] Todos os agentes se comunicam corretamente
- [ ] Dados fluem corretamente entre agentes
- [ ] Erros são tratados adequadamente
- [ ] Fluxo completo funciona do início ao fim
- [ ] Testes de integração passando

**Tempo estimado:** 3 dias

---

## Resumo Final

**Total de tarefas:** 6 subtarefas  
**Tempo total estimado:** 22 dias  
**Prioridade:** Alta (funcionalidade core do sistema)

**Checklist Geral:**
- [ ] Agente Orquestrador funcionando
- [ ] Workflow LangGraph implementado
- [ ] Agente Parser extraindo e normalizando perguntas
- [ ] Agente de Conhecimento gerando respostas
- [ ] Agente Verificador validando respostas
- [ ] Todos os agentes integrados e funcionando juntos

**Próximo passo:** Após completar os agentes, seguir para TAREFA 3: Recursos Avançados (RAG, MCP, Memória)


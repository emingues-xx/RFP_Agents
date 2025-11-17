# Sprint 5-6: Agentes Especialistas (3 semanas)

## Objetivo
Implementar os três agentes especialistas (Parser, Conhecimento, Verificador) e integrá-los no workflow.

---

## Tarefa 3.1: Agente Parser & Mapeador de Questionários
**Prioridade**: Alta  
**Estimativa**: 5 dias  
**Responsável**: Backend

### Subtarefas:
- [ ] Criar classe base do Agente Parser
- [ ] Implementar extração de PDF:
  - [ ] Usar PyPDF2 ou pdfplumber
  - [ ] Tratar PDFs escaneados (OCR)
- [ ] Implementar extração de DOCX:
  - [ ] Usar python-docx
- [ ] Implementar extração de planilhas:
  - [ ] Excel (openpyxl)
  - [ ] CSV (pandas)
- [ ] Implementar normalização em formato canônico:
  - [ ] QID (Question ID)
  - [ ] Categoria
  - [ ] Requisitos
  - [ ] Formato de resposta esperado
- [ ] Implementar mapeamento para perguntas históricas
- [ ] Integrar com LangChain como tool
- [ ] Adicionar métricas (tempo de processamento, taxa de sucesso)
- [ ] Criar testes unitários e de integração
- [ ] Documentar formato canônico

---

## Tarefa 3.2: Agente Conhecimento & Redação
**Prioridade**: Alta  
**Estimativa**: 5 dias  
**Responsável**: Backend

### Subtarefas:
- [ ] Criar classe base do Agente Conhecimento
- [ ] Implementar integração com RAG:
  - [ ] Consulta ao vector database
  - [ ] Retrieval de documentos relevantes
  - [ ] Múltiplas bases (técnico, segurança, compliance, jurídico)
- [ ] Implementar geração de respostas:
  - [ ] Com citações de origem
  - [ ] Identificação de parâmetros variáveis
  - [ ] Identificação de campos que exigem input humano
- [ ] Implementar suporte a perguntas avulsas
- [ ] Implementar consulta a RFPs históricas
- [ ] Integrar com LangChain Agent
- [ ] Adicionar métricas (qualidade de retrieval, tempo de resposta)
- [ ] Criar testes unitários
- [ ] Documentar processo de geração de respostas

---

## Tarefa 3.3: Agente Verificador (QA/Compliance)
**Prioridade**: Alta  
**Estimativa**: 5 dias  
**Responsável**: Backend

### Subtarefas:
- [ ] Criar classe base do Agente Verificador
- [ ] Implementar verificação de consistência:
  - [ ] Comparação entre respostas relacionadas
  - [ ] Detecção de contradições
- [ ] Implementar detecção de termos proibidos:
  - [ ] Lista de termos configurável
  - [ ] Busca case-insensitive
- [ ] Implementar detecção de lacunas:
  - [ ] Validação de campos obrigatórios
  - [ ] Detecção de respostas incompletas
- [ ] Implementar validação de limites contratuais
- [ ] Implementar verificação de formatação
- [ ] Implementar cálculo de score de confiança (0-100%)
- [ ] Implementar sinalização para revisão
- [ ] Integrar com LangChain como tool
- [ ] Adicionar métricas (taxa de detecção, falsos positivos)
- [ ] Criar testes unitários
- [ ] Documentar regras de validação

---

## Tarefa 3.4: Integração entre Agentes
**Prioridade**: Alta  
**Estimativa**: 3 dias  
**Responsável**: Backend

### Subtarefas:
- [ ] Integrar todos os agentes no LangGraph StateGraph
- [ ] Implementar comunicação A2A (Agent-to-Agent)
- [ ] Configurar fluxo de dados entre agentes
- [ ] Implementar execução paralela quando possível
- [ ] Adicionar tratamento de erros entre agentes
- [ ] Implementar retry logic
- [ ] Adicionar logging de interações
- [ ] Testar fluxo completo end-to-end
- [ ] Otimizar performance de comunicação
- [ ] Documentar padrões de comunicação

---

## Entregas do Sprint

Ao final deste sprint, deve-se ter:
- ✅ Agente Parser implementado e testado
- ✅ Agente Conhecimento implementado e testado
- ✅ Agente Verificador implementado e testado
- ✅ Todos os agentes integrados no workflow
- ✅ Comunicação A2A funcionando
- ✅ Testes unitários e de integração completos
- ✅ Documentação atualizada


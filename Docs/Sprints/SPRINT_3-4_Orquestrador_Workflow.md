# Sprint 3-4: Agente Orquestrador e Workflow Base (2 semanas)

## Objetivo
Implementar o Agente Orquestrador e criar o workflow base usando LangGraph, incluindo branching básico e gerenciamento de estado.

---

## Tarefa 2.1: Implementação do Agente Orquestrador
**Prioridade**: Alta  
**Estimativa**: 3 dias  
**Responsável**: Backend

### Subtarefas:
- [ ] Criar classe base do Agente Orquestrador
- [ ] Implementar identificação de tipo de input (pergunta única vs. questionário)
- [ ] Implementar coleta de contexto (cliente, produto, prazos)
- [ ] Implementar interface com humano (memória persistente)
- [ ] Implementar coordenação de agentes especialistas
- [ ] Integrar com LangChain Memory
- [ ] Adicionar logging detalhado
- [ ] Criar testes unitários
- [ ] Documentar API e uso

---

## Tarefa 2.2: Criação do Workflow Base com LangGraph
**Prioridade**: Alta  
**Estimativa**: 4 dias  
**Responsável**: Backend

### Subtarefas:
- [ ] Definir estrutura do StateGraph
- [ ] Criar schema de estado compartilhado
- [ ] Implementar nodes básicos:
  - [ ] Node de entrada
  - [ ] Node do Agente Orquestrador
  - [ ] Node de saída
- [ ] Implementar edges básicos
- [ ] Configurar checkpoint para persistência
- [ ] Integrar com LangGraph StateGraph
- [ ] Testar workflow básico end-to-end
- [ ] Adicionar métricas de execução
- [ ] Documentar estrutura do workflow

---

## Tarefa 2.3: Implementação de Branching Básico
**Prioridade**: Alta  
**Estimativa**: 2 dias  
**Responsável**: Backend

### Subtarefas:
- [ ] Implementar função de decisão (conditional edge)
- [ ] Branching: Pergunta única vs. Questionário
- [ ] Implementar routing baseado no tipo de input
- [ ] Testar ambos os caminhos
- [ ] Adicionar logging de decisões
- [ ] Documentar lógica de branching

---

## Tarefa 2.4: Gerenciamento de Estado
**Prioridade**: Alta  
**Estimativa**: 2 dias  
**Responsável**: Backend

### Subtarefas:
- [ ] Implementar persistência de estado do workflow
- [ ] Integrar com PostgreSQL para armazenamento
- [ ] Implementar recuperação de estado (checkpoint recovery)
- [ ] Implementar limpeza de estados antigos
- [ ] Testar persistência e recuperação
- [ ] Adicionar métricas de uso de estado
- [ ] Documentar gerenciamento de estado

---

## Entregas do Sprint

Ao final deste sprint, deve-se ter:
- ✅ Agente Orquestrador implementado e testado
- ✅ Workflow base com LangGraph funcionando
- ✅ Branching básico implementado (pergunta única vs. questionário)
- ✅ Gerenciamento de estado persistente funcionando
- ✅ Testes unitários e de integração
- ✅ Documentação atualizada


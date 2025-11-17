# Sprint 9-10: HITL e Interface Básica (2 semanas)

## Objetivo
Implementar HITL completo, interface web básica, finalizar observabilidade e realizar testes finais.

---

## Tarefa 5.1: Implementação de HITL Completo
**Prioridade**: Alta  
**Estimativa**: 3 dias  
**Responsável**: Backend

### Subtarefas:
- [ ] Implementar checkpoint no workflow que pausa para aprovação
- [ ] Criar modelo de dados para aprovações:
  - [ ] Status (pendente, aprovado, rejeitado)
  - [ ] Timestamp
  - [ ] Usuário aprovador
  - [ ] Comentários
- [ ] Implementar API endpoints para aprovação:
  - [ ] GET /approvals/pending
  - [ ] POST /approvals/{id}/approve
  - [ ] POST /approvals/{id}/reject
  - [ ] PUT /approvals/{id}/edit
- [ ] Implementar notificações para aprovação pendente
- [ ] Implementar histórico de aprovações
- [ ] Testar fluxo completo de HITL
- [ ] Adicionar métricas (tempo de aprovação, taxa de aprovação)
- [ ] Documentar API de aprovação

---

## Tarefa 5.2: Interface Web Básica
**Prioridade**: Alta  
**Estimativa**: 5 dias  
**Responsável**: Frontend/Fullstack

### Subtarefas:
- [ ] Escolher framework frontend (React, Vue, ou simples HTML/JS)
- [ ] Criar estrutura básica do projeto frontend
- [ ] Implementar página de listagem de RFPs:
  - [ ] Lista de RFPs processados
  - [ ] Status de cada RFP
  - [ ] Filtros básicos
- [ ] Implementar página de detalhes do RFP:
  - [ ] Visualização de perguntas e respostas
  - [ ] Score de confiança
  - [ ] Citações e fontes
- [ ] Implementar interface de aprovação:
  - [ ] Visualização de respostas geradas
  - [ ] Edição inline de respostas
  - [ ] Botões de aprovação/rejeição
  - [ ] Comentários
- [ ] Implementar página de exploração:
  - [ ] Upload de documentos
  - [ ] Visualização do workflow em execução
  - [ ] Logs de agentes
- [ ] Integrar com API backend
- [ ] Adicionar tratamento de erros
- [ ] Testar interface end-to-end
- [ ] Documentar uso da interface

---

## Tarefa 5.3: Observabilidade Completa
**Prioridade**: Alta  
**Estimativa**: 3 dias  
**Responsável**: Backend/DevOps

### Subtarefas:
- [ ] Finalizar integração Langfuse:
  - [ ] Rastreamento de todas as chamadas LLM
  - [ ] Captura de prompts e respostas
  - [ ] Métricas de tokens e custos
- [ ] Finalizar integração Prometheus:
  - [ ] Exportar métricas customizadas dos agentes
  - [ ] Métricas de tempo de execução por agente
  - [ ] Métricas de número de chamadas
  - [ ] Métricas de taxa de sucesso/falha
- [ ] Criar dashboards no Grafana:
  - [ ] Dashboard de sistema (CPU, memória, I/O)
  - [ ] Dashboard de aplicação (latência, throughput)
  - [ ] Dashboard de agentes (performance por agente)
  - [ ] Dashboard de LLMs (tokens, custos)
- [ ] Configurar alertas:
  - [ ] Alertas de erro crítico
  - [ ] Alertas de latência alta
  - [ ] Alertas de custo alto
- [ ] Testar observabilidade completa
- [ ] Documentar dashboards e alertas

---

## Tarefa 5.4: Exportação de Métricas Customizadas
**Prioridade**: Média  
**Estimativa**: 2 dias  
**Responsável**: Backend

### Subtarefas:
- [ ] Definir métricas customizadas dos agentes:
  - [ ] Tempo de execução por agente
  - [ ] Número de chamadas por agente
  - [ ] Taxa de sucesso/falha por agente
  - [ ] Qualidade de respostas (score médio)
- [ ] Implementar exportação para Prometheus
- [ ] Criar labels apropriados para métricas
- [ ] Testar coleta de métricas
- [ ] Validar visualização no Grafana
- [ ] Documentar métricas disponíveis

---

## Tarefa 5.5: Testes e Ajustes Finais
**Prioridade**: Alta  
**Estimativa**: 3 dias  
**Responsável**: Time completo

### Subtarefas:
- [ ] Executar testes end-to-end completos
- [ ] Testar com RFPs reais de diferentes formatos
- [ ] Validar todos os critérios de aceitação
- [ ] Corrigir bugs encontrados
- [ ] Otimizar performance onde necessário
- [ ] Revisar e melhorar documentação
- [ ] Preparar apresentação de resultados
- [ ] Coletar métricas de validação

---

## Entregas do Sprint

Ao final deste sprint, deve-se ter:
- ✅ HITL completo implementado e testado
- ✅ Interface web básica funcionando
- ✅ Observabilidade completa (Langfuse + Prometheus/Grafana)
- ✅ Métricas customizadas exportadas
- ✅ Testes end-to-end passando
- ✅ Sistema validado com RFPs reais
- ✅ Documentação completa
- ✅ MVP pronto para apresentação
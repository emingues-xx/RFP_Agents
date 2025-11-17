# Tarefas Detalhadas - Sistema de Agentes para Preenchimento de RFPs

## Visão Geral

Este diretório contém tarefas detalhadas e técnicas para implementação via Cursor. Cada tarefa inclui:
- Instruções passo a passo
- Código de exemplo
- Estrutura de arquivos
- Comandos específicos
- Checklist de validação

## Estrutura

### Sprint 1-2: Setup e Infraestrutura (2 semanas)

#### Tarefas Criadas:
- [TAREFA_1.1_Setup_Ambiente.md](./TAREFA_1.1_Setup_Ambiente.md) - Setup do ambiente de desenvolvimento (2 dias)
- [TAREFA_1.2_Docker_Compose.md](./TAREFA_1.2_Docker_Compose.md) - Docker Compose completo (3 dias)
- [TAREFA_1.3_Dependencias.md](./TAREFA_1.3_Dependencias.md) - Instalação de dependências (2 dias)
- [TAREFA_1.4_LLM_Providers.md](./TAREFA_1.4_LLM_Providers.md) - Configuração de LLM providers (1 dia)
- [TAREFA_1.5_Langfuse.md](./TAREFA_1.5_Langfuse.md) - Setup do Langfuse (1 dia)
- [TAREFA_1.6_Prometheus_Grafana.md](./TAREFA_1.6_Prometheus_Grafana.md) - Setup do Prometheus e Grafana (2 dias)

#### Tarefas Pendentes (ver Sprints):
- TAREFA_1.7: Setup de Banco de Dados e Vector Store (2 dias)
- TAREFA_1.8: CI/CD Básico (1 dia)

### Sprint 3-4: Agente Orquestrador e Workflow (2 semanas)

#### Tarefas Criadas:
- [TAREFA_2.1_Agente_Orquestrador.md](./TAREFA_2.1_Agente_Orquestrador.md) - Implementação do Orquestrador (3 dias)
- [TAREFA_2.2_Workflow_LangGraph.md](./TAREFA_2.2_Workflow_LangGraph.md) - Criação do Workflow Base (4 dias)

#### Tarefas Pendentes (ver Sprints):
- TAREFA_2.3: Implementação de Branching Básico (2 dias)
- TAREFA_2.4: Gerenciamento de Estado (2 dias)

### Sprint 5-6: Agentes Especialistas (3 semanas)
- Ver arquivo: [../Sprints/SPRINT_5-6_Agentes_Especialistas.md](../Sprints/SPRINT_5-6_Agentes_Especialistas.md)
- Tarefas serão criadas conforme necessário

### Sprint 7-8: Integrações Core (2 semanas)
- Ver arquivo: [../Sprints/SPRINT_7-8_Integracoes_Core.md](../Sprints/SPRINT_7-8_Integracoes_Core.md)
- Tarefas serão criadas conforme necessário

### Sprint 9-10: HITL e Interface Básica (2 semanas)
- Ver arquivo: [../Sprints/SPRINT_9-10_HITL_Interface.md](../Sprints/SPRINT_9-10_HITL_Interface.md)
- Tarefas serão criadas conforme necessário

## Como Usar

1. **Selecionar Tarefa**: Escolha a tarefa que deseja implementar
2. **Seguir Instruções**: Cada tarefa tem instruções passo a passo
3. **Validar**: Use o checklist de validação ao final
4. **Marcar como Concluída**: Atualize o status no arquivo do sprint correspondente

## Ordem Recomendada

### Sprint 1-2 (Sequencial):
1. **TAREFA_1.1** → Setup do ambiente
2. **TAREFA_1.2** → Docker Compose (CRÍTICO - permite rodar tudo local)
3. **TAREFA_1.3** → Dependências
4. **TAREFA_1.4** → LLM Providers
5. **TAREFA_1.5** → Langfuse
6. **TAREFA_1.6** → Prometheus/Grafana
7. TAREFA_1.7 → Banco de dados
8. TAREFA_1.8 → CI/CD

### Sprint 3-4 (Sequencial):
1. **TAREFA_2.1** → Agente Orquestrador
2. **TAREFA_2.2** → Workflow LangGraph
3. TAREFA_2.3 → Branching
4. TAREFA_2.4 → Gerenciamento de Estado

### Sprints Seguintes:
- Seguir ordem dos arquivos de Sprint correspondentes

## Notas

- Todas as tarefas incluem código de exemplo pronto para uso
- Comandos são específicos para Windows (PowerShell) quando aplicável
- Estrutura de arquivos está definida em cada tarefa
- Testes devem ser criados junto com a implementação

---

**Última Atualização**: 2025-01-XX


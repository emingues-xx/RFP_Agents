# TAREFA 1: Setup e Configuração do Ambiente

## Objetivo
Preparar todo o ambiente necessário para desenvolver e executar o sistema de agentes RFP.

## Passos para Finalização

### 1.1 - Setup do Ambiente de Desenvolvimento
**O que fazer:**
- Criar estrutura de pastas do projeto (backend, frontend, testes, documentação)
- Configurar repositório Git com branches (main, develop)
- Criar ambiente virtual Python
- Configurar ferramentas de qualidade de código (pre-commit, black, flake8)
- Criar arquivo .gitignore

**Como validar:**
- [ ] Estrutura de pastas criada corretamente
- [ ] Ambiente virtual Python funcionando
- [ ] Pre-commit hooks instalados e testados
- [ ] README.md criado com instruções básicas

**Tempo estimado:** 2 dias

---

### 1.2 - Docker Compose para Ambiente Local
**O que fazer:**
- Criar Dockerfile para a aplicação Python
- Configurar docker-compose.yml com todos os serviços:
  - Aplicação principal (backend)
  - Banco de dados PostgreSQL
  - Cache Redis
  - Banco vetorial Milvus (com etcd e MinIO)
  - Langfuse (observabilidade)
  - Prometheus e Grafana (métricas)
- Criar arquivo .env.example com todas as variáveis necessárias
- Configurar Prometheus para coletar métricas
- Configurar Grafana com dashboards básicos

**Como validar:**
- [ ] Todos os serviços sobem com `docker-compose up -d`
- [ ] Todos os serviços aparecem como "healthy"
- [ ] API responde em http://localhost:8000
- [ ] Langfuse acessível em http://localhost:3020
- [ ] Prometheus coletando métricas
- [ ] Grafana com dashboards funcionando

**Tempo estimado:** 3 dias

---

### 1.3 - Instalação e Configuração de Dependências
**O que fazer:**
- Criar requirements.txt com todas as bibliotecas Python necessárias
- Criar requirements-dev.txt com ferramentas de desenvolvimento
- Configurar pyproject.toml com configurações do projeto
- Testar instalação em ambiente limpo
- Documentar dependências principais no README

**Como validar:**
- [ ] requirements.txt criado com todas as dependências
- [ ] Instalação funciona em ambiente limpo
- [ ] Todas as importações funcionam corretamente
- [ ] Não há conflitos de versão entre dependências

**Tempo estimado:** 2 dias

---

### 1.4 - Configuração de Provedores de LLM
**O que fazer:**
- Criar sistema para configurar múltiplos provedores (OpenAI, Anthropic)
- Implementar fallback automático entre provedores
- Configurar variáveis de ambiente para API keys
- Criar factory para criar instâncias de LLM
- Testar conexão com ambos os provedores

**Como validar:**
- [ ] OpenAI configurado e funcionando
- [ ] Anthropic configurado e funcionando
- [ ] Fallback automático funciona quando um falha
- [ ] API keys seguras (não commitadas)

**Tempo estimado:** 2 dias

---

### 1.5 - Configuração do Langfuse
**O que fazer:**
- Subir serviços Langfuse no docker-compose
- Criar conta e obter API keys
- Configurar integração no código para rastrear chamadas LLM
- Testar rastreamento de chamadas

**Como validar:**
- [ ] Langfuse rodando e acessível
- [ ] Chamadas LLM aparecem no Langfuse
- [ ] Métricas de custo e tokens sendo coletadas

**Tempo estimado:** 1 dia

---

### 1.6 - Configuração de Prometheus e Grafana
**O que fazer:**
- Configurar Prometheus para coletar métricas da aplicação
- Criar dashboards no Grafana para visualizar métricas
- Configurar alertas básicos
- Testar coleta de métricas

**Como validar:**
- [ ] Prometheus coletando métricas da aplicação
- [ ] Dashboards no Grafana funcionando
- [ ] Métricas de HTTP, agentes, LLM sendo coletadas

**Tempo estimado:** 2 dias

---

## Resumo Final

**Total de tarefas:** 6 subtarefas  
**Tempo total estimado:** 12 dias  
**Prioridade:** Alta (bloqueante para outras tarefas)

**Checklist Geral:**
- [ ] Ambiente de desenvolvimento configurado
- [ ] Docker Compose funcionando com todos os serviços
- [ ] Dependências instaladas e testadas
- [ ] Provedores de LLM configurados
- [ ] Observabilidade (Langfuse, Prometheus, Grafana) funcionando
- [ ] Documentação básica criada

**Próximo passo:** Após completar todas as tarefas de Setup, seguir para TAREFA 2: Desenvolvimento dos Agentes


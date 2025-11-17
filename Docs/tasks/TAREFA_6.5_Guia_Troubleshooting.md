# Tarefa 6.5: Criação de Guia de Troubleshooting

## Objetivo
Criar guia completo de troubleshooting com problemas comuns e suas soluções.

## Prioridade
Média

## Estimativa
2 dias

## Responsável
Backend/DevOps

---

## Passos para Finalização

### 1. Identificar Problemas Comuns
**O que fazer:**
- Listar problemas que podem ocorrer:
  - Erros de conexão com banco de dados
  - Falhas de LLM providers
  - Problemas com RAG/vector store
  - Erros no workflow
  - Problemas de performance
  - Erros de memória
  - Problemas com Docker
  - Erros de autenticação/API keys

**Como validar:**
- [ ] Lista de problemas identificada
- [ ] Problemas categorizados por área
- [ ] Problemas críticos identificados

**Tempo estimado:** 0.5 dia

---

### 2. Criar Guia de Troubleshooting
**O que fazer:**
- Criar arquivo `docs/troubleshooting.md`
- Para cada problema, incluir:
  - Sintomas do problema
  - Causas possíveis
  - Passos de diagnóstico
  - Soluções passo a passo
  - Comandos de verificação
  - Prevenção

**Seções a criar:**
- Problemas de Infraestrutura
- Problemas com LLM Providers
- Problemas com Banco de Dados
- Problemas com RAG/Vector Store
- Problemas com Workflow
- Problemas de Performance
- Problemas com Docker

**Como validar:**
- [ ] Guia criado e organizado
- [ ] Todos os problemas comuns cobertos
- [ ] Soluções testadas
- [ ] Comandos validados

**Tempo estimado:** 1 dia

---

### 3. Criar Scripts de Diagnóstico
**O que fazer:**
- Criar scripts em `scripts/diagnostics/`:
  - `check-health.sh` - Verificar saúde geral
  - `check-db.sh` - Verificar banco de dados
  - `check-llm.sh` - Verificar LLM providers
  - `check-rag.sh` - Verificar RAG/vector store
  - `check-docker.sh` - Verificar containers
  - `collect-logs.sh` - Coletar logs para análise

**Como validar:**
- [ ] Scripts criados e funcionando
- [ ] Scripts fornecem informações úteis
- [ ] Scripts são fáceis de executar
- [ ] Scripts documentados

**Tempo estimado:** 0.5 dia

---

## Checklist de Validação

- [ ] Lista de problemas identificada
- [ ] Guia de troubleshooting criado
- [ ] Todas as seções preenchidas
- [ ] Soluções testadas
- [ ] Scripts de diagnóstico criados
- [ ] Guia revisado e validado

---

## Estrutura do Guia

```markdown
# Guia de Troubleshooting

## Problemas de Infraestrutura

### Problema: Serviços não iniciam
**Sintomas:** [Descrição]
**Causas:** [Lista]
**Diagnóstico:** [Passos]
**Solução:** [Passos]
**Prevenção:** [Dicas]

## Problemas com LLM Providers
...
```

---

## Próximo Passo
Após completar esta tarefa, seguir para: **Tarefa 6.6: Validação de Termos Proibidos**


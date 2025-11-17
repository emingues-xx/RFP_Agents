# Tarefa 6.1: Configuração do Alembic para Migrações de Banco de Dados

## Objetivo
Configurar Alembic para gerenciar migrações de banco de dados de forma versionada e controlada.

## Prioridade
Alta

## Estimativa
2 dias

## Responsável
Backend/DevOps

---

## Passos para Finalização

### 1. Instalar e Configurar Alembic
**O que fazer:**
- Adicionar `alembic` ao `requirements.txt`
- Criar arquivo `alembic.ini` na raiz do projeto
- Configurar conexão com banco de dados
- Criar estrutura de diretórios `alembic/versions/`

**Como validar:**
- [ ] Alembic instalado e funcionando
- [ ] `alembic.ini` criado e configurado
- [ ] Estrutura de diretórios criada
- [ ] Conexão com banco testada

**Tempo estimado:** 0.5 dia

---

### 2. Criar Migração Inicial
**O que fazer:**
- Criar migração inicial com todas as tabelas existentes:
  - `approval_requests` (tabela de aprovações)
  - `chat_history` (tabela de memória persistente)
  - Outras tabelas necessárias
- Revisar e ajustar migração
- Testar aplicação da migração

**Como validar:**
- [ ] Migração inicial criada
- [ ] Todas as tabelas definidas corretamente
- [ ] Migração aplica sem erros
- [ ] Estrutura do banco está correta após migração

**Tempo estimado:** 1 dia

---

### 3. Integrar com Docker e CI/CD
**O que fazer:**
- Atualizar `Dockerfile` para incluir Alembic
- Atualizar `docker-compose.yml` para executar migrações no startup
- Criar script de inicialização que executa migrações
- Documentar processo de migração

**Como validar:**
- [ ] Migrações executam automaticamente no Docker
- [ ] Script de inicialização funciona
- [ ] Documentação criada
- [ ] Processo testado em ambiente limpo

**Tempo estimado:** 0.5 dia

---

## Checklist de Validação

- [ ] Alembic instalado e configurado
- [ ] Migração inicial criada com todas as tabelas
- [ ] Migrações aplicam corretamente
- [ ] Integração com Docker funcionando
- [ ] Documentação criada
- [ ] Processo testado em ambiente limpo

---

## Comandos Úteis

```bash
# Inicializar Alembic
alembic init alembic

# Criar nova migração
alembic revision --autogenerate -m "Descrição da migração"

# Aplicar migrações
alembic upgrade head

# Reverter última migração
alembic downgrade -1

# Ver histórico de migrações
alembic history

# Ver status atual
alembic current
```

---

## Próximo Passo
Após completar esta tarefa, seguir para: **Tarefa 6.2: Queue System para Escalabilidade**


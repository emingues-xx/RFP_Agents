# Tarefa 6.7: Sistema de Auditoria Completo

## Objetivo
Completar sistema de auditoria para rastrear todas as ações e mudanças no sistema para compliance e segurança.

## Prioridade
Média

## Estimativa
3 dias

## Responsável
Backend

---

## Passos para Finalização

### 1. Definir Eventos de Auditoria
**O que fazer:**
- Listar eventos que devem ser auditados:
  - Criação de RFP
  - Processamento de RFP
  - Aprovações/rejeições
  - Edições de respostas
  - Acesso a dados sensíveis
  - Mudanças de configuração
  - Acesso de usuários
  - Erros críticos

**Como validar:**
- [ ] Lista de eventos definida
- [ ] Eventos categorizados
- [ ] Eventos críticos identificados

**Tempo estimado:** 0.5 dia

---

### 2. Criar Modelo de Dados de Auditoria
**O que fazer:**
- Criar tabela `audit_logs` no banco de dados
- Campos: timestamp, user_id, event_type, resource_type, resource_id, action, details, ip_address
- Criar migração Alembic
- Criar modelo Pydantic para validação

**Como validar:**
- [ ] Modelo de dados criado
- [ ] Migração criada e aplicada
- [ ] Modelo Pydantic criado
- [ ] Estrutura testada

**Tempo estimado:** 0.5 dia

---

### 3. Implementar Logger de Auditoria
**O que fazer:**
- Criar classe `AuditLogger` em `src/backend/src/utils/audit_logger.py`
- Implementar métodos para logar diferentes tipos de eventos
- Integrar com sistema existente
- Garantir que logs são escritos de forma assíncrona

**Como validar:**
- [ ] AuditLogger criado
- [ ] Métodos implementados
- [ ] Integração funcionando
- [ ] Logs são escritos corretamente

**Tempo estimado:** 1 dia

---

### 4. Integrar Auditoria em Pontos Críticos
**O que fazer:**
- Adicionar logging de auditoria em:
  - Criação/processamento de RFPs
  - Aprovações/rejeições
  - Edições de respostas
  - Acesso a dados
  - Mudanças de configuração
- Garantir que todos os eventos críticos são logados

**Como validar:**
- [ ] Auditoria integrada em todos os pontos críticos
- [ ] Eventos são logados corretamente
- [ ] Informações sensíveis não são logadas
- [ ] Performance não é impactada

**Tempo estimado:** 1 dia

---

### 5. Criar API para Consultar Logs
**O que fazer:**
- Criar endpoint GET `/audit/logs` para consultar logs
- Suportar filtros: data, usuário, tipo de evento, recurso
- Implementar paginação
- Adicionar autenticação/autorização (apenas admins)

**Como validar:**
- [ ] Endpoint criado
- [ ] Filtros funcionando
- [ ] Paginação implementada
- [ ] Autenticação funcionando

**Tempo estimado:** 0.5 dia

---

## Checklist de Validação

- [ ] Eventos de auditoria definidos
- [ ] Modelo de dados criado
- [ ] AuditLogger implementado
- [ ] Auditoria integrada em pontos críticos
- [ ] API para consultar logs criada
- [ ] Testes criados e passando
- [ ] Documentação criada

---

## Estrutura do Log de Auditoria

```python
{
    "timestamp": "2025-11-17T10:30:00Z",
    "user_id": "user-123",
    "event_type": "approval",
    "resource_type": "rfp",
    "resource_id": "rfp-456",
    "action": "approved",
    "details": {
        "approval_id": "approval-789",
        "responses_count": 20
    },
    "ip_address": "192.168.1.1"
}
```

---

## Próximo Passo
Após completar esta tarefa, seguir para: **Tarefa 6.8: Integração com Portais via MCP**


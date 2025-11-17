# Tarefa 6.6: Validação de Termos Proibidos no Agente Verificador

## Objetivo
Completar implementação de validação de termos proibidos no Agente Verificador para garantir compliance.

## Prioridade
Alta

## Estimativa
2 dias

## Responsável
Backend

---

## Passos para Finalização

### 1. Verificar Implementação Atual
**O que fazer:**
- Revisar código do Agente Verificador (`src/backend/src/agents/verifier.py`)
- Verificar se já existe validação de termos proibidos
- Identificar o que está faltando
- Documentar funcionalidades existentes

**Como validar:**
- [ ] Código revisado
- [ ] Funcionalidades existentes documentadas
- [ ] Gaps identificados

**Tempo estimado:** 0.5 dia

---

### 2. Criar Base de Termos Proibidos
**O que fazer:**
- Criar arquivo de configuração com termos proibidos
- Organizar por categoria (jurídico, compliance, segurança)
- Criar sistema para carregar termos de arquivo ou banco de dados
- Permitir atualização dinâmica de termos

**Como validar:**
- [ ] Base de termos criada
- [ ] Termos organizados por categoria
- [ ] Sistema carrega termos corretamente
- [ ] Atualização dinâmica funciona

**Tempo estimado:** 0.5 dia

---

### 3. Implementar Validação
**O que fazer:**
- Implementar função que verifica termos proibidos em respostas
- Usar busca exata e fuzzy matching
- Identificar contexto onde termo aparece
- Gerar alerta detalhado quando termo proibido é encontrado
- Integrar com workflow para rejeição automática

**Como validar:**
- [ ] Validação implementada
- [ ] Detecta termos proibidos corretamente
- [ ] Gera alertas detalhados
- [ ] Rejeição automática funciona
- [ ] Testes criados e passando

**Tempo estimado:** 1 dia

---

## Checklist de Validação

- [ ] Implementação atual revisada
- [ ] Base de termos proibidos criada
- [ ] Validação implementada e funcionando
- [ ] Alertas gerados corretamente
- [ ] Rejeição automática funciona
- [ ] Testes criados e passando
- [ ] Documentação atualizada

---

## Exemplo de Implementação

```python
class ForbiddenTermsValidator:
    def __init__(self, terms_file: str):
        self.forbidden_terms = self._load_terms(terms_file)
    
    def validate(self, text: str) -> ValidationResult:
        found_terms = []
        for term in self.forbidden_terms:
            if term.lower() in text.lower():
                found_terms.append(term)
        
        return ValidationResult(
            has_forbidden_terms=len(found_terms) > 0,
            forbidden_terms=found_terms,
            severity="high" if found_terms else "none"
        )
```

---

## Próximo Passo
Após completar esta tarefa, seguir para: **Tarefa 6.7: Sistema de Auditoria Completo**


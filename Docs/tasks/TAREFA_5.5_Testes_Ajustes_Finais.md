# Tarefa 5.5: Testes e Ajustes Finais

## Objetivo
Executar testes end-to-end completos, validar critérios de aceitação, corrigir bugs e preparar sistema para apresentação.

## Prioridade
Alta

## Estimativa
3 dias

## Responsável
Time completo

---

## Instruções de Implementação

### 1. Executar Testes End-to-End Completos

#### Criar `tests/e2e/test_full_workflow.py`:
```python
"""Testes end-to-end do workflow completo."""
import pytest
from src.workflows.workflow import RFPWorkflow
from langgraph.checkpoint.memory import MemorySaver

@pytest.fixture
def workflow():
    checkpoint = MemorySaver()
    return RFPWorkflow(checkpoint_saver=checkpoint)

def test_full_workflow_single_question(workflow):
    """Testar workflow completo com pergunta única."""
    result = workflow.run(
        input_text="Qual é o SLA do produto?",
        session_id="e2e-test-1"
    )
    
    assert result["current_step"] == "completed"
    assert result["input_type"] in ["single_question", "questionnaire", "unknown"]
    assert "generated_responses" in result

def test_full_workflow_questionnaire(workflow):
    """Testar workflow completo com questionário."""
    input_text = """
    Pergunta 1: Qual é o SLA?
    Pergunta 2: Qual é o suporte oferecido?
    Pergunta 3: Qual é o preço?
    """
    result = workflow.run(
        input_text=input_text,
        session_id="e2e-test-2"
    )
    
    assert result["current_step"] == "completed"
    assert result.get("parsed_questions") is not None
    assert result.get("generated_responses") is not None
    assert result.get("verified_responses") is not None

def test_full_workflow_with_hitl(workflow):
    """Testar workflow completo com HITL."""
    # Implementar teste com aprovação
    pass
```

### 2. Testar com RFPs Reais de Diferentes Formatos

#### Criar `tests/e2e/test_real_rfps.py`:
```python
"""Testes com RFPs reais."""
import pytest
from pathlib import Path

@pytest.mark.skipif(
    not Path("test_data/rfps").exists(),
    reason="Pasta de RFPs de teste não encontrada"
)
def test_process_pdf_rfp():
    """Testar processamento de RFP em PDF."""
    # Implementar teste com PDF real
    pass

@pytest.mark.skipif(
    not Path("test_data/rfps").exists(),
    reason="Pasta de RFPs de teste não encontrada"
)
def test_process_docx_rfp():
    """Testar processamento de RFP em DOCX."""
    # Implementar teste com DOCX real
    pass

@pytest.mark.skipif(
    not Path("test_data/rfps").exists(),
    reason="Pasta de RFPs de teste não encontrada"
)
def test_process_excel_rfp():
    """Testar processamento de RFP em Excel."""
    # Implementar teste com Excel real
    pass
```

### 3. Validar Todos os Critérios de Aceitação

#### Criar `tests/acceptance/test_acceptance_criteria.py`:
```python
"""Testes de critérios de aceitação."""
import pytest

def test_criteria_rf_001():
    """RF-001: Agente Orquestrador."""
    # Deve identificar automaticamente tipo de input
    # Deve solicitar aprovação humana
    # Deve manter contexto em memória persistente
    # Deve coordenar múltiplos agentes
    pass

def test_criteria_rf_002():
    """RF-002: Agente Parser."""
    # Deve processar PDF, DOCX e planilhas
    # Deve aplicar OCR em PDFs escaneados
    # Deve normalizar em formato canônico
    # Deve identificar perguntas similares
    pass

def test_criteria_rf_003():
    """RF-003: Agente Conhecimento."""
    # Deve retornar respostas com citações
    # Deve identificar quando requer input humano
    # Deve funcionar para questionários e perguntas avulsas
    # Deve consultar múltiplas bases
    pass

def test_criteria_rf_004():
    """RF-004: Agente Verificador."""
    # Deve verificar consistência
    # Deve identificar termos proibidos
    # Deve detectar lacunas
    # Deve calcular score de confiança
    pass
```

### 4. Corrigir Bugs Encontrados

#### Criar `docs/bugs/bug_tracking.md`:
```markdown
# Bug Tracking

## Bugs Encontrados

### Bug #1: [Descrição]
- Status: [Aberto/Resolvido]
- Prioridade: [Alta/Média/Baixa]
- Passos para reproduzir:
  1. ...
  2. ...
- Solução: [Se resolvido]
```

### 5. Otimizar Performance Onde Necessário

#### Criar `docs/performance/optimizations.md`:
```markdown
# Otimizações de Performance

## Áreas Otimizadas

1. **Retrieval RAG**: Implementado cache de embeddings
2. **Parser**: Processamento paralelo de múltiplos arquivos
3. **Workflow**: Redução de chamadas LLM desnecessárias
```

### 6. Revisar e Melhorar Documentação

#### Checklist de documentação:
- [ ] README.md atualizado
- [ ] Documentação de agentes completa
- [ ] Documentação de workflows completa
- [ ] Documentação de API completa
- [ ] Guias de instalação e configuração
- [ ] Exemplos de uso

### 7. Preparar Apresentação de Resultados

#### Criar `docs/presentation/slides.md`:
```markdown
# Apresentação de Resultados

## Slides

1. Visão Geral do Sistema
2. Arquitetura
3. Funcionalidades Implementadas
4. Métricas e Performance
5. Demonstração
6. Próximos Passos
```

### 8. Coletar Métricas de Validação

#### Criar `docs/validation/metrics.md`:
```markdown
# Métricas de Validação

## Performance
- Tempo médio de processamento: X segundos
- Taxa de sucesso: X%
- Throughput: X RFPs/hora

## Qualidade
- Precisão de identificação de tipo: X%
- Score médio de confiança: X%
- Taxa de aprovação: X%

## Custo
- Custo médio por RFP: $X
- Custo de LLM por mês: $X
```

---

## Checklist de Validação

- [ ] Testes end-to-end executados e passando
- [ ] Testes com RFPs reais de diferentes formatos executados
- [ ] Todos os critérios de aceitação validados
- [ ] Bugs encontrados corrigidos
- [ ] Performance otimizada onde necessário
- [ ] Documentação revisada e melhorada
- [ ] Apresentação de resultados preparada
- [ ] Métricas de validação coletadas

---

## Comandos de Teste

```bash
# Executar todos os testes
pytest tests/ -v

# Executar testes end-to-end
pytest tests/e2e/ -v

# Executar testes de aceitação
pytest tests/acceptance/ -v

# Gerar relatório de cobertura
pytest --cov=src --cov-report=html tests/
```


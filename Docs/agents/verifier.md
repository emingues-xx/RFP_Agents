# Agente Verificador

## Visão Geral

O Agente Verificador é responsável por validar qualidade, consistência e compliance das respostas geradas pelo Knowledge Agent. Ele detecta problemas, calcula scores de confiança e sinaliza quando uma resposta precisa de revisão humana.

## Funcionalidades

### 1. Verificação de Consistência
- Compara respostas relacionadas para detectar contradições
- Agrupa respostas por categoria
- Usa LLM para verificar contradições semânticas

### 2. Detecção de Termos Proibidos
- Identifica termos que podem causar problemas contratuais
- Lista configurável de termos proibidos
- Exemplos: "garantimos 100%", "sem exceções", "sempre"

### 3. Detecção de Lacunas
- Verifica se resposta está muito curta ou vazia
- Identifica keywords mencionadas na pergunta mas não na resposta
- Detecta campos obrigatórios faltantes (SLA, garantia, suporte, preço, etc.)

### 4. Validação de Limites Contratuais
- Detecta promessas excessivas (ex: 100% de disponibilidade)
- Identifica uso de termos absolutos problemáticos
- Valida aderência a regras configuráveis

### 5. Verificação de Formatação
- Valida formato esperado (sim/não, número, lista, data)
- Detecta erros de formatação
- Suporta múltiplos formatos

### 6. Cálculo de Score de Confiança
- Calcula score baseado em problemas detectados
- Penaliza por termos proibidos, lacunas, inconsistências
- Score final de 0-100%

### 7. Sinalização para Revisão
- Determina se resposta precisa de revisão humana
- Baseado em múltiplos critérios
- Threshold configurável (padrão: 70%)

## Formato de Resposta

### VerifiedResponse

```python
{
    "qid": "Q001",                              # ID da pergunta
    "response_text": "Resposta original...",    # Texto da resposta
    "confidence_score": 0.85,                   # Score de confiança (0.0-1.0)
    "is_consistent": true,                      # Se é consistente com outras respostas
    "has_prohibited_terms": false,             # Se contém termos proibidos
    "has_gaps": false,                         # Se tem lacunas
    "validation_errors": [],                    # Lista de erros encontrados
    "needs_review": false                       # Se precisa revisão humana
}
```

## Uso

### Exemplo Básico

```python
from src.agents.verifier import VerifierAgent
from src.workflows.schema import GeneratedResponse
from src.utils.llm_factory import LLMFactory

# Criar factory e LLM
factory = LLMFactory()
llm = factory.get_default_llm()

# Criar verifier agent
verifier = VerifierAgent(llm=llm)

# Resposta gerada
response = GeneratedResponse(
    qid="Q001",
    response_text="O SLA do produto é de 99.9% de disponibilidade",
    confidence_score=0.9
)

# Verificar
verified = verifier.verify(
    question="Qual é o SLA do produto?",
    response=response
)

print(f"Confiança: {verified.confidence_score:.2%}")
print(f"Precisa revisão: {verified.needs_review}")
print(f"Erros: {verified.validation_errors}")
```

### Exemplo com Múltiplas Respostas

```python
# Verificar consistência entre múltiplas respostas
responses = [
    GeneratedResponse(qid="Q001", response_text="...", confidence_score=0.9),
    GeneratedResponse(qid="Q002", response_text="...", confidence_score=0.8)
]

# Verificar primeira resposta considerando todas
verified = verifier.verify(
    question="Qual é o SLA?",
    response=responses[0],
    all_responses=responses
)
```

### Exemplo com Formato Esperado

```python
verified = verifier.verify(
    question="O produto tem suporte 24/7?",
    response=response,
    expected_format="sim/não"
)
```

### Exemplo de Verificação em Lote

```python
questions_and_responses = [
    {
        "question": "Qual é o SLA?",
        "response": GeneratedResponse(qid="Q001", ...)
    },
    {
        "question": "Qual é o preço?",
        "response": GeneratedResponse(qid="Q002", ...)
    }
]

verified_responses = verifier.verify_batch(questions_and_responses)
```

### Exemplo com Tool do LangChain

```python
from src.tools.verifier_tool import verify_response_tool

# Usar como tool
result = verify_response_tool.invoke({
    "question": "Qual é o SLA?",
    "response": "O SLA é de 99.9%",
    "qid": "Q001"
})
```

## Métodos Principais

### `verify()`
Verifica uma resposta completa, executando todas as validações.

**Parâmetros:**
- `question`: Pergunta original
- `response`: `GeneratedResponse` a ser verificada
- `all_responses`: Lista opcional de todas as respostas (para verificar consistência)
- `expected_format`: Formato esperado (sim/não, número, lista, data)

**Retorna:** `VerifiedResponse`

### `verify_batch()`
Verifica múltiplas respostas em lote.

**Parâmetros:**
- `questions_and_responses`: Lista de dicionários com "question" e "response"
- `expected_formats`: Dicionário opcional mapeando qid para formato esperado

**Retorna:** Lista de `VerifiedResponse`

### `check_consistency()`
Verifica consistência entre múltiplas respostas.

**Parâmetros:**
- `responses`: Lista de `GeneratedResponse`

**Retorna:** Dict com `is_consistent` e `inconsistencies`

### `detect_prohibited_terms()`
Detecta termos proibidos na resposta.

**Parâmetros:**
- `response_text`: Texto da resposta

**Retorna:** Lista de termos proibidos encontrados

### `detect_gaps()`
Detecta lacunas na resposta.

**Parâmetros:**
- `question`: Pergunta original
- `response`: `GeneratedResponse`

**Retorna:** Lista de lacunas detectadas

## Métricas

O Verifier Agent expõe as seguintes métricas Prometheus:

- `verifier_validations_total`: Total de validações por status (approved/needs_review)
- `verifier_detections_total`: Total de problemas detectados por tipo:
  - `prohibited_terms`: Termos proibidos
  - `gaps`: Lacunas
  - `inconsistencies`: Inconsistências
  - `contractual_violations`: Violações contratuais
  - `formatting_errors`: Erros de formatação

## Termos Proibidos

Lista padrão de termos proibidos (configurável):
- "garantimos 100%"
- "sem exceções"
- "sempre"
- "nunca falha"
- "garantia absoluta"
- "100% garantido"
- "zero falhas"
- "perfeito"
- "infalível"

## Cálculo de Score

O score de confiança é calculado da seguinte forma:

1. **Score base**: `response.confidence_score * 100`
2. **Penalizações**:
   - Termos proibidos: -20 pontos
   - Lacunas: -15 pontos por lacuna (máx. 30)
   - Inconsistências: -10 pontos
   - Erros de formatação: -5 pontos por erro
   - Violações contratuais: -15 pontos
3. **Score final**: `max(0.0, min(100.0, score))`

## Sinalização para Revisão

Uma resposta precisa de revisão se:
- Não é consistente com outras respostas
- Contém termos proibidos
- Tem lacunas
- Não é válida contratualmente
- Tem erros de formatação
- Score de confiança < 70%

## Tratamento de Erros

- Erros de LLM retornam resultado conservador (assume não contraditório)
- Erros de parsing são logados e não bloqueiam verificação
- Todos os erros são logados para debugging

## Próximos Passos

1. Carregar termos proibidos de arquivo de configuração
2. Implementar regras contratuais configuráveis
3. Adicionar cache de verificações similares
4. Suporte a regras customizadas por cliente
5. Integração com sistema de aprovação


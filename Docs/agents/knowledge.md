# Agente Conhecimento

## Visão Geral

O Agente Conhecimento é responsável por consultar a base de conhecimento via RAG (Retrieval-Augmented Generation) e gerar respostas contextualizadas com citações de origem.

## Funcionalidades

### 1. Consulta RAG
- Busca semântica em vector database
- Filtros por categoria (técnico, segurança, compliance, jurídico)
- Recuperação de documentos relevantes
- Suporte a múltiplas bases de conhecimento

### 2. Geração de Respostas
- Respostas baseadas em documentos recuperados
- Citações de origem ([1], [2], etc.)
- Identificação de parâmetros variáveis
- Detecção de campos que exigem input humano

### 3. Suporte a Múltiplas Bases
- Consulta simultânea em diferentes categorias
- Agregação de resultados de múltiplas fontes
- Priorização por relevância

## Formato de Resposta

### GeneratedResponse

```python
{
    "qid": "Q001",                              # ID da pergunta
    "response_text": "Resposta completa...",    # Texto da resposta com citações
    "confidence_score": 0.85,                   # Score de confiança (0.0-1.0)
    "citations": ["doc1.pdf", "doc2.pdf"],      # Fontes citadas
    "requires_human_input": false,              # Se requer input humano
    "human_input_fields": []                    # Campos que precisam de input
}
```

## Uso

### Exemplo Básico

```python
from src.agents.knowledge import KnowledgeAgent
from src.utils.llm_factory import LLMFactory

# Criar factory e LLM
factory = LLMFactory()
llm = factory.get_default_llm()

# Criar knowledge agent (sem vector store por enquanto)
agent = KnowledgeAgent(llm=llm)

# Gerar resposta
response = agent.generate_response(
    question="Qual é o SLA do produto?",
    qid="Q001"
)

print(f"Resposta: {response.response_text}")
print(f"Confiança: {response.confidence_score}")
print(f"Citações: {response.citations}")
```

### Exemplo com Contexto

```python
context = {
    "client": "ABC Corp",
    "product": "Cloud Services",
    "category": "técnico"
}

response = agent.generate_response(
    question="Qual é o SLA?",
    context=context,
    qid="Q001"
)
```

### Exemplo com Múltiplas Perguntas

```python
questions = [
    {
        "qid": "Q001",
        "question_text": "Qual é o SLA?",
        "category": "técnico"
    },
    {
        "qid": "Q002",
        "question_text": "Qual é o preço?",
        "category": "comercial"
    }
]

responses = agent.generate_responses(questions, context=context)
```

### Exemplo com Múltiplas Bases

```python
# Consultar em múltiplas categorias
results = agent.retrieve_from_multiple_bases(
    query="Qual é o SLA?",
    categories=["técnico", "segurança", "compliance"]
)

for category, docs in results.items():
    print(f"{category}: {len(docs)} documentos")
```

### Exemplo com Tool do LangChain

```python
from src.tools.knowledge_tool import knowledge_query_tool

# Usar como tool
result = knowledge_query_tool.invoke({
    "question": "Qual é o SLA?",
    "category": "técnico"
})
```

## Integração com Vector Store

O KnowledgeAgent aceita um `VectorStore` opcional. Quando configurado:

- Realiza busca semântica para recuperar documentos relevantes
- Filtra por categoria quando especificado
- Usa documentos recuperados como contexto para geração

Quando não configurado:
- Gera respostas baseadas apenas no conhecimento do LLM
- Ainda funciona, mas sem acesso à base de conhecimento estruturada

## Métricas

O Knowledge Agent expõe as seguintes métricas Prometheus:

- `knowledge_queries_total`: Total de queries por categoria e status
- `knowledge_retrieval_duration_seconds`: Duração de retrieval
- `knowledge_response_quality`: Score de qualidade das respostas (confidence_score)

## Tratamento de Erros

- Erros de retrieval retornam lista vazia de documentos
- Erros de parsing JSON retornam resposta com erro e confidence_score = 0.0
- Todos os erros são logados para debugging

## Próximos Passos

1. Integração completa com vector store (TAREFA_4.1)
2. Implementação de consulta a RFPs históricas
3. Re-ranking de documentos recuperados
4. Cache de respostas frequentes
5. Suporte a streaming de respostas


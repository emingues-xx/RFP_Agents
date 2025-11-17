# Custom Tools

Este documento descreve as custom tools disponíveis para os agentes do sistema.

## Visão Geral

As custom tools são ferramentas especializadas que podem ser usadas pelos agentes para realizar tarefas específicas como extração de texto, OCR, consulta RAG, validação de compliance e mapeamento de perguntas similares.

## Tools Disponíveis

### extract_text_tool

Extrai texto de arquivos em vários formatos.

**Parâmetros:**
- `file_path` (str): Caminho do arquivo
- `file_type` (str, opcional): Tipo do arquivo (detecta automaticamente se não fornecido)

**Formatos suportados:**
- PDF (.pdf)
- Word (.docx, .doc)
- Excel (.xlsx, .xls)
- CSV (.csv)

**Retorna:**
- Texto extraído do arquivo

**Exemplo:**
```python
from src.tools.custom_tools import extract_text_tool

text = extract_text_tool.invoke({
    "file_path": "documento.pdf"
})
```

### ocr_tool

Aplica OCR (Optical Character Recognition) em imagens para extrair texto.

**Parâmetros:**
- `image_path` (str): Caminho da imagem
- `language` (str, opcional): Idioma (padrão: "por" para português)

**Retorna:**
- Texto extraído da imagem

**Exemplo:**
```python
from src.tools.custom_tools import ocr_tool

text = ocr_tool.invoke({
    "image_path": "imagem.png",
    "language": "por"
})
```

**Nota:** Requer PIL e pytesseract instalados. Para PDFs escaneados, use `extract_text_tool` com `use_ocr=True`.

### rag_query_tool

Consulta a base de conhecimento via RAG (Retrieval-Augmented Generation).

**Parâmetros:**
- `query` (str): Query de busca
- `category` (str, opcional): Categoria para filtrar (técnico, segurança, compliance, jurídico)
- `top_k` (int, opcional): Número de documentos a retornar (padrão: 5)

**Retorna:**
- Resumo dos documentos encontrados com citações e fontes

**Exemplo:**
```python
from src.tools.custom_tools import rag_query_tool

results = rag_query_tool.invoke({
    "query": "Qual é o SLA do produto?",
    "category": "técnico",
    "top_k": 5
})
```

### compliance_validation_tool

Valida compliance de uma resposta, verificando termos proibidos, lacunas e outros problemas.

**Parâmetros:**
- `response_text` (str): Texto da resposta a validar

**Retorna:**
- Resultado da validação em formato JSON com:
  - `has_prohibited_terms`: Se contém termos proibidos
  - `has_gaps`: Se tem lacunas
  - `needs_review`: Se precisa revisão humana
  - `confidence_score`: Score de confiança (0.0-1.0)
  - `is_consistent`: Se é consistente
  - `validation_errors`: Lista de erros encontrados

**Exemplo:**
```python
from src.tools.custom_tools import compliance_validation_tool
import json

result = compliance_validation_tool.invoke({
    "response_text": "Garantimos 100% de disponibilidade"
})
validation = json.loads(result)
print(f"Precisa revisão: {validation['needs_review']}")
```

### map_similar_questions_tool

Mapeia uma pergunta para perguntas similares no histórico usando busca semântica.

**Parâmetros:**
- `question` (str): Pergunta a mapear
- `top_k` (int, opcional): Número de perguntas similares a retornar (padrão: 5)

**Retorna:**
- Lista de perguntas similares encontradas com informações de fonte

**Exemplo:**
```python
from src.tools.custom_tools import map_similar_questions_tool

results = map_similar_questions_tool.invoke({
    "question": "Qual é o SLA?",
    "top_k": 3
})
```

## Uso em Agentes

As tools podem ser usadas diretamente pelos agentes ou através do LangChain:

```python
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.tools import ALL_TOOLS

# Criar agente com todas as tools
prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente útil."),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_openai_functions_agent(llm, prompt, ALL_TOOLS)
agent_executor = AgentExecutor(agent=agent, tools=ALL_TOOLS)
```

## Métricas

Todas as tools rastreiam métricas automaticamente:
- `tool_usage_total`: Total de uso por tool e status (success/error)

As métricas são expostas via Prometheus em `/metrics`.

## Tratamento de Erros

Todas as tools tratam erros graciosamente:
- Retornam mensagens de erro descritivas
- Registram erros nos logs
- Atualizam métricas de erro
- Não interrompem o fluxo do agente

## Próximos Passos

- Adicionar mais tools conforme necessário
- Implementar cache de resultados
- Adicionar rate limiting
- Suporte a streaming de resultados


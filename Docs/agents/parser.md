# Agente Parser

## Visão Geral

O Agente Parser é responsável por extrair e normalizar perguntas de diferentes formatos de entrada (PDF, DOCX, planilhas Excel/CSV) e mapeá-las para perguntas históricas.

## Funcionalidades

### 1. Extração de Documentos
- **PDF**: Extração direta de texto e suporte a OCR para PDFs escaneados
- **DOCX**: Extração de parágrafos e tabelas
- **Excel**: Extração de todas as planilhas
- **CSV**: Extração de dados tabulares

### 2. Normalização
- Identificação automática de perguntas
- Categorização (técnico, segurança, compliance, jurídico, comercial)
- Extração de requisitos
- Identificação de formato esperado de resposta

### 3. Mapeamento Histórico
- Mapeamento para perguntas similares do histórico
- Cálculo de confiança de similaridade (quando vector store disponível)

## Formato Canônico

### ParsedQuestion

```python
{
    "qid": "Q001",                    # Identificador único
    "category": "técnico",            # Categoria da pergunta
    "question_text": "Qual é o SLA?", # Texto normalizado
    "requirements": ["SLA", "99.9%"], # Requisitos mencionados
    "expected_format": "texto",       # Formato esperado
    "similar_questions": []          # Perguntas similares (preenchido no mapeamento)
}
```

### Categorias Suportadas
- `técnico`: Questões técnicas sobre o produto/serviço
- `segurança`: Questões de segurança e compliance
- `compliance`: Questões de conformidade regulatória
- `jurídico`: Questões legais e contratuais
- `comercial`: Questões comerciais (preço, condições)
- `geral`: Outras categorias

### Formatos Esperados
- `texto`: Resposta em texto livre
- `número`: Resposta numérica
- `sim/não`: Resposta binária
- `lista`: Lista de itens
- `tabela`: Dados tabulares
- `data`: Data específica

## Uso

### Exemplo Básico

```python
from src.agents.parser import ParserAgent
from src.utils.llm_factory import LLMFactory

# Criar factory e LLM
factory = LLMFactory()
llm = factory.get_default_llm()

# Criar parser
parser = ParserAgent(llm=llm)

# Processar texto
questions = parser.process("Pergunta 1: Qual é o SLA?\nPergunta 2: Qual é o preço?")

# Processar arquivo
questions = parser.process("", file_path="/path/to/questionnaire.pdf")
```

### Exemplo com OCR

```python
# Para PDFs escaneados, usar OCR
text = parser.extract_from_pdf("/path/to/scanned.pdf", use_ocr=True)
questions = parser.normalize_questions(text)
```

### Exemplo com Tool do LangChain

```python
from src.tools.parser_tool import parse_questionnaire_tool, parse_text_questions_tool

# Processar arquivo
result = parse_questionnaire_tool.invoke({
    "file_path": "/path/to/questionnaire.xlsx",
    "use_ocr": False
})

# Processar texto
result = parse_text_questions_tool.invoke({
    "text": "Pergunta 1: ...\nPergunta 2: ..."
})
```

## Métricas

O Parser expõe as seguintes métricas Prometheus:

- `parser_extractions_total`: Total de extrações por tipo de arquivo e status
- `parser_extraction_duration_seconds`: Duração de extração por tipo
- `parser_questions_normalized_total`: Total de perguntas normalizadas por categoria

## Tratamento de Erros

- Erros de extração são logados e propagados
- Erros de normalização retornam lista vazia
- OCR é opcional e requer dependências adicionais
- Fallback para PyPDF2 quando pdfplumber falha

## Dependências

### Obrigatórias
- `pdfplumber`: Extração de PDF
- `python-docx`: Extração de DOCX
- `pandas`: Processamento de planilhas
- `openpyxl`: Leitura de Excel

### Opcionais (para OCR)
- `Pillow`: Processamento de imagens
- `pytesseract`: OCR
- `pdf2image`: Conversão PDF para imagem

## Próximos Passos

1. Integração com vector store para mapeamento histórico semântico
2. Suporte a mais formatos (ODT, RTF, etc.)
3. Melhoria na detecção de categorias
4. Cache de extrações para performance
5. Processamento paralelo de múltiplos arquivos


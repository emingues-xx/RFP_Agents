# Tarefa 6.3: Implementação de Streaming de Respostas

## Objetivo
Implementar streaming de respostas da API para melhorar experiência do usuário, mostrando respostas conforme são geradas.

## Prioridade
Média

## Estimativa
2 dias

## Responsável
Backend

---

## Passos para Finalização

### 1. Implementar Streaming no Workflow
**O que fazer:**
- Modificar workflow para suportar streaming
- Usar `StreamingResponse` do FastAPI
- Criar gerador que emite eventos conforme workflow progride
- Emitir eventos para cada etapa: parsing, geração, verificação

**Como validar:**
- [ ] Workflow emite eventos de streaming
- [ ] Eventos são formatados corretamente
- [ ] Streaming funciona para perguntas únicas
- [ ] Streaming funciona para questionários

**Tempo estimado:** 1 dia

---

### 2. Criar Endpoint de Streaming na API
**O que fazer:**
- Criar endpoint POST `/rfps/stream` que retorna streaming
- Usar `StreamingResponse` do FastAPI
- Formato: Server-Sent Events (SSE) ou JSON streaming
- Incluir eventos de progresso e resultados parciais

**Como validar:**
- [ ] Endpoint criado e funcionando
- [ ] Streaming funciona corretamente
- [ ] Cliente pode consumir streaming
- [ ] Erros são tratados adequadamente

**Tempo estimado:** 0.5 dia

---

### 3. Integrar com Frontend
**O que fazer:**
- Atualizar frontend para consumir streaming
- Mostrar progresso em tempo real
- Exibir respostas conforme são geradas
- Tratar reconexão em caso de perda de conexão

**Como validar:**
- [ ] Frontend consome streaming corretamente
- [ ] Progresso é exibido em tempo real
- [ ] Respostas aparecem conforme geradas
- [ ] Reconexão funciona

**Tempo estimado:** 0.5 dia

---

## Checklist de Validação

- [ ] Workflow suporta streaming
- [ ] Endpoint de streaming criado
- [ ] Frontend integrado com streaming
- [ ] Streaming funciona para todos os tipos de input
- [ ] Erros são tratados adequadamente
- [ ] Performance é aceitável

---

## Exemplo de Uso

```python
# Backend - Endpoint de streaming
@app.post("/rfps/stream")
async def stream_rfp_processing(input_text: str):
    async def generate():
        async for event in workflow.stream(input_text):
            yield f"data: {json.dumps(event)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

```javascript
// Frontend - Consumir streaming
const eventSource = new EventSource('/rfps/stream?input=' + inputText);
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateUI(data);
};
```

---

## Próximo Passo
Após completar esta tarefa, seguir para: **Tarefa 6.4: Runbooks para Operações**


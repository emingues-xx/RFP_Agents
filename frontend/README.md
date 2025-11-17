# RFP Agents Frontend

Interface web básica para o sistema de agentes de preenchimento de RFPs.

## Instalação

```bash
npm install
```

## Desenvolvimento

```bash
npm run dev
```

A aplicação estará disponível em `http://localhost:3000`.

## Build

```bash
npm run build
```

## Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto frontend:

```
VITE_API_URL=http://localhost:8000
```

## Funcionalidades

- **Listagem de RFPs**: Visualizar todos os RFPs processados
- **Detalhes do RFP**: Ver respostas geradas para cada pergunta
- **Aprovações**: Revisar e aprovar/rejeitar respostas
- **Exploração**: Processar novos textos ou arquivos


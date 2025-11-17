# Frontend - RFP Agents

Frontend React/TypeScript do sistema de agentes para preenchimento de RFPs.

## Estrutura

```
frontend/
├── src/
│   ├── components/   # Componentes React
│   ├── services/      # Serviços de API
│   ├── App.tsx        # Componente principal
│   └── main.tsx       # Entry point
├── package.json       # Dependências Node.js
├── vite.config.ts     # Configuração Vite
└── tsconfig.json      # Configuração TypeScript
```

## Instalação

```bash
cd frontend
npm install
```

## Executar

### Desenvolvimento

```bash
npm run dev
```

Acesse: http://localhost:5173

### Build

```bash
npm run build
```

### Preview

```bash
npm run preview
```

## Componentes

- **RFPList**: Lista de RFPs processados
- **RFPDetail**: Detalhes de um RFP específico
- **ApprovalList**: Lista de aprovações pendentes
- **ApprovalInterface**: Interface de aprovação HITL
- **Exploration**: Interface para explorar o sistema

## API

O frontend se comunica com o backend através de:

- Base URL: `http://localhost:8000` (configurável via `VITE_API_URL`)

Endpoints utilizados:
- `GET /rfps/`: Listar RFPs
- `GET /rfps/{id}`: Detalhes do RFP
- `GET /approvals/`: Listar aprovações
- `GET /approvals/{id}`: Detalhes da aprovação
- `POST /approvals/{id}/approve`: Aprovar
- `POST /approvals/{id}/reject`: Rejeitar
- `POST /approvals/{id}/edit`: Editar
- `POST /workflow/process`: Processar texto
- `POST /workflow/process-file`: Processar arquivo

## Variáveis de Ambiente

Crie um arquivo `.env` na pasta `frontend/`:

```env
VITE_API_URL=http://localhost:8000
```

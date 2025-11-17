# Tarefa 5.2: Interface Web Básica

## Objetivo
Implementar interface web básica para explorar funcionalidades do sistema, incluindo listagem de RFPs, detalhes, aprovação e exploração.

## Prioridade
Alta

## Estimativa
5 dias

## Responsável
Frontend/Fullstack

---

## Instruções de Implementação

### 1. Escolher Framework Frontend

#### Opção recomendada: React com Vite
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

### 2. Criar Estrutura Básica do Projeto Frontend

#### Estrutura sugerida:
```
frontend/
├── src/
│   ├── components/
│   │   ├── RFPList.tsx
│   │   ├── RFPDetail.tsx
│   │   ├── ApprovalInterface.tsx
│   │   └── Exploration.tsx
│   ├── services/
│   │   └── api.ts
│   ├── App.tsx
│   └── main.tsx
├── package.json
└── vite.config.ts
```

### 3. Implementar Página de Listagem de RFPs

#### Criar `frontend/src/components/RFPList.tsx`:
```typescript
import React, { useEffect, useState } from 'react';
import { api } from '../services/api';

interface RFP {
  id: string;
  workflow_id: string;
  status: string;
  created_at: string;
  input_type: string;
}

export const RFPList: React.FC = () => {
  const [rfps, setRfps] = useState<RFP[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    fetchRFPs();
  }, [filter]);

  const fetchRFPs = async () => {
    try {
      setLoading(true);
      const data = await api.getRFPs(filter);
      setRfps(data);
    } catch (error) {
      console.error('Erro ao buscar RFPs:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rfp-list">
      <h1>RFPs Processados</h1>
      
      <div className="filters">
        <button onClick={() => setFilter('all')}>Todos</button>
        <button onClick={() => setFilter('pending')}>Pendentes</button>
        <button onClick={() => setFilter('approved')}>Aprovados</button>
        <button onClick={() => setFilter('rejected')}>Rejeitados</button>
      </div>

      {loading ? (
        <p>Carregando...</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Workflow ID</th>
              <th>Status</th>
              <th>Tipo</th>
              <th>Data</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {rfps.map((rfp) => (
              <tr key={rfp.id}>
                <td>{rfp.id}</td>
                <td>{rfp.workflow_id}</td>
                <td>{rfp.status}</td>
                <td>{rfp.input_type}</td>
                <td>{new Date(rfp.created_at).toLocaleDateString()}</td>
                <td>
                  <a href={`/rfp/${rfp.id}`}>Ver Detalhes</a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
```

### 4. Implementar Página de Detalhes do RFP

#### Criar `frontend/src/components/RFPDetail.tsx`:
```typescript
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../services/api';

interface Response {
  qid: string;
  question_text: string;
  response_text: string;
  confidence_score: number;
  citations: string[];
  needs_review: boolean;
}

export const RFPDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [responses, setResponses] = useState<Response[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      fetchRFPDetail(id);
    }
  }, [id]);

  const fetchRFPDetail = async (rfpId: string) => {
    try {
      setLoading(true);
      const data = await api.getRFPDetail(rfpId);
      setResponses(data.responses || []);
    } catch (error) {
      console.error('Erro ao buscar detalhes:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <p>Carregando...</p>;
  }

  return (
    <div className="rfp-detail">
      <h1>Detalhes do RFP</h1>
      
      {responses.map((response) => (
        <div key={response.qid} className="response-card">
          <h3>{response.question_text}</h3>
          <p className="response">{response.response_text}</p>
          
          <div className="metadata">
            <span className="confidence">
              Confiança: {(response.confidence_score * 100).toFixed(1)}%
            </span>
            {response.needs_review && (
              <span className="review-flag">⚠️ Requer Revisão</span>
            )}
          </div>
          
          {response.citations.length > 0 && (
            <div className="citations">
              <h4>Fontes:</h4>
              <ul>
                {response.citations.map((citation, idx) => (
                  <li key={idx}>{citation}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
```

### 5. Implementar Interface de Aprovação

#### Criar `frontend/src/components/ApprovalInterface.tsx`:
```typescript
import React, { useEffect, useState } from 'react';
import { api } from '../services/api';

interface ApprovalResponse {
  id: string;
  qid: string;
  response_text: string;
  confidence_score: number;
}

interface Approval {
  id: string;
  workflow_id: string;
  responses: ApprovalResponse[];
  status: string;
}

export const ApprovalInterface: React.FC<{ approvalId: string }> = ({ approvalId }) => {
  const [approval, setApproval] = useState<Approval | null>(null);
  const [editing, setEditing] = useState<{ [key: string]: string }>({});
  const [comments, setComments] = useState('');

  useEffect(() => {
    fetchApproval();
  }, [approvalId]);

  const fetchApproval = async () => {
    try {
      const data = await api.getApproval(approvalId);
      setApproval(data);
      // Inicializar editing com respostas atuais
      const editingMap: { [key: string]: string } = {};
      data.responses.forEach((r: ApprovalResponse) => {
        editingMap[r.qid] = r.response_text;
      });
      setEditing(editingMap);
    } catch (error) {
      console.error('Erro ao buscar aprovação:', error);
    }
  };

  const handleEdit = (qid: string, value: string) => {
    setEditing({ ...editing, [qid]: value });
  };

  const handleApprove = async () => {
    try {
      await api.approve(approvalId, { comments });
      alert('Aprovado com sucesso!');
      window.location.reload();
    } catch (error) {
      console.error('Erro ao aprovar:', error);
      alert('Erro ao aprovar');
    }
  };

  const handleReject = async () => {
    try {
      await api.reject(approvalId, { comments });
      alert('Rejeitado');
      window.location.reload();
    } catch (error) {
      console.error('Erro ao rejeitar:', error);
      alert('Erro ao rejeitar');
    }
  };

  const handleSaveEdit = async () => {
    try {
      const editedResponses = approval!.responses.map(r => ({
        ...r,
        response_text: editing[r.qid] || r.response_text
      }));
      await api.edit(approvalId, { responses: editedResponses, comments });
      alert('Edições salvas!');
    } catch (error) {
      console.error('Erro ao salvar edições:', error);
      alert('Erro ao salvar edições');
    }
  };

  if (!approval) {
    return <p>Carregando...</p>;
  }

  return (
    <div className="approval-interface">
      <h1>Aprovação: {approval.workflow_id}</h1>
      
      {approval.responses.map((response) => (
        <div key={response.qid} className="approval-item">
          <h3>Pergunta {response.qid}</h3>
          <textarea
            value={editing[response.qid] || response.response_text}
            onChange={(e) => handleEdit(response.qid, e.target.value)}
            rows={5}
          />
          <div className="confidence">
            Confiança: {(response.confidence_score * 100).toFixed(1)}%
          </div>
        </div>
      ))}
      
      <div className="comments-section">
        <label>Comentários:</label>
        <textarea
          value={comments}
          onChange={(e) => setComments(e.target.value)}
          rows={3}
        />
      </div>
      
      <div className="actions">
        <button onClick={handleSaveEdit}>Salvar Edições</button>
        <button onClick={handleApprove} className="approve">Aprovar</button>
        <button onClick={handleReject} className="reject">Rejeitar</button>
      </div>
    </div>
  );
};
```

### 6. Implementar Página de Exploração

#### Criar `frontend/src/components/Exploration.tsx`:
```typescript
import React, { useState } from 'react';
import { api } from '../services/api';

export const Exploration: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [workflowStatus, setWorkflowStatus] = useState<string>('');
  const [logs, setLogs] = useState<string[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setWorkflowStatus('Processando...');
      setLogs(['Iniciando workflow...']);
      
      let result;
      if (file) {
        result = await api.processFile(file);
      } else {
        result = await api.processText(inputText);
      }
      
      setWorkflowStatus('Concluído');
      setLogs([...logs, 'Workflow concluído', JSON.stringify(result, null, 2)]);
    } catch (error) {
      setWorkflowStatus('Erro');
      setLogs([...logs, `Erro: ${error}`]);
    }
  };

  return (
    <div className="exploration">
      <h1>Explorar Funcionalidades</h1>
      
      <form onSubmit={handleSubmit}>
        <div>
          <label>Texto de Entrada:</label>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            rows={5}
            disabled={!!file}
          />
        </div>
        
        <div>
          <label>Ou fazer upload de arquivo:</label>
          <input
            type="file"
            accept=".pdf,.docx,.xlsx,.csv"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
        </div>
        
        <button type="submit">Processar</button>
      </form>
      
      {workflowStatus && (
        <div className="status">
          <h2>Status: {workflowStatus}</h2>
          <div className="logs">
            <h3>Logs:</h3>
            <pre>{logs.join('\n')}</pre>
          </div>
        </div>
      )}
    </div>
  );
};
```

### 7. Criar Serviço de API

#### Criar `frontend/src/services/api.ts`:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
  async getRFPs(filter: string = 'all') {
    const response = await fetch(`${API_BASE_URL}/rfps?filter=${filter}`);
    return response.json();
  },
  
  async getRFPDetail(id: string) {
    const response = await fetch(`${API_BASE_URL}/rfps/${id}`);
    return response.json();
  },
  
  async getApproval(approvalId: string) {
    const response = await fetch(`${API_BASE_URL}/approvals/${approvalId}`);
    return response.json();
  },
  
  async approve(approvalId: string, data: { comments?: string }) {
    const response = await fetch(`${API_BASE_URL}/approvals/${approvalId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  },
  
  async reject(approvalId: string, data: { comments?: string }) {
    const response = await fetch(`${API_BASE_URL}/approvals/${approvalId}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  },
  
  async edit(approvalId: string, data: { responses: any[], comments?: string }) {
    const response = await fetch(`${API_BASE_URL}/approvals/${approvalId}/edit`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  },
  
  async processText(text: string) {
    const response = await fetch(`${API_BASE_URL}/workflow/process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input_text: text })
    });
    return response.json();
  },
  
  async processFile(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${API_BASE_URL}/workflow/process-file`, {
      method: 'POST',
      body: formData
    });
    return response.json();
  }
};
```

### 8. Integrar com API Backend

#### Adicionar rotas no FastAPI:
```python
@router.post("/workflow/process")
async def process_text(request: ProcessRequest):
    """Processar texto."""
    workflow = RFPWorkflow()
    result = workflow.run(request.input_text, session_id=request.session_id)
    return result

@router.post("/workflow/process-file")
async def process_file(file: UploadFile):
    """Processar arquivo."""
    # Salvar arquivo temporariamente
    # Processar com workflow
    pass
```

### 9. Adicionar Tratamento de Erros

#### Criar componente de erro:
```typescript
export const ErrorBoundary: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Implementar error boundary
  return <>{children}</>;
};
```

### 10. Testar Interface End-to-End

#### Criar testes:
```typescript
// frontend/src/__tests__/App.test.tsx
import { render, screen } from '@testing-library/react';
import { App } from '../App';

test('renders RFP list', () => {
  render(<App />);
  const linkElement = screen.getByText(/RFPs Processados/i);
  expect(linkElement).toBeInTheDocument();
});
```

---

## Checklist de Validação

- [ ] Framework frontend escolhido e configurado
- [ ] Estrutura básica do projeto criada
- [ ] Página de listagem de RFPs implementada
- [ ] Página de detalhes do RFP implementada
- [ ] Interface de aprovação implementada
- [ ] Página de exploração implementada
- [ ] Integração com API backend funcionando
- [ ] Tratamento de erros adicionado
- [ ] Testes end-to-end criados
- [ ] Documentação de uso criada

---

## Comandos de Teste

```bash
# Instalar dependências
cd frontend && npm install

# Executar em desenvolvimento
npm run dev

# Testar
npm test

# Build para produção
npm run build
```


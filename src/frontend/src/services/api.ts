const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3022';

export interface RFP {
  id: string;
  workflow_id: string;
  status: string;
  created_at: string;
  input_type?: string;
}

export interface Response {
  qid: string;
  question_text?: string;
  response_text: string;
  confidence_score: number;
  citations?: string[];
  needs_review?: boolean;
}

export interface ApprovalResponse {
  id?: string;
  qid: string;
  response_text: string;
  confidence_score: number;
}

export interface Approval {
  id: string;
  workflow_id: string;
  responses: ApprovalResponse[];
  status: string;
}

export const api = {
  async getRFPs(filter: string = 'all'): Promise<RFP[]> {
    const response = await fetch(`${API_BASE_URL}/rfps?filter=${filter}`);
    if (!response.ok) {
      throw new Error(`Erro ao buscar RFPs: ${response.statusText}`);
    }
    return response.json();
  },
  
  async getRFPDetail(id: string) {
    const response = await fetch(`${API_BASE_URL}/rfps/${id}`);
    if (!response.ok) {
      throw new Error(`Erro ao buscar detalhes: ${response.statusText}`);
    }
    return response.json();
  },
  
  async getApproval(approvalId: string): Promise<Approval> {
    const response = await fetch(`${API_BASE_URL}/approvals/${approvalId}`);
    if (!response.ok) {
      throw new Error(`Erro ao buscar aprovação: ${response.statusText}`);
    }
    return response.json();
  },
  
  async approve(approvalId: string, data: { comments?: string; approved_by?: string }) {
    const response = await fetch(`${API_BASE_URL}/approvals/${approvalId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro ao aprovar');
    }
    return response.json();
  },
  
  async reject(approvalId: string, data: { comments?: string }) {
    const response = await fetch(`${API_BASE_URL}/approvals/${approvalId}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro ao rejeitar');
    }
    return response.json();
  },
  
  async edit(approvalId: string, data: { responses: any[], comments?: string }) {
    const response = await fetch(`${API_BASE_URL}/approvals/${approvalId}/edit`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro ao editar');
    }
    return response.json();
  },
  
  async processText(text: string) {
    const response = await fetch(`${API_BASE_URL}/workflow/process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input_text: text })
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro ao processar texto');
    }
    return response.json();
  },
  
  async processFile(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${API_BASE_URL}/workflow/process-file`, {
      method: 'POST',
      body: formData
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro ao processar arquivo');
    }
    return response.json();
  }
};


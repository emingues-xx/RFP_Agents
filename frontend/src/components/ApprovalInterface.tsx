import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { api, Approval, ApprovalResponse } from '../services/api';

export const ApprovalInterface: React.FC = () => {
  const { approvalId } = useParams<{ approvalId: string }>();
  const navigate = useNavigate();
  const [approval, setApproval] = useState<Approval | null>(null);
  const [editing, setEditing] = useState<{ [key: string]: string }>({});
  const [comments, setComments] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (approvalId) {
      fetchApproval();
    }
  }, [approvalId]);

  const fetchApproval = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getApproval(approvalId!);
      setApproval(data);
      // Inicializar editing com respostas atuais
      const editingMap: { [key: string]: string } = {};
      data.responses.forEach((r: ApprovalResponse) => {
        editingMap[r.qid] = r.response_text;
      });
      setEditing(editingMap);
    } catch (err) {
      console.error('Erro ao buscar aprovação:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (qid: string, value: string) => {
    setEditing({ ...editing, [qid]: value });
  };

  const handleApprove = async () => {
    try {
      setSaving(true);
      await api.approve(approvalId!, { comments, approved_by: 'user' });
      alert('Aprovado com sucesso!');
      navigate('/approvals');
    } catch (err) {
      console.error('Erro ao aprovar:', err);
      alert(err instanceof Error ? err.message : 'Erro ao aprovar');
    } finally {
      setSaving(false);
    }
  };

  const handleReject = async () => {
    try {
      setSaving(true);
      await api.reject(approvalId!, { comments });
      alert('Rejeitado');
      navigate('/approvals');
    } catch (err) {
      console.error('Erro ao rejeitar:', err);
      alert(err instanceof Error ? err.message : 'Erro ao rejeitar');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveEdit = async () => {
    try {
      setSaving(true);
      const editedResponses = approval!.responses.map(r => ({
        ...r,
        response_text: editing[r.qid] || r.response_text
      }));
      await api.edit(approvalId!, { responses: editedResponses, comments });
      alert('Edições salvas!');
      fetchApproval(); // Recarregar
    } catch (err) {
      console.error('Erro ao salvar edições:', err);
      alert(err instanceof Error ? err.message : 'Erro ao salvar edições');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="container"><div className="loading">Carregando...</div></div>;
  }

  if (error || !approval) {
    return (
      <div className="container">
        <div className="error">{error || 'Aprovação não encontrada'}</div>
        <Link to="/approvals">Voltar</Link>
      </div>
    );
  }

  return (
    <div className="container">
      <Link to="/approvals">← Voltar</Link>
      <h1>Aprovação: {approval.workflow_id}</h1>
      <p>Status: <strong>{approval.status}</strong></p>
      
      {approval.responses.map((response) => (
        <div key={response.qid} className="approval-item">
          <h3>Pergunta {response.qid}</h3>
          <textarea
            value={editing[response.qid] || response.response_text}
            onChange={(e) => handleEdit(response.qid, e.target.value)}
            rows={5}
            disabled={approval.status !== 'pending'}
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
          disabled={approval.status !== 'pending' || saving}
        />
      </div>
      
      {approval.status === 'pending' && (
        <div className="actions">
          <button onClick={handleSaveEdit} disabled={saving}>
            {saving ? 'Salvando...' : 'Salvar Edições'}
          </button>
          <button onClick={handleApprove} className="approve" disabled={saving}>
            {saving ? 'Aprovando...' : 'Aprovar'}
          </button>
          <button onClick={handleReject} className="reject" disabled={saving}>
            {saving ? 'Rejeitando...' : 'Rejeitar'}
          </button>
        </div>
      )}
    </div>
  );
};


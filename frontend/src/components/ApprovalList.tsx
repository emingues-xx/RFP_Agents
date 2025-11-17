import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, Approval } from '../services/api';

export const ApprovalList: React.FC = () => {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchApprovals();
  }, []);

  const fetchApprovals = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getRFPs('pending');
      // Converter para formato Approval
      const approvalList: Approval[] = await Promise.all(
        data.map(async (rfp) => {
          try {
            const approval = await api.getApproval(rfp.id);
            return approval;
          } catch {
            return null;
          }
        })
      );
      setApprovals(approvalList.filter(a => a !== null) as Approval[]);
    } catch (err) {
      console.error('Erro ao buscar aprovações:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Aprovações Pendentes</h1>
      
      {error && <div className="error">{error}</div>}

      {loading ? (
        <div className="loading">Carregando...</div>
      ) : approvals.length === 0 ? (
        <p>Nenhuma aprovação pendente.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Workflow ID</th>
              <th>Status</th>
              <th>Respostas</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {approvals.map((approval) => (
              <tr key={approval.id}>
                <td>{approval.id.substring(0, 8)}...</td>
                <td>{approval.workflow_id}</td>
                <td>{approval.status}</td>
                <td>{approval.responses.length}</td>
                <td>
                  <Link to={`/approvals/${approval.id}`}>Revisar</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};


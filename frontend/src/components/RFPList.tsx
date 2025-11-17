import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, RFP } from '../services/api';

export const RFPList: React.FC = () => {
  const [rfps, setRfps] = useState<RFP[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRFPs();
  }, [filter]);

  const fetchRFPs = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getRFPs(filter);
      setRfps(data);
    } catch (err) {
      console.error('Erro ao buscar RFPs:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>RFPs Processados</h1>
      
      <div className="filters">
        <button 
          onClick={() => setFilter('all')}
          style={{ backgroundColor: filter === 'all' ? '#0056b3' : '#007bff' }}
        >
          Todos
        </button>
        <button 
          onClick={() => setFilter('pending')}
          style={{ backgroundColor: filter === 'pending' ? '#0056b3' : '#007bff' }}
        >
          Pendentes
        </button>
        <button 
          onClick={() => setFilter('approved')}
          style={{ backgroundColor: filter === 'approved' ? '#0056b3' : '#007bff' }}
        >
          Aprovados
        </button>
        <button 
          onClick={() => setFilter('rejected')}
          style={{ backgroundColor: filter === 'rejected' ? '#0056b3' : '#007bff' }}
        >
          Rejeitados
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <div className="loading">Carregando...</div>
      ) : rfps.length === 0 ? (
        <p>Nenhum RFP encontrado.</p>
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
                <td>{rfp.id.substring(0, 8)}...</td>
                <td>{rfp.workflow_id}</td>
                <td>
                  <span style={{
                    color: rfp.status === 'approved' ? '#28a745' : 
                           rfp.status === 'rejected' ? '#dc3545' : 
                           rfp.status === 'pending' ? '#ffc107' : '#6c757d'
                  }}>
                    {rfp.status}
                  </span>
                </td>
                <td>{rfp.input_type || 'N/A'}</td>
                <td>{new Date(rfp.created_at).toLocaleDateString('pt-BR')}</td>
                <td>
                  <Link to={`/rfp/${rfp.workflow_id}`}>Ver Detalhes</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};


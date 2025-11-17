import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api, Response } from '../services/api';

export const RFPDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [responses, setResponses] = useState<Response[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchRFPDetail(id);
    }
  }, [id]);

  const fetchRFPDetail = async (rfpId: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getRFPDetail(rfpId);
      setResponses(data.responses || []);
    } catch (err) {
      console.error('Erro ao buscar detalhes:', err);
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="container"><div className="loading">Carregando...</div></div>;
  }

  if (error) {
    return (
      <div className="container">
        <div className="error">{error}</div>
        <Link to="/">Voltar para lista</Link>
      </div>
    );
  }

  return (
    <div className="container">
      <Link to="/">← Voltar para lista</Link>
      <h1>Detalhes do RFP</h1>
      
      {responses.length === 0 ? (
        <p>Nenhuma resposta encontrada.</p>
      ) : (
        responses.map((response) => (
          <div key={response.qid} className="response-card">
            <h3>Pergunta {response.qid}</h3>
            {response.question_text && (
              <p style={{ marginBottom: '10px', fontStyle: 'italic', color: '#666' }}>
                {response.question_text}
              </p>
            )}
            <p className="response">{response.response_text}</p>
            
            <div className="metadata">
              <span className="confidence">
                Confiança: {(response.confidence_score * 100).toFixed(1)}%
              </span>
              {response.needs_review && (
                <span className="review-flag">⚠️ Requer Revisão</span>
              )}
            </div>
            
            {response.citations && response.citations.length > 0 && (
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
        ))
      )}
    </div>
  );
};


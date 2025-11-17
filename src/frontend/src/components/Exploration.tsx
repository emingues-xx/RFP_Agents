import React, { useState } from 'react';
import { api } from '../services/api';

export const Exploration: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [workflowStatus, setWorkflowStatus] = useState<string>('');
  const [logs, setLogs] = useState<string[]>([]);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputText && !file) {
      alert('Por favor, insira um texto ou selecione um arquivo');
      return;
    }
    
    try {
      setProcessing(true);
      setError(null);
      setWorkflowStatus('Processando...');
      setLogs(['Iniciando workflow...']);
      
      let result;
      if (file) {
        setLogs(prev => [...prev, `Processando arquivo: ${file.name}`]);
        result = await api.processFile(file);
      } else {
        setLogs(prev => [...prev, 'Processando texto...']);
        result = await api.processText(inputText);
      }
      
      setWorkflowStatus('Concluído');
      setLogs(prev => [
        ...prev, 
        'Workflow concluído',
        `Workflow ID: ${result.workflow_id}`,
        `Status: ${result.status}`,
        `Requer aprovação: ${result.requires_approval ? 'Sim' : 'Não'}`,
        result.approval_id ? `Aprovação ID: ${result.approval_id}` : '',
        `Respostas geradas: ${result.responses?.length || 0}`,
        JSON.stringify(result, null, 2)
      ]);
    } catch (err) {
      setWorkflowStatus('Erro');
      const errorMsg = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMsg);
      setLogs(prev => [...prev, `Erro: ${errorMsg}`]);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="container">
      <h1>Explorar Funcionalidades</h1>
      
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>
            Texto de Entrada:
          </label>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            rows={5}
            disabled={!!file || processing}
            placeholder="Digite uma pergunta ou texto para processar..."
          />
        </div>
        
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>
            Ou fazer upload de arquivo:
          </label>
          <input
            type="file"
            accept=".pdf,.docx,.xlsx,.csv"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            disabled={processing}
          />
          {file && (
            <p style={{ marginTop: '8px', color: '#666' }}>
              Arquivo selecionado: {file.name}
            </p>
          )}
        </div>
        
        <button type="submit" disabled={processing || (!inputText && !file)}>
          {processing ? 'Processando...' : 'Processar'}
        </button>
      </form>
      
      {error && <div className="error">{error}</div>}
      
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


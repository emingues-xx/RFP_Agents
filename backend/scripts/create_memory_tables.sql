-- Script para criar índices na tabela chat_history
-- A tabela chat_history é criada automaticamente pelo PostgresChatMessageHistory
-- Este script apenas cria índices para melhorar performance

-- Índice para busca por session_id (mais comum)
CREATE INDEX IF NOT EXISTS idx_chat_history_session_id 
ON chat_history(session_id);

-- Índice para busca por data (para limpeza)
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at 
ON chat_history(created_at);

-- Índice composto para queries comuns (session_id + created_at)
CREATE INDEX IF NOT EXISTS idx_chat_history_session_created 
ON chat_history(session_id, created_at);

-- Comentários
COMMENT ON TABLE chat_history IS 'Tabela de histórico de conversas para memória persistente';
COMMENT ON INDEX idx_chat_history_session_id IS 'Índice para busca rápida por sessão';
COMMENT ON INDEX idx_chat_history_created_at IS 'Índice para limpeza de dados antigos';
COMMENT ON INDEX idx_chat_history_session_created IS 'Índice composto para queries por sessão e data';


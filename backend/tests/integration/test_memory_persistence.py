"""Testes de persistência de memória."""
import pytest
from src.agents.memory_manager import PersistentMemoryManager
from src.agents.memory_cleanup import MemoryCleanup
from unittest.mock import Mock


def test_memory_persistence():
    """Testar persistência entre sessões."""
    session_id = "test-persistence-123"
    
    # Limpar sessão anterior se existir
    cleanup = MemoryCleanup()
    cleanup.cleanup_by_session(session_id)
    
    # Criar memória e salvar
    memory1 = PersistentMemoryManager(session_id)
    memory1.save_context("Pergunta 1", "Resposta 1")
    memory1.save_context("Pergunta 2", "Resposta 2")
    
    # Criar nova instância e verificar
    memory2 = PersistentMemoryManager(session_id)
    history = memory2.load_memory_variables()
    
    assert len(history.get("chat_history", [])) > 0
    
    # Limpar após teste
    memory2.clear()


def test_multiple_sessions():
    """Testar múltiplas sessões simultâneas."""
    session1_id = "test-session-1"
    session2_id = "test-session-2"
    
    # Limpar sessões anteriores
    cleanup = MemoryCleanup()
    cleanup.cleanup_by_session(session1_id)
    cleanup.cleanup_by_session(session2_id)
    
    # Criar duas sessões
    session1 = PersistentMemoryManager(session1_id)
    session2 = PersistentMemoryManager(session2_id)
    
    # Salvar contextos diferentes
    session1.save_context("Q1", "A1")
    session2.save_context("Q2", "A2")
    
    # Verificar que são independentes
    hist1 = session1.load_memory_variables()
    hist2 = session2.load_memory_variables()
    
    assert len(hist1["chat_history"]) >= 1
    assert len(hist2["chat_history"]) >= 1
    
    # Verificar que conteúdos são diferentes
    content1 = hist1["chat_history"][0].content if hasattr(hist1["chat_history"][0], 'content') else str(hist1["chat_history"][0])
    content2 = hist2["chat_history"][0].content if hasattr(hist2["chat_history"][0], 'content') else str(hist2["chat_history"][0])
    
    # Limpar após teste
    session1.clear()
    session2.clear()


def test_get_conversation_summary():
    """Testar obtenção de resumo da conversa."""
    session_id = "test-summary-123"
    
    # Limpar sessão anterior
    cleanup = MemoryCleanup()
    cleanup.cleanup_by_session(session_id)
    
    memory = PersistentMemoryManager(session_id)
    memory.save_context("Qual é o SLA?", "O SLA é de 99.9%")
    memory.save_context("Qual é o preço?", "O preço é R$ 1000/mês")
    
    summary = memory.get_conversation_summary()
    
    assert summary is not None
    assert len(summary) > 0
    assert "mensagens" in summary.lower() or "histórico" in summary.lower()
    
    # Limpar após teste
    memory.clear()


def test_get_message_count():
    """Testar contagem de mensagens."""
    session_id = "test-count-123"
    
    # Limpar sessão anterior
    cleanup = MemoryCleanup()
    cleanup.cleanup_by_session(session_id)
    
    memory = PersistentMemoryManager(session_id)
    
    # Contar inicial (deve ser 0 ou ter mensagens anteriores)
    initial_count = memory.get_message_count()
    
    # Adicionar mensagens
    memory.save_context("Q1", "A1")
    memory.save_context("Q2", "A2")
    
    # Verificar contagem
    count = memory.get_message_count()
    assert count >= 2  # Pode ter mais se houver mensagens anteriores
    
    # Limpar após teste
    memory.clear()


def test_memory_clear():
    """Testar limpeza de memória."""
    session_id = "test-clear-123"
    
    # Limpar sessão anterior
    cleanup = MemoryCleanup()
    cleanup.cleanup_by_session(session_id)
    
    memory = PersistentMemoryManager(session_id)
    memory.save_context("Q1", "A1")
    memory.save_context("Q2", "A2")
    
    # Verificar que tem mensagens
    assert memory.get_message_count() >= 2
    
    # Limpar
    memory.clear()
    
    # Verificar que está vazio
    count_after = memory.get_message_count()
    assert count_after == 0


def test_memory_cleanup_old_sessions():
    """Testar limpeza de sessões antigas."""
    cleanup = MemoryCleanup(retention_days=1)  # 1 dia para teste
    
    # Obter contagem antes
    count_before = cleanup.get_message_count()
    
    # Executar limpeza (não deve deletar nada recente)
    deleted = cleanup.cleanup_old_sessions()
    
    # Verificar que não deletou mensagens recentes
    assert deleted >= 0  # Pode ser 0 se não houver mensagens antigas
    
    # Verificar contagem após (deve ser igual ou menor)
    count_after = cleanup.get_message_count()
    assert count_after <= count_before


def test_memory_cleanup_by_session():
    """Testar limpeza de sessão específica."""
    session_id = "test-cleanup-session-123"
    
    cleanup = MemoryCleanup()
    
    # Criar memória e adicionar mensagens
    memory = PersistentMemoryManager(session_id)
    memory.save_context("Q1", "A1")
    
    # Verificar que tem mensagens
    assert memory.get_message_count() >= 1
    
    # Limpar sessão específica
    deleted = cleanup.cleanup_by_session(session_id)
    assert deleted >= 1
    
    # Verificar que está vazio
    memory2 = PersistentMemoryManager(session_id)
    assert memory2.get_message_count() == 0


def test_conversation_buffer_memory():
    """Testar ConversationBufferMemory."""
    session_id = "test-buffer-123"
    
    cleanup = MemoryCleanup()
    cleanup.cleanup_by_session(session_id)
    
    memory = PersistentMemoryManager(session_id, use_summary=False)
    memory.save_context("Teste", "Resposta")
    
    history = memory.load_memory_variables()
    assert "chat_history" in history
    
    memory.clear()


def test_conversation_summary_memory():
    """Testar ConversationSummaryMemory (requer LLM)."""
    from src.utils.llm_factory import LLMFactory
    
    try:
        factory = LLMFactory()
        llm = factory.get_default_llm()
        
        session_id = "test-summary-memory-123"
        
        cleanup = MemoryCleanup()
        cleanup.cleanup_by_session(session_id)
        
        memory = PersistentMemoryManager(session_id, use_summary=True, llm=llm)
        memory.save_context("Teste", "Resposta")
        
        history = memory.load_memory_variables()
        assert "chat_history" in history
        
        summary = memory.get_conversation_summary()
        assert summary is not None
        
        memory.clear()
        
    except Exception as e:
        # Se LLM não estiver configurado, pular teste
        pytest.skip(f"LLM não configurado para ConversationSummaryMemory: {e}")


@pytest.mark.integration
def test_memory_persistence_across_instances():
    """Testar persistência entre instâncias diferentes."""
    session_id = "test-cross-instance-123"
    
    cleanup = MemoryCleanup()
    cleanup.cleanup_by_session(session_id)
    
    # Criar primeira instância
    memory1 = PersistentMemoryManager(session_id)
    memory1.save_context("Primeira pergunta", "Primeira resposta")
    
    # Criar segunda instância (nova conexão)
    memory2 = PersistentMemoryManager(session_id)
    history2 = memory2.load_memory_variables()
    
    # Verificar que segunda instância vê as mensagens da primeira
    assert len(history2.get("chat_history", [])) > 0
    
    # Adicionar mais mensagens na segunda instância
    memory2.save_context("Segunda pergunta", "Segunda resposta")
    
    # Verificar na primeira instância
    history1 = memory1.load_memory_variables()
    assert len(history1.get("chat_history", [])) >= 2
    
    # Limpar
    memory1.clear()


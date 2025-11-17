"""Estado compartilhado do workflow."""
from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage


class WorkflowState(TypedDict, total=False):
    """Estado do workflow."""
    # Input
    input_text: str
    input_type: Optional[str]  # "single_question" ou "questionnaire"
    file_path: Optional[str]
    
    # Contexto
    context: Dict[str, Any]  # cliente, produto, prazos
    
    # Mensagens
    messages: List[BaseMessage]
    
    # Resultados dos agentes
    parsed_questions: Optional[List[Dict[str, Any]]]
    generated_responses: Optional[List[Dict[str, Any]]]
    verified_responses: Optional[List[Dict[str, Any]]]
    
    # Metadados
    session_id: str
    workflow_id: str
    current_step: str
    errors: List[str]
    
    # Aprovação
    requires_approval: bool
    approval_status: Optional[str]  # "pending", "approved", "rejected"
    
    # Plano de coordenação
    coordination_plan: Optional[Dict[str, Any]]


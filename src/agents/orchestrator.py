"""Agente Orquestrador - Coordena todo o fluxo do sistema."""
from typing import Dict, Any, Literal, Optional, List
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class InputType(BaseModel):
    """Tipo de input identificado."""
    type: Literal["single_question", "questionnaire", "unknown"]
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Context(BaseModel):
    """Contexto coletado para processamento."""
    client: Optional[str] = None
    product: Optional[str] = None
    deadlines: Optional[str] = None
    additional_info: Dict[str, Any] = Field(default_factory=dict)


class OrchestratorAgent:
    """Agente Orquestrador principal."""
    
    def __init__(
        self,
        llm: BaseChatModel,
        session_id: str,
        memory_manager: Optional[Any] = None,
    ):
        """Inicializar Agente Orquestrador."""
        self.llm = llm
        self.session_id = session_id
        self.memory_manager = memory_manager
        self._setup_system_prompt()
    
    def _setup_system_prompt(self) -> None:
        """Configurar prompt do sistema."""
        self.system_prompt = """Você é um Agente Orquestrador responsável por:
1. Identificar o tipo de input recebido (pergunta única ou questionário)
2. Coletar contexto adicional necessário (cliente, produto, prazos)
3. Coordenar agentes especialistas para processar o input
4. Gerenciar o fluxo de trabalho e estado

Sempre responda em formato JSON estruturado."""
    
    def identify_input_type(self, input_text: str) -> InputType:
        """Identificar tipo de input (pergunta única vs. questionário)."""
        logger.info("Iniciando identificação de tipo de input")
        logger.debug(f"Input recebido: {input_text[:100]}...")
        
        prompt = f"""Analise o seguinte input e identifique se é:
- "single_question": Uma pergunta única e direta
- "questionnaire": Um questionário com múltiplas perguntas
- "unknown": Não é possível determinar

Input: {input_text}

Responda em JSON:
{{"type": "single_question|questionnaire|unknown", "confidence": 0.0-1.0, "metadata": {{}}}}"""
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            # Parse JSON response - tentar extrair JSON do conteúdo
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Tentar extrair JSON do conteúdo (pode ter texto antes/depois)
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
            else:
                # Fallback: tentar parse direto
                result = json.loads(content)
            
            input_type = InputType(**result)
            logger.info(f"Tipo identificado: {input_type.type} (confiança: {input_type.confidence})")
            return input_type
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao fazer parse do JSON: {e}")
            logger.debug(f"Resposta recebida: {content[:200]}")
            return InputType(type="unknown", confidence=0.0, metadata={"error": str(e)})
        except Exception as e:
            logger.error(f"Erro ao identificar tipo de input: {e}")
            return InputType(type="unknown", confidence=0.0, metadata={"error": str(e)})
    
    def identify_input_type_enhanced(self, input_text: str, file_path: Optional[str] = None) -> InputType:
        """Identificação melhorada com suporte a arquivos."""
        logger.info("Iniciando identificação melhorada de tipo de input")
        
        # Heurísticas simples
        question_count = input_text.count('?')
        line_count = len(input_text.split('\n'))
        
        # Se tem arquivo, provavelmente é questionário
        if file_path:
            logger.info(f"Arquivo detectado: {file_path}, classificando como questionário")
            return InputType(
                type="questionnaire",
                confidence=0.9,
                metadata={"source": "file", "file_path": file_path}
            )
        
        # Se tem múltiplas perguntas, é questionário
        if question_count > 1 or line_count > 5:
            logger.info(f"Múltiplas perguntas detectadas (count: {question_count}, lines: {line_count})")
            return InputType(
                type="questionnaire",
                confidence=0.8,
                metadata={"question_count": question_count, "line_count": line_count}
            )
        
        # Caso contrário, usar LLM para decidir
        logger.debug("Usando LLM para identificação")
        return self.identify_input_type(input_text)
    
    def collect_context(self, input_text: str) -> Context:
        """Coletar contexto adicional (cliente, produto, prazos)."""
        logger.info("Iniciando coleta de contexto")
        logger.debug(f"Input para contexto: {input_text[:100]}...")
        
        prompt = f"""Extraia informações de contexto do seguinte input:
- Cliente (se mencionado)
- Produto (se mencionado)
- Prazos (se mencionado)
- Outras informações relevantes

Input: {input_text}

Responda em JSON:
{{"client": "...", "product": "...", "deadlines": "...", "additional_info": {{}}}}"""
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Tentar extrair JSON do conteúdo
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
            else:
                result = json.loads(content)
            
            context = Context(**result)
            logger.info(f"Contexto coletado: cliente={context.client}, produto={context.product}")
            return context
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao fazer parse do JSON do contexto: {e}")
            logger.debug(f"Resposta recebida: {content[:200]}")
            return Context(additional_info={"error": str(e)})
        except Exception as e:
            logger.error(f"Erro ao coletar contexto: {e}")
            return Context(additional_info={"error": str(e)})
    
    def collect_context_interactive(self, input_text: str) -> Context:
        """Coletar contexto com possibilidade de perguntas adicionais."""
        logger.info("Iniciando coleta de contexto interativa")
        context = self.collect_context(input_text)
        
        # Se contexto está incompleto, preparar perguntas
        if not context.client or not context.product:
            context.additional_info["needs_clarification"] = True
            context.additional_info["questions"] = []
            
            if not context.client:
                context.additional_info["questions"].append("Qual é o nome do cliente?")
            if not context.product:
                context.additional_info["questions"].append("Qual produto está sendo proposto?")
            
            logger.info(f"Contexto incompleto, perguntas preparadas: {context.additional_info['questions']}")
        
        return context
    
    def coordinate_agents(
        self,
        input_type: InputType,
        context: Context,
        input_data: str
    ) -> Dict[str, Any]:
        """Coordenar agentes especialistas baseado no tipo de input."""
        logger.info(f"Coordenando agentes para tipo: {input_type.type}")
        
        coordination_plan = {
            "input_type": input_type.type,
            "context": context.model_dump(),
            "next_steps": []
        }
        
        if input_type.type == "single_question":
            coordination_plan["next_steps"] = [
                {
                    "agent": "knowledge",
                    "action": "generate_response",
                    "input": input_data
                }
            ]
            logger.info("Plano: pergunta única -> knowledge agent")
        elif input_type.type == "questionnaire":
            coordination_plan["next_steps"] = [
                {
                    "agent": "parser",
                    "action": "extract_and_normalize",
                    "input": input_data
                },
                {
                    "agent": "knowledge",
                    "action": "generate_responses",
                    "depends_on": "parser"
                },
                {
                    "agent": "verifier",
                    "action": "validate_responses",
                    "depends_on": "knowledge"
                }
            ]
            logger.info("Plano: questionário -> parser -> knowledge -> verifier")
        else:
            logger.warning(f"Tipo desconhecido: {input_type.type}, usando fallback")
            coordination_plan["next_steps"] = [
                {
                    "agent": "knowledge",
                    "action": "generate_response",
                    "input": input_data
                }
            ]
        
        logger.info(f"Plano de coordenação criado com {len(coordination_plan['next_steps'])} passos")
        return coordination_plan
    
    def manage_workflow_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Gerenciar estado do workflow."""
        logger.debug("Gerenciando estado do workflow")
        # Adicionar metadados ao estado
        state["orchestrator"] = {
            "last_update": str(datetime.now()),
            "version": "1.0",
            "session_id": self.session_id
        }
        return state
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """Obter histórico de conversa da memória."""
        if self.memory_manager:
            try:
                memory_vars = self.memory_manager.load_memory_variables()
                return memory_vars.get("chat_history", [])
            except Exception as e:
                logger.warning(f"Erro ao carregar histórico: {e}")
                return []
        return []
    
    def add_to_memory(self, user_input: str, agent_response: str) -> None:
        """Adicionar interação à memória."""
        if self.memory_manager:
            try:
                self.memory_manager.save_context(user_input, agent_response)
                logger.debug("Contexto salvo na memória")
            except Exception as e:
                logger.warning(f"Erro ao salvar na memória: {e}")

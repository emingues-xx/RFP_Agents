"""Coordenador de agentes especialistas."""
from typing import Dict, Any, List, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """Coordenador de agentes."""
    
    def __init__(
        self,
        parser_agent: Optional[Any] = None,
        knowledge_agent: Optional[Any] = None,
        verifier_agent: Optional[Any] = None,
    ):
        """Inicializar coordenador."""
        self.parser_agent = parser_agent
        self.knowledge_agent = knowledge_agent
        self.verifier_agent = verifier_agent
        logger.info("AgentCoordinator inicializado")
    
    async def coordinate_parallel(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Coordenar execução paralela de tarefas."""
        logger.info(f"Coordenando {len(tasks)} tarefas")
        results = {}
        
        # Agrupar tarefas por dependências
        independent_tasks = [t for t in tasks if "depends_on" not in t]
        dependent_tasks = [t for t in tasks if "depends_on" in t]
        
        logger.debug(f"Tarefas independentes: {len(independent_tasks)}, dependentes: {len(dependent_tasks)}")
        
        # Executar tarefas independentes em paralelo
        if independent_tasks:
            try:
                parallel_results = await asyncio.gather(*[
                    self._execute_task(task) for task in independent_tasks
                ])
                for task, result in zip(independent_tasks, parallel_results):
                    results[task["agent"]] = result
                    logger.debug(f"Tarefa {task['agent']} concluída")
            except Exception as e:
                logger.error(f"Erro ao executar tarefas paralelas: {e}")
                raise
        
        # Executar tarefas dependentes sequencialmente
        for task in dependent_tasks:
            dependency = task["depends_on"]
            if dependency in results:
                task["input"] = results[dependency]
                try:
                    result = await self._execute_task(task)
                    results[task["agent"]] = result
                    logger.debug(f"Tarefa {task['agent']} concluída (dependência: {dependency})")
                except Exception as e:
                    logger.error(f"Erro ao executar tarefa {task['agent']}: {e}")
                    raise
            else:
                logger.warning(f"Dependência '{dependency}' não encontrada para tarefa {task['agent']}")
        
        logger.info(f"Coordenação concluída: {len(results)} resultados")
        return results
    
    async def _execute_task(self, task: Dict[str, Any]) -> Any:
        """Executar tarefa individual."""
        agent_name = task["agent"]
        action = task["action"]
        input_data = task.get("input")
        
        logger.debug(f"Executando tarefa: {agent_name}.{action}")
        
        try:
            if agent_name == "parser":
                if not self.parser_agent:
                    raise ValueError("ParserAgent não está disponível")
                # Assumindo que o parser tem um método process
                if hasattr(self.parser_agent, 'process'):
                    if asyncio.iscoroutinefunction(self.parser_agent.process):
                        return await self.parser_agent.process(input_data)
                    else:
                        return self.parser_agent.process(input_data)
                else:
                    raise ValueError(f"ParserAgent não tem método 'process'")
            
            elif agent_name == "knowledge":
                if not self.knowledge_agent:
                    raise ValueError("KnowledgeAgent não está disponível")
                # Assumindo que o knowledge tem um método generate_response
                if hasattr(self.knowledge_agent, 'generate_response'):
                    if asyncio.iscoroutinefunction(self.knowledge_agent.generate_response):
                        return await self.knowledge_agent.generate_response(input_data)
                    else:
                        return self.knowledge_agent.generate_response(input_data)
                else:
                    raise ValueError(f"KnowledgeAgent não tem método 'generate_response'")
            
            elif agent_name == "verifier":
                if not self.verifier_agent:
                    raise ValueError("VerifierAgent não está disponível")
                # Assumindo que o verifier tem um método verify
                if hasattr(self.verifier_agent, 'verify'):
                    if asyncio.iscoroutinefunction(self.verifier_agent.verify):
                        return await self.verifier_agent.verify(input_data)
                    else:
                        return self.verifier_agent.verify(input_data)
                else:
                    raise ValueError(f"VerifierAgent não tem método 'verify'")
            
            else:
                raise ValueError(f"Agente desconhecido: {agent_name}")
        except Exception as e:
            logger.error(f"Erro ao executar tarefa {agent_name}.{action}: {e}")
            raise


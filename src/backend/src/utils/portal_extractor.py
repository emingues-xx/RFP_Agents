"""Extrator de questionários de portais usando MCP."""
from typing import Dict, Any, Optional, List
from src.mcp.mcp_tools import MCPToolManager
from src.utils.metrics import (
    parser_extractions_total,
    parser_extraction_duration_seconds
)
import logging
import time
import asyncio

logger = logging.getLogger(__name__)


class PortalExtractor:
    """Extrator de questionários de portais via MCP."""
    
    def __init__(self):
        """Inicializar extrator."""
        self.mcp_manager = MCPToolManager()
        logger.info("PortalExtractor inicializado")
    
    async def extract_from_portal(
        self,
        portal_url: str,
        portal_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extrair questionário de um portal.
        
        Args:
            portal_url: URL do portal/RFP
            portal_type: Tipo de portal (opcional, será detectado automaticamente)
        
        Returns:
            Dicionário com questionário extraído
        """
        start_time = time.time()
        
        try:
            # Detectar tipo de portal se não fornecido
            if not portal_type:
                portal_type = self._detect_portal_type(portal_url)
            
            logger.info(f"Extraindo questionário de {portal_type}: {portal_url}")
            
            # Extrair usando MCP baseado no tipo
            if portal_type == "playwright":
                questionnaire = await self._extract_with_playwright(portal_url)
            elif portal_type == "atlassian":
                questionnaire = await self._extract_with_atlassian(portal_url)
            else:
                # Tentar extração genérica
                questionnaire = await self._extract_generic(portal_url)
            
            duration = time.time() - start_time
            
            # Métricas
            parser_extractions_total.labels(
                file_type=f"portal_{portal_type}",
                status="success"
            ).inc()
            parser_extraction_duration_seconds.labels(
                file_type=f"portal_{portal_type}"
            ).observe(duration)
            
            logger.info(f"Questionário extraído com sucesso em {duration:.2f}s")
            
            return {
                "success": True,
                "portal_url": portal_url,
                "portal_type": portal_type,
                "questionnaire": questionnaire,
                "extraction_method": "mcp"
            }
            
        except Exception as e:
            duration = time.time() - start_time
            portal_type = portal_type or "unknown"
            
            parser_extractions_total.labels(
                file_type=f"portal_{portal_type}",
                status="error"
            ).inc()
            parser_extraction_duration_seconds.labels(
                file_type=f"portal_{portal_type}"
            ).observe(duration)
            
            logger.error(f"Erro ao extrair questionário do portal {portal_url}: {e}")
            raise
    
    def _detect_portal_type(self, url: str) -> str:
        """Detectar tipo de portal baseado na URL.
        
        Args:
            url: URL do portal
        
        Returns:
            Tipo de portal detectado
        """
        url_lower = url.lower()
        
        # Detectar tipos conhecidos
        if "atlassian" in url_lower or "jira" in url_lower or "confluence" in url_lower:
            return "atlassian"
        elif "playwright" in url_lower or "browser" in url_lower:
            return "playwright"
        else:
            # Tentar genérico primeiro
            return "generic"
    
    async def _extract_with_playwright(self, url: str) -> str:
        """Extrair usando Playwright MCP.
        
        Args:
            url: URL do portal
        
        Returns:
            Texto extraído
        """
        try:
            # Verificar se cliente Playwright está disponível
            if "playwright" not in self.mcp_manager.clients:
                # Tentar criar cliente Playwright
                try:
                    from src.mcp.mcp_factory import MCPFactory
                    playwright_client = MCPFactory.create_npm_client(
                        "playwright",
                        "@playwright/mcp-server"
                    )
                    self.mcp_manager.add_client("playwright", playwright_client)
                except Exception as e:
                    logger.warning(f"Não foi possível criar cliente Playwright: {e}")
                    raise ValueError("Cliente Playwright MCP não disponível")
            
            # Usar Playwright para navegar e extrair
            result = await self.mcp_manager.call_tool(
                "playwright",
                "navigate_and_extract",
                {
                    "url": url,
                    "selector": "body",  # Extrair todo o conteúdo
                    "wait_for": "networkidle"
                },
                timeout=60
            )
            
            # Processar resultado
            if isinstance(result, dict):
                return result.get("content", str(result))
            elif isinstance(result, list):
                return "\n".join(str(item) for item in result)
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"Erro ao extrair com Playwright: {e}")
            raise
    
    async def _extract_with_atlassian(self, url: str) -> str:
        """Extrair usando Atlassian MCP.
        
        Args:
            url: URL do portal Atlassian
        
        Returns:
            Texto extraído
        """
        try:
            # Verificar se cliente Atlassian está disponível
            if "atlassian" not in self.mcp_manager.clients:
                # Tentar criar cliente Atlassian
                try:
                    from src.mcp.mcp_factory import MCPFactory
                    atlassian_client = MCPFactory.create_npm_client(
                        "atlassian",
                        "@atlassian/mcp-server"
                    )
                    self.mcp_manager.add_client("atlassian", atlassian_client)
                except Exception as e:
                    logger.warning(f"Não foi possível criar cliente Atlassian: {e}")
                    raise ValueError("Cliente Atlassian MCP não disponível")
            
            # Extrair conteúdo do Atlassian
            result = await self.mcp_manager.call_tool(
                "atlassian",
                "get_content",
                {
                    "url": url
                },
                timeout=60
            )
            
            # Processar resultado
            if isinstance(result, dict):
                return result.get("content", result.get("body", str(result)))
            elif isinstance(result, list):
                return "\n".join(str(item) for item in result)
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"Erro ao extrair com Atlassian: {e}")
            raise
    
    async def _extract_generic(self, url: str) -> str:
        """Extração genérica usando HTTP request.
        
        Args:
            url: URL do portal
        
        Returns:
            Texto extraído
        """
        try:
            import httpx
            
            # Fazer requisição HTTP
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Extrair texto HTML básico
                content = response.text
                
                # Tentar extrair apenas texto (remover HTML básico)
                import re
                # Remover tags HTML
                text = re.sub(r'<[^>]+>', '', content)
                # Remover espaços múltiplos
                text = re.sub(r'\s+', ' ', text)
                
                logger.info(f"Extraído {len(text)} caracteres via HTTP genérico")
                return text
                
        except Exception as e:
            logger.error(f"Erro na extração genérica: {e}")
            raise
    
    async def extract_and_parse(
        self,
        portal_url: str,
        parser_agent: Any,
        portal_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extrair e parsear questionário de portal.
        
        Args:
            portal_url: URL do portal
            parser_agent: Instância do ParserAgent
            portal_type: Tipo de portal (opcional)
        
        Returns:
            Dicionário com perguntas parseadas
        """
        # Extrair texto do portal
        extraction_result = await self.extract_from_portal(portal_url, portal_type)
        
        if not extraction_result["success"]:
            raise Exception("Falha na extração do portal")
        
        questionnaire_text = extraction_result["questionnaire"]
        
        # Parsear com ParserAgent
        parsed_questions = parser_agent.normalize_questions(questionnaire_text)
        
        return {
            "success": True,
            "portal_url": portal_url,
            "extraction": extraction_result,
            "parsed_questions": [q.model_dump() if hasattr(q, 'model_dump') else q for q in parsed_questions],
            "question_count": len(parsed_questions)
        }


"""Factory para criação de LLMs."""
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from src.config.llm_config import LLMConfig
import logging

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory para criar instâncias de LLM."""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Inicializar factory com configuração."""
        self.config = config or LLMConfig()
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validar configuração dos providers."""
        if self.config.default_provider == "openai" and not self.config.openai_api_key:
            raise ValueError("OpenAI API key não configurada")
        if self.config.default_provider == "anthropic" and not self.config.anthropic_api_key:
            raise ValueError("Anthropic API key não configurada")
    
    def create_openai_llm(self) -> ChatOpenAI:
        """Criar instância do OpenAI LLM."""
        if not self.config.openai_api_key:
            raise ValueError("OpenAI API key não configurada")
        
        return ChatOpenAI(
            model=self.config.openai_model,
            temperature=self.config.openai_temperature,
            max_tokens=self.config.openai_max_tokens,
            api_key=self.config.openai_api_key,
        )
    
    def create_anthropic_llm(self) -> ChatAnthropic:
        """Criar instância do Anthropic LLM."""
        if not self.config.anthropic_api_key:
            raise ValueError("Anthropic API key não configurada")
        
        return ChatAnthropic(
            model=self.config.anthropic_model,
            temperature=self.config.anthropic_temperature,
            max_tokens=self.config.anthropic_max_tokens,
            api_key=self.config.anthropic_api_key,
        )
    
    def get_default_llm(self) -> BaseChatModel:
        """Obter LLM padrão configurado."""
        try:
            if self.config.default_provider == "openai":
                return self.create_openai_llm()
            elif self.config.default_provider == "anthropic":
                return self.create_anthropic_llm()
            else:
                raise ValueError(f"Provider desconhecido: {self.config.default_provider}")
        except Exception as e:
            logger.error(f"Erro ao criar LLM padrão: {e}")
            if self.config.enable_fallback:
                return self.get_fallback_llm()
            raise
    
    def get_fallback_llm(self) -> BaseChatModel:
        """Obter LLM de fallback."""
        try:
            if self.config.fallback_provider == "openai":
                return self.create_openai_llm()
            elif self.config.fallback_provider == "anthropic":
                return self.create_anthropic_llm()
            else:
                raise ValueError(f"Provider de fallback desconhecido: {self.config.fallback_provider}")
        except Exception as e:
            logger.error(f"Erro ao criar LLM de fallback: {e}")
            raise
    
    def get_llm_by_provider(self, provider: str) -> BaseChatModel:
        """Obter LLM por provider específico."""
        if provider == "openai":
            return self.create_openai_llm()
        elif provider == "anthropic":
            return self.create_anthropic_llm()
        else:
            raise ValueError(f"Provider desconhecido: {provider}")


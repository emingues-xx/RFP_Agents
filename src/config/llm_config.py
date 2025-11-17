"""Configuração de LLM Providers."""
from typing import Literal, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class LLMConfig(BaseSettings):
    """Configuração de LLM Providers."""
    
    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    openai_max_tokens: int = Field(default=2000, env="OPENAI_MAX_TOKENS")
    
    # Anthropic
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022", env="ANTHROPIC_MODEL")
    anthropic_temperature: float = Field(default=0.7, env="ANTHROPIC_TEMPERATURE")
    anthropic_max_tokens: int = Field(default=2000, env="ANTHROPIC_MAX_TOKENS")
    
    # Provider padrão
    default_provider: Literal["openai", "anthropic"] = Field(
        default="openai", env="DEFAULT_LLM_PROVIDER"
    )
    
    # Fallback
    enable_fallback: bool = Field(default=True, env="ENABLE_LLM_FALLBACK")
    fallback_provider: Literal["openai", "anthropic"] = Field(
        default="anthropic", env="FALLBACK_LLM_PROVIDER"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


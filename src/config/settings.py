"""Configurações e variáveis de ambiente."""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    # Database
    database_url: str = Field(
        default="postgresql://postgres:postgres@postgres:5432/rfp_agents",
        env="DATABASE_URL"
    )
    
    # Redis
    redis_url: str = Field(
        default="redis://:redis_password@redis:6379/0",
        env="REDIS_URL"
    )
    redis_password: str = Field(default="redis_password", env="REDIS_PASSWORD")
    
    # Milvus
    milvus_host: str = Field(default="milvus", env="MILVUS_HOST")
    milvus_port: int = Field(default=19530, env="MILVUS_PORT")
    milvus_username: str = Field(default="root", env="MILVUS_USERNAME")
    milvus_password: str = Field(default="Milvus", env="MILVUS_PASSWORD")
    
    # MinIO
    minio_access_key: str = Field(default="minioadmin", env="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(default="minioadmin", env="MINIO_SECRET_KEY")
    minio_endpoint: str = Field(default="minio:9000", env="MINIO_ENDPOINT")
    minio_bucket: str = Field(default="rfp-documents", env="MINIO_BUCKET")
    
    # Langfuse
    langfuse_url: str = Field(default="http://localhost:3000", env="LANGFUSE_URL")
    langfuse_public_key: Optional[str] = Field(default=None, env="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: Optional[str] = Field(default=None, env="LANGFUSE_SECRET_KEY")
    
    # Application
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    debug: bool = Field(default=False, env="DEBUG")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instância global
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Obter instância de configurações (singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

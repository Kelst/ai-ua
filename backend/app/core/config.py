"""Configuration management using pydantic-settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1

    # Model Configuration
    model_path: str = "/app/models/mamay-gemma-3-12b-q5_k_m.gguf"
    model_name: str = "mamay-gemma-3-12b"
    model_context_size: int = 128000
    model_threads: int = 16
    model_batch_size: int = 512
    model_gpu_layers: int = 0

    # Generation Defaults
    default_temperature: float = 0.3
    default_max_tokens: int = 8192
    default_top_k: int = 40
    default_top_p: float = 0.95

    # Embeddings Configuration
    embeddings_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    embeddings_dimensions: int = 768
    embeddings_host: str = "embeddings-service"
    embeddings_port: int = 8001

    # Concurrency
    max_concurrent_requests: int = 4
    request_timeout: int = 300

    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

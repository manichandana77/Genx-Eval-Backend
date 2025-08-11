"""
DeepEval Service Configuration
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Service configuration settings"""
    
    # Service Identity
    service_name: str = "deepeval"
    service_version: str = "1.0.0"
    
    # Server Configuration
    grpc_port: int = 50051
    http_port: int = 8001
    environment: str = "development"
    
    # DeepEval Configuration
   
    deepeval_telemetry_opt_out: bool = True
    deepeval_cache_enabled: bool = True
    
    # Metrics Configuration
    default_metrics: str = "answer_relevancy,faithfulness,bias"
    enable_safety_metrics: bool = True
    enable_custom_metrics: bool = True
    enable_performance_metrics: bool = False
    
    # Processing Configuration
    max_concurrent_metrics: int = 5
    metric_timeout_seconds: int = 60
    batch_processing_enabled: bool = True
    max_batch_size: int = 100
    
    # Model Configuration
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.0
    llm_max_tokens: int = 1000
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Initialize settings on import
settings = get_settings()

# Set OpenAI API key for DeepEval


# Set DeepEval telemetry
if settings.deepeval_telemetry_opt_out:
    os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"

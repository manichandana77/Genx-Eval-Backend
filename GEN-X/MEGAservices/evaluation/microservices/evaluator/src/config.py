"""
Evaluator Service Configuration
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Evaluator service configuration settings"""
    
    # Service Identity
    service_name: str = "evaluator"
    service_version: str = "1.0.0"
    environment: str = "development"
    
    # Server Configuration
    http_port: int = 8000
    debug: bool = False
    
    # Database Configuration (MongoDB)
    mongo_uri: str = "mongodb://localhost:27017/evaluation_db"
    db_name: str = "evaluation_db"
    results_collection: str = "results"
    status_collection: str = "status"
    config_collection: str = "config"
    metrics_collection: str = "metrics"
    
    # gRPC Client Configuration
    deepeval_grpc_host: str = "deepeval:50051"
    grpc_timeout_seconds: int = 300
    grpc_max_retries: int = 3
    grpc_retry_delay: float = 1.0
    
    # Evaluation Configuration
    max_concurrent_evaluations: int = 5
    default_evaluation_timeout: int = 3600
    dataset_upload_max_size: str = "100MB"
    supported_dataset_formats: str = "yaml,json,csv"
    
    # Model Configuration
    default_metrics: str = "answer_relevancy,faithfulness,bias"
    enable_streaming_responses: bool = True
    model_timeout_seconds: int = 120
    
    # File Storage Configuration
    upload_dir: str = "/app/data/uploads"
    results_dir: str = "/app/data/results"
    log_dir: str = "/app/logs"
    max_file_size_mb: int = 100
    
    # API Configuration
    cors_origins: List[str] = ["*"]
    api_rate_limit: int = 100
    api_rate_limit_window: int = 60
    
    # External Model API Configuration
    model_api_timeout: int = 60
    model_api_max_retries: int = 3
    model_api_base_url: str = "http://localhost:8000"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"
    
    @property
    def default_metrics_list(self) -> List[str]:
        """Get default metrics as list"""
        return [m.strip() for m in self.default_metrics.split(",")]
    
    @property
    def supported_formats_list(self) -> List[str]:
        """Get supported dataset formats as list"""
        return [f.strip() for f in self.supported_dataset_formats.split(",")]
    
    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

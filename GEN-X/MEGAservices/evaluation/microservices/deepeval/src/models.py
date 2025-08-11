"""
Internal Pydantic Models for DeepEval Service
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class MetricType(str, Enum):
    """Available metric types"""
    # RAG Metrics
    ANSWER_RELEVANCY = "answer_relevancy"
    FAITHFULNESS = "faithfulness"
    CONTEXTUAL_PRECISION = "contextual_precision"
    CONTEXTUAL_RECALL = "contextual_recall"
    CONTEXTUAL_RELEVANCY = "contextual_relevancy"
    
    # Safety Metrics
    BIAS = "bias"
    TOXICITY = "toxicity"
    HALLUCINATION = "hallucination"
    
    # Task-Specific Metrics
    SUMMARIZATION = "summarization"
    CLASSIFICATION = "classification"
    GENERATION = "generation"
    
    # Custom Metrics
    GEVAL = "geval"
    CUSTOM = "custom"


class EvaluationData(BaseModel):
    """Internal evaluation data model"""
    question: str = ""
    answer: str = ""
    context: str = ""
    expected_answer: str = ""
    reference_output: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MetricRequest(BaseModel):
    """Single metric calculation request"""
    metric_type: MetricType
    evaluation_data: EvaluationData
    config: Dict[str, Any] = Field(default_factory=dict)


class MetricResult(BaseModel):
    """Single metric calculation result"""
    metric_name: str
    score: float
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float = 0.0


class BatchMetricRequest(BaseModel):
    """Batch metric calculation request (internal)"""
    items: List[EvaluationData]
    metrics: List[MetricType]
    process_id: str
    user_id: str
    global_config: Dict[str, Any] = Field(default_factory=dict)


class BatchMetricResult(BaseModel):
    """Batch metric calculation result (internal)"""
    results: List[Dict[str, Any]]  # List of item results
    success: bool = True
    total_processed: int = 0
    successful_count: int = 0
    failed_count: int = 0
    total_execution_time_ms: float = 0.0
    summary_stats: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None


class AvailableMetrics(BaseModel):
    """Available metrics information"""
    rag_metrics: List[str] = [
        "answer_relevancy", 
        "faithfulness", 
        "contextual_precision", 
        "contextual_recall", 
        "contextual_relevancy"
    ]
    safety_ethics: List[str] = ["bias", "toxicity", "hallucination"]
    task_specific: List[str] = ["summarization", "classification", "generation"]
    custom_metrics: List[str] = ["geval", "custom"]
    
    @property
    def all_metrics(self) -> List[str]:
        """Get all available metrics"""
        return (self.rag_metrics + 
                self.safety_ethics + 
                self.task_specific + 
                self.custom_metrics)


class ServiceHealth(BaseModel):
    """Service health status"""
    status: str = "healthy"
    version: str = "1.0.0"
    available_metrics: int = 0
    uptime_seconds: float = 0.0
    last_check: str = ""

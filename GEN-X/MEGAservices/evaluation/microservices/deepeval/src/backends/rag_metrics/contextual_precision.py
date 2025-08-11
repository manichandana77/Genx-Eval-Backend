"""
Contextual Precision Metric
🎯 Measures precision of context retrieval for the query
"""
from typing import Dict, Any
import structlog

from backends.core_metric_logic import DeepEvalMetricWrapper
from models import EvaluationData, MetricResult

logger = structlog.get_logger()


class ContextualPrecisionMetric(DeepEvalMetricWrapper):
    """
    Contextual Precision Metric using DeepEval
    
    Evaluates how precise the retrieved context is for answering the question.
    High precision means less irrelevant information in the context.
    """
    
    def __init__(self):
        try:
            from deepeval.metrics import ContextualPrecisionMetric as DeepEvalContextualPrecision
            super().__init__("contextual_precision", DeepEvalContextualPrecision)
            
            self.timeout_seconds = 100
            
            logger.info("✅ Contextual Precision Metric initialized")
            
        except ImportError as e:
            logger.error("❌ Failed to import DeepEval ContextualPrecisionMetric", error=str(e))
            raise Exception("DeepEval library not available for Contextual Precision")
    
    def _validate_input(self, data: EvaluationData):
        """Validate input data for contextual precision"""
        super()._validate_input(data)
        
        if not data.context.strip():
            raise ValueError("Context is required for contextual precision metric")
            
        if not data.expected_answer.strip():
            raise ValueError("Expected answer is required for contextual precision metric")
    
    async def _calculate_metric(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Calculate contextual precision using DeepEval"""
        try:
            logger.info("🔍 Calculating contextual precision", 
                       context_length=len(data.context))
            
            score = await super()._calculate_metric(data, config)
            normalized_score = max(0.0, min(1.0, score))
            
            logger.info("📊 Contextual precision calculated", score=normalized_score)
            
            return normalized_score
            
        except Exception as e:
            logger.error("💥 Contextual precision calculation failed", error=str(e))
            raise

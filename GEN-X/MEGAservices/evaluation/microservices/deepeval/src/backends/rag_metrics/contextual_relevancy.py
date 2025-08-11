"""
Contextual Relevancy Metric
🎯 Measures how relevant the context is to the query
"""
from typing import Dict, Any
import structlog

from backends.core_metric_logic import DeepEvalMetricWrapper
from models import EvaluationData, MetricResult

logger = structlog.get_logger()


class ContextualRelevancyMetric(DeepEvalMetricWrapper):
    """
    Contextual Relevancy Metric using DeepEval
    
    Evaluates how relevant the retrieved context is to the given question.
    Helps identify if the retrieval system is working effectively.
    """
    
    def __init__(self):
        try:
            from deepeval.metrics import ContextualRelevancyMetric as DeepEvalContextualRelevancy
            super().__init__("contextual_relevancy", DeepEvalContextualRelevancy)
            
            self.timeout_seconds = 90
            
            logger.info("✅ Contextual Relevancy Metric initialized")
            
        except ImportError as e:
            logger.error("❌ Failed to import DeepEval ContextualRelevancyMetric", error=str(e))
            raise Exception("DeepEval library not available for Contextual Relevancy")
    
    def _validate_input(self, data: EvaluationData):
        """Validate input data for contextual relevancy"""
        super()._validate_input(data)
        
        if not data.context.strip():
            raise ValueError("Context is required for contextual relevancy metric")
    
    async def _calculate_metric(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Calculate contextual relevancy using DeepEval"""
        try:
            logger.info("🔍 Calculating contextual relevancy")
            
            score = await super()._calculate_metric(data, config)
            normalized_score = max(0.0, min(1.0, score))
            
            logger.info("📊 Contextual relevancy calculated", score=normalized_score)
            
            return normalized_score
            
        except Exception as e:
            logger.error("💥 Contextual relevancy calculation failed", error=str(e))
            raise

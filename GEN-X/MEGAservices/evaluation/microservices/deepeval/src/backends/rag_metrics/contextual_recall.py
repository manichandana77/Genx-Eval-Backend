"""
Contextual Recall Metric
🎯 Measures recall of context retrieval for the query
"""
from typing import Dict, Any
import structlog

from backends.core_metric_logic import DeepEvalMetricWrapper
from models import EvaluationData, MetricResult

logger = structlog.get_logger()


class ContextualRecallMetric(DeepEvalMetricWrapper):
    """
    Contextual Recall Metric using DeepEval
    
    Evaluates how well the retrieved context covers all information needed 
    to answer the question. High recall means no important information is missing.
    """
    
    def __init__(self):
        try:
            from deepeval.metrics import ContextualRecallMetric as DeepEvalContextualRecall
            super().__init__("contextual_recall", DeepEvalContextualRecall)
            
            self.timeout_seconds = 100
            
            logger.info("✅ Contextual Recall Metric initialized")
            
        except ImportError as e:
            logger.error("❌ Failed to import DeepEval ContextualRecallMetric", error=str(e))
            raise Exception("DeepEval library not available for Contextual Recall")
    
    def _validate_input(self, data: EvaluationData):
        """Validate input data for contextual recall"""
        super()._validate_input(data)
        
        if not data.context.strip():
            raise ValueError("Context is required for contextual recall metric")
            
        if not data.expected_answer.strip():
            raise ValueError("Expected answer is required for contextual recall metric")
    
    async def _calculate_metric(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Calculate contextual recall using DeepEval"""
        try:
            logger.info("🔍 Calculating contextual recall")
            
            score = await super()._calculate_metric(data, config)
            normalized_score = max(0.0, min(1.0, score))
            
            logger.info("📊 Contextual recall calculated", score=normalized_score)
            
            return normalized_score
            
        except Exception as e:
            logger.error("💥 Contextual recall calculation failed", error=str(e))
            raise

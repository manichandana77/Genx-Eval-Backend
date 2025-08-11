"""
Answer Relevancy Metric
🎯 Measures how relevant the answer is to the given question
"""
from typing import Dict, Any
import structlog

from backends.core_metric_logic import DeepEvalMetricWrapper
from models import EvaluationData, MetricResult

logger = structlog.get_logger()


class AnswerRelevancyMetric(DeepEvalMetricWrapper):
    """
    Answer Relevancy Metric using DeepEval
    
    Evaluates how well the generated answer addresses the specific question asked.
    Uses LLM-based evaluation to determine relevance.
    """
    
    def __init__(self):
        try:
            from deepeval.metrics import AnswerRelevancyMetric as DeepEvalAnswerRelevancy
            super().__init__("answer_relevancy", DeepEvalAnswerRelevancy)
            
            # Configure metric-specific settings
            self.timeout_seconds = 90  # Longer timeout for LLM calls
            
            logger.info("✅ Answer Relevancy Metric initialized")
            
        except ImportError as e:
            logger.error("❌ Failed to import DeepEval AnswerRelevancyMetric", error=str(e))
            raise Exception("DeepEval library not available for Answer Relevancy")
    
    def _validate_input(self, data: EvaluationData):
        """Validate input data for answer relevancy"""
        super()._validate_input(data)
        
        if not data.question.strip():
            raise ValueError("Question is required for answer relevancy metric")
        
        if not data.answer.strip():
            raise ValueError("Answer is required for answer relevancy metric")
    
    async def _calculate_metric(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Calculate answer relevancy using DeepEval"""
        try:
            logger.info("🔍 Calculating answer relevancy", 
                       question_preview=data.question[:50])
            
            # Use parent class DeepEval wrapper
            score = await super()._calculate_metric(data, config)
            
            # Answer relevancy scores are typically 0-1, ensure proper range
            normalized_score = max(0.0, min(1.0, score))
            
            logger.info("📊 Answer relevancy calculated", 
                       score=normalized_score,
                       question_preview=data.question[:50])
            
            return normalized_score
            
        except Exception as e:
            logger.error("💥 Answer relevancy calculation failed", error=str(e))
            raise

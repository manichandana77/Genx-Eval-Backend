"""
Faithfulness Metric
🎯 Measures how factually accurate the answer is given the context
"""
from typing import Dict, Any
import structlog

from backends.core_metric_logic import DeepEvalMetricWrapper
from models import EvaluationData, MetricResult

logger = structlog.get_logger()


class FaithfulnessMetric(DeepEvalMetricWrapper):
    """
    Faithfulness Metric using DeepEval
    
    Evaluates whether the generated answer is factually consistent with the given context.
    Essential for RAG applications to prevent hallucinations.
    """
    
    def __init__(self):
        try:
            from deepeval.metrics import FaithfulnessMetric as DeepEvalFaithfulness
            super().__init__("faithfulness", DeepEvalFaithfulness)
            
            self.timeout_seconds = 120  # Longer timeout for complex faithfulness checks
            
            logger.info("✅ Faithfulness Metric initialized")
            
        except ImportError as e:
            logger.error("❌ Failed to import DeepEval FaithfulnessMetric", error=str(e))
            raise Exception("DeepEval library not available for Faithfulness")
    
    def _validate_input(self, data: EvaluationData):
        """Validate input data for faithfulness"""
        super()._validate_input(data)
        
        if not data.context.strip():
            raise ValueError("Context is required for faithfulness metric")
            
        if not data.answer.strip():
            raise ValueError("Answer is required for faithfulness metric")
    
    async def _calculate_metric(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Calculate faithfulness using DeepEval"""
        try:
            logger.info("🔍 Calculating faithfulness", 
                       context_preview=data.context[:50],
                       answer_preview=data.answer[:50])
            
            # Use parent class DeepEval wrapper
            score = await super()._calculate_metric(data, config)
            
            # Faithfulness scores are typically 0-1
            normalized_score = max(0.0, min(1.0, score))
            
            logger.info("📊 Faithfulness calculated", 
                       score=normalized_score,
                       context_length=len(data.context))
            
            return normalized_score
            
        except Exception as e:
            logger.error("💥 Faithfulness calculation failed", error=str(e))
            raise

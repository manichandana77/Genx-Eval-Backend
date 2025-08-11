"""
Hallucination Detection Metric
🎯 Detects when the model generates false or unverifiable information
"""
from typing import Dict, Any
import structlog

from backends.core_metric_logic import DeepEvalMetricWrapper
from models import EvaluationData, MetricResult

logger = structlog.get_logger()


class HallucinationMetric(DeepEvalMetricWrapper):
    """
    Hallucination Detection Metric using DeepEval
    
    Detects when the generated answer contains information that is not supported 
    by the given context or contains factually incorrect information.
    """
    
    def __init__(self):
        try:
            from deepeval.metrics import HallucinationMetric as DeepEvalHallucination
            super().__init__("hallucination", DeepEvalHallucination)
            
            self.timeout_seconds = 150  # Hallucination detection can be complex
            
            logger.info("✅ Hallucination Detection Metric initialized")
            
        except ImportError as e:
            logger.error("❌ Failed to import DeepEval HallucinationMetric", error=str(e))
            raise Exception("DeepEval library not available for Hallucination Detection")
    
    def _validate_input(self, data: EvaluationData):
        """Validate input data for hallucination detection"""
        super()._validate_input(data)
        
        if not data.answer.strip():
            raise ValueError("Answer is required for hallucination detection")
            
        if not data.context.strip():
            raise ValueError("Context is required for hallucination detection")
    
    async def _calculate_metric(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Calculate hallucination score using DeepEval"""
        try:
            logger.info("🔍 Calculating hallucination detection", 
                       context_length=len(data.context),
                       answer_length=len(data.answer))
            
            score = await super()._calculate_metric(data, config)
            
            # Hallucination scores: 0 = no hallucination, 1 = high hallucination
            normalized_score = max(0.0, min(1.0, score))
            
            # Determine hallucination level
            if normalized_score < 0.2:
                hallucination_level = "minimal"
            elif normalized_score < 0.5:
                hallucination_level = "low"
            elif normalized_score < 0.8:
                hallucination_level = "moderate"
            else:
                hallucination_level = "high"
            
            logger.info("📊 Hallucination detection completed", 
                       score=normalized_score,
                       hallucination_level=hallucination_level)
            
            return normalized_score
            
        except Exception as e:
            logger.error("💥 Hallucination detection failed", error=str(e))
            raise

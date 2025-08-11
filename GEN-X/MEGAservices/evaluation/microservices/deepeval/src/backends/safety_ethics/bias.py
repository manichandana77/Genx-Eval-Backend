"""
Bias Detection Metric
🎯 Detects various forms of bias in generated content
"""
from typing import Dict, Any
import structlog

from backends.core_metric_logic import DeepEvalMetricWrapper
from models import EvaluationData, MetricResult

logger = structlog.get_logger()


class BiasMetric(DeepEvalMetricWrapper):
    """
    Bias Detection Metric using DeepEval
    
    Detects various forms of bias including gender, racial, political, and other biases
    in the generated answers. Essential for fair and ethical AI systems.
    """
    
    def __init__(self):
        try:
            from deepeval.metrics import BiasMetric as DeepEvalBias
            super().__init__("bias", DeepEvalBias)
            
            self.timeout_seconds = 120  # Bias detection can be complex
            
            logger.info("✅ Bias Detection Metric initialized")
            
        except ImportError as e:
            logger.error("❌ Failed to import DeepEval BiasMetric", error=str(e))
            raise Exception("DeepEval library not available for Bias Detection")
    
    def _validate_input(self, data: EvaluationData):
        """Validate input data for bias detection"""
        super()._validate_input(data)
        
        # Bias detection primarily needs the answer/output text
        if not data.answer.strip():
            raise ValueError("Answer is required for bias detection")
    
    async def _calculate_metric(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Calculate bias score using DeepEval"""
        try:
            logger.info("🔍 Calculating bias detection", 
                       answer_length=len(data.answer))
            
            # Configure bias categories if specified in config
            bias_categories = config.get("bias_categories", [
                "gender", "race", "religion", "political", "age", "disability"
            ])
            
            # Use parent class DeepEval wrapper
            score = await super()._calculate_metric(data, config)
            
            # Bias scores: 0 = no bias detected, 1 = high bias detected
            # We want lower scores to be better, so normalize accordingly
            normalized_score = max(0.0, min(1.0, score))
            
            # Log bias detection results
            bias_level = "low" if normalized_score < 0.3 else "medium" if normalized_score < 0.7 else "high"
            logger.info("📊 Bias detection completed", 
                       score=normalized_score,
                       bias_level=bias_level,
                       categories_checked=bias_categories)
            
            return normalized_score
            
        except Exception as e:
            logger.error("💥 Bias detection failed", error=str(e))
            raise

"""
Toxicity Detection Metric
🎯 Detects toxic, harmful, or inappropriate content
"""
from typing import Dict, Any
import structlog

from backends.core_metric_logic import DeepEvalMetricWrapper
from models import EvaluationData, MetricResult

logger = structlog.get_logger()


class ToxicityMetric(DeepEvalMetricWrapper):
    """
    Toxicity Detection Metric using DeepEval
    
    Detects toxic, harmful, offensive, or inappropriate content in generated answers.
    Critical for maintaining safe and professional AI interactions.
    """
    
    def __init__(self):
        try:
            from deepeval.metrics import ToxicityMetric as DeepEvalToxicity
            super().__init__("toxicity", DeepEvalToxicity)
            
            self.timeout_seconds = 90
            
            logger.info("✅ Toxicity Detection Metric initialized")
            
        except ImportError as e:
            logger.error("❌ Failed to import DeepEval ToxicityMetric", error=str(e))
            raise Exception("DeepEval library not available for Toxicity Detection")
    
    def _validate_input(self, data: EvaluationData):
        """Validate input data for toxicity detection"""
        super()._validate_input(data)
        
        if not data.answer.strip():
            raise ValueError("Answer is required for toxicity detection")
    
    async def _calculate_metric(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Calculate toxicity score using DeepEval"""
        try:
            logger.info("🔍 Calculating toxicity detection", 
                       answer_length=len(data.answer))
            
            # Get toxicity threshold from config (default 0.5)
            threshold = config.get("toxicity_threshold", 0.5)
            
            score = await super()._calculate_metric(data, config)
            
            # Toxicity scores: 0 = not toxic, 1 = highly toxic
            normalized_score = max(0.0, min(1.0, score))
            
            # Determine toxicity level
            if normalized_score < 0.2:
                toxicity_level = "safe"
            elif normalized_score < 0.5:
                toxicity_level = "mild"
            elif normalized_score < 0.8:
                toxicity_level = "concerning"
            else:
                toxicity_level = "toxic"
            
            logger.info("📊 Toxicity detection completed", 
                       score=normalized_score,
                       toxicity_level=toxicity_level,
                       threshold=threshold)
            
            return normalized_score
            
        except Exception as e:
            logger.error("💥 Toxicity detection failed", error=str(e))
            raise

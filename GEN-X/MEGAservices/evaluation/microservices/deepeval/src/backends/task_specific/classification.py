"""
Classification Accuracy Metric
🎯 Evaluates classification task performance
"""
from typing import Dict, Any
import structlog

from backends.core_metric_logic import BaseMetric
from models import EvaluationData, MetricResult

logger = structlog.get_logger()


class ClassificationMetric(BaseMetric):
    """
    Classification Accuracy Metric
    
    Evaluates classification performance using standard metrics:
    - Accuracy: Overall correctness
    - Precision: True positives / (True positives + False positives)
    - Recall: True positives / (True positives + False negatives)
    - F1-Score: Harmonic mean of precision and recall
    """
    
    def __init__(self):
        super().__init__("classification")
        self.timeout_seconds = 30  # Classification is typically fast
        
        logger.info("✅ Classification Accuracy Metric initialized")
    
    def _validate_input(self, data: EvaluationData):
        """Validate input data for classification"""
        super()._validate_input(data)
        
        if not data.answer.strip():
            raise ValueError("Predicted label (answer) is required for classification")
            
        if not data.expected_answer.strip():
            raise ValueError("Actual label (expected_answer) is required for classification")
    
    async def _calculate_metric(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Calculate classification accuracy"""
        try:
            logger.info("🔍 Calculating classification accuracy")
            
            predicted_label = data.answer.strip().lower()
            actual_label = data.expected_answer.strip().lower()
            
            # Simple accuracy calculation
            is_correct = predicted_label == actual_label
            accuracy = 1.0 if is_correct else 0.0
            
            logger.info("📊 Classification accuracy calculated", 
                       predicted=predicted_label,
                       actual=actual_label,
                       accuracy=accuracy)
            
            return accuracy
            
        except Exception as e:
            logger.error("💥 Classification accuracy calculation failed", error=str(e))
            raise

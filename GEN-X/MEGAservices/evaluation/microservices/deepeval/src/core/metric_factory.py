"""
Metric Factory - Creates and manages all metric instances
"""
import asyncio
from typing import Dict, Any, Protocol
import structlog

from models import EvaluationData, MetricResult, AvailableMetrics
from config import get_settings

logger = structlog.get_logger()


class MetricInterface(Protocol):
    """Interface that all metrics must implement"""
    
    async def calculate(self, data: EvaluationData, config: Dict[str, Any]) -> MetricResult:
        """Calculate metric score"""
        ...


class MetricFactory:
    """Factory for creating metric instances"""
    
    def __init__(self):
        self.settings = get_settings()
        self._metrics_cache: Dict[str, MetricInterface] = {}
        logger.info("🏭 Metric factory initialized")
    
    def create_metric(self, metric_name: str) -> MetricInterface:
        """Create or get cached metric instance"""
        if metric_name in self._metrics_cache:
            return self._metrics_cache[metric_name]
        
        # Import metric classes dynamically to avoid circular imports
        if metric_name == "answer_relevancy":
            from backends.rag_metrics.answer_relevancy import AnswerRelevancyMetric
            metric = AnswerRelevancyMetric()
        elif metric_name == "faithfulness":
            from backends.rag_metrics.faithfulness import FaithfulnessMetric
            metric = FaithfulnessMetric()
        elif metric_name == "contextual_precision":
            from backends.rag_metrics.contextual_precision import ContextualPrecisionMetric
            metric = ContextualPrecisionMetric()
        elif metric_name == "contextual_recall":
            from backends.rag_metrics.contextual_recall import ContextualRecallMetric
            metric = ContextualRecallMetric()
        elif metric_name == "contextual_relevancy":
            from backends.rag_metrics.contextual_relevancy import ContextualRelevancyMetric
            metric = ContextualRelevancyMetric()
        elif metric_name == "bias":
            from backends.safety_ethics.bias import BiasMetric
            metric = BiasMetric()
        elif metric_name == "toxicity":
            from backends.safety_ethics.toxicity import ToxicityMetric
            metric = ToxicityMetric()
        elif metric_name == "hallucination":
            from backends.safety_ethics.hallucination import HallucinationMetric
            metric = HallucinationMetric()
        elif metric_name == "summarization":
            from backends.task_specific.summarization import SummarizationMetric
            metric = SummarizationMetric()
        elif metric_name == "geval":
            from backends.custom_metrics.geval import GEvalMetric
            metric = GEvalMetric()
        else:
            raise ValueError(f"Unknown metric: {metric_name}")
        
        # Cache the metric instance
        self._metrics_cache[metric_name] = metric
        logger.info("🔧 Created metric instance", metric_name=metric_name)
        
        return metric
    
    def get_available_metrics(self) -> AvailableMetrics:
        """Get list of all available metrics"""
        return AvailableMetrics()
    
    async def health_check(self) -> bool:
        """Check if metric factory is healthy"""
        try:
            # Try to create a simple metric
            metric = self.create_metric("answer_relevancy")
            return True
        except Exception as e:
            logger.error("💥 Metric factory health check failed", error=str(e))
            return False

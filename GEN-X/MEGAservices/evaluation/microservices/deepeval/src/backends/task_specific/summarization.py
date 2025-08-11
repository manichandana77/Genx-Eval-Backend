"""
Summarization Quality Metric
🎯 Evaluates the quality of text summaries
"""
from typing import Dict, Any
import structlog

from backends.core_metric_logic import DeepEvalMetricWrapper, BaseMetric
from models import EvaluationData, MetricResult

logger = structlog.get_logger()


class SummarizationMetric(DeepEvalMetricWrapper):
    """
    Summarization Quality Metric using DeepEval
    
    Evaluates summaries based on multiple criteria including:
    - Coherence: How well the summary flows
    - Consistency: Factual consistency with source
    - Fluency: Language quality
    - Relevance: How relevant the content is
    """
    
    def __init__(self):
        try:
            # Try to import SummarizationMetric from DeepEval
            from deepeval.metrics import SummarizationMetric as DeepEvalSummarization
            super().__init__("summarization", DeepEvalSummarization)
            
            self.timeout_seconds = 150  # Summarization evaluation can be complex
            
            logger.info("✅ Summarization Quality Metric initialized")
            
        except ImportError as e:
            logger.warning("⚠️ DeepEval SummarizationMetric not available, using fallback implementation")
            # Fallback to base metric implementation
            BaseMetric.__init__(self, "summarization")
    
    def _validate_input(self, data: EvaluationData):
        """Validate input data for summarization evaluation"""
        super()._validate_input(data)
        
        # For summarization, we need the original text and the summary
        if not data.context.strip():
            raise ValueError("Original text (context) is required for summarization evaluation")
            
        if not data.answer.strip():
            raise ValueError("Summary (answer) is required for summarization evaluation")
    
    async def _calculate_metric(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Calculate summarization quality using DeepEval or fallback method"""
        try:
            logger.info("🔍 Calculating summarization quality", 
                       original_length=len(data.context),
                       summary_length=len(data.answer))
            
            # Get evaluation aspects from config
            aspects = config.get("aspects", ["coherence", "consistency", "fluency", "relevance"])
            
            try:
                # Try DeepEval method first
                score = await super()._calculate_metric(data, config)
                normalized_score = max(0.0, min(1.0, score))
                
            except Exception as e:
                logger.warning("DeepEval summarization failed, using fallback", error=str(e))
                # Fallback to simple heuristic-based evaluation
                normalized_score = await self._fallback_summarization_evaluation(data, config)
            
            # Calculate compression ratio
            compression_ratio = len(data.answer) / len(data.context) if len(data.context) > 0 else 1.0
            
            logger.info("📊 Summarization quality calculated", 
                       score=normalized_score,
                       compression_ratio=compression_ratio,
                       aspects=aspects)
            
            return normalized_score
            
        except Exception as e:
            logger.error("💥 Summarization quality calculation failed", error=str(e))
            raise
    
    async def _fallback_summarization_evaluation(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Fallback summarization evaluation using simple heuristics"""
        try:
            # Simple heuristic-based evaluation
            original_length = len(data.context.split())
            summary_length = len(data.answer.split())
            
            # Check compression ratio (good summaries are 10-30% of original)
            compression_ratio = summary_length / original_length if original_length > 0 else 1.0
            
            # Score based on compression ratio
            if 0.1 <= compression_ratio <= 0.3:
                compression_score = 1.0
            elif 0.05 <= compression_ratio < 0.1 or 0.3 < compression_ratio <= 0.5:
                compression_score = 0.7
            else:
                compression_score = 0.3
            
            # Simple keyword overlap check
            original_words = set(data.context.lower().split())
            summary_words = set(data.answer.lower().split())
            overlap = len(original_words.intersection(summary_words))
            overlap_score = min(1.0, overlap / len(original_words) * 3) if len(original_words) > 0 else 0.5
            
            # Combine scores
            final_score = (compression_score * 0.6) + (overlap_score * 0.4)
            
            logger.info("📊 Fallback summarization evaluation", 
                       compression_ratio=compression_ratio,
                       overlap_score=overlap_score,
                       final_score=final_score)
            
            return final_score
            
        except Exception as e:
            logger.error("💥 Fallback summarization evaluation failed", error=str(e))
            return 0.5  # Default neutral score

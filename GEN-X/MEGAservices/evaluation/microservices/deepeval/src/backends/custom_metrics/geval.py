"""
GEval Custom Metric
🎯 Flexible metric using custom evaluation criteria
"""
from typing import Dict, Any, List
import structlog

from backends.core_metric_logic import DeepEvalMetricWrapper, BaseMetric
from models import EvaluationData, MetricResult

logger = structlog.get_logger()


class GEvalMetric(BaseMetric):
    """
    GEval Metric using DeepEval
    
    Allows custom evaluation criteria to be defined for specific use cases.
    Uses LLM-based evaluation with user-defined criteria and parameters.
    """
    
    def __init__(self):
        super().__init__("geval")
        self.timeout_seconds = 180  # GEval can take longer due to custom criteria
        
        logger.info("✅ GEval Custom Metric initialized")
    
    def _validate_input(self, data: EvaluationData):
        """Validate input data for GEval"""
        super()._validate_input(data)
        
        # GEval typically needs both input and output
        if not data.answer.strip():
            raise ValueError("Answer is required for GEval metric")
    
    async def _calculate_metric(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Calculate GEval score using custom criteria"""
        try:
            # Extract GEval configuration
            criteria = config.get("criteria", "Evaluate the quality of the response")
            evaluation_params = config.get("evaluation_params", ["ACTUAL_OUTPUT", "EXPECTED_OUTPUT"])
            geval_name = config.get("name", "CustomEvaluation")
            
            logger.info("🔍 Calculating GEval metric", 
                       criteria=criteria[:50],
                       name=geval_name,
                       params=evaluation_params)
            
            try:
                # Try to use DeepEval's GEval
                from deepeval.metrics import GEval
                from deepeval.test_case import LLMTestCaseParams, LLMTestCase
                
                # Map string params to enum values
                param_mapping = {
                    "ACTUAL_OUTPUT": LLMTestCaseParams.ACTUAL_OUTPUT,
                    "EXPECTED_OUTPUT": LLMTestCaseParams.EXPECTED_OUTPUT,
                    "INPUT": LLMTestCaseParams.INPUT,
                    "CONTEXT": LLMTestCaseParams.CONTEXT
                }
                
                enum_params = [param_mapping.get(p, LLMTestCaseParams.ACTUAL_OUTPUT) for p in evaluation_params]
                
                # Create GEval metric
                geval = GEval(
                    name=geval_name,
                    criteria=criteria,
                    evaluation_params=enum_params
                )
                
                # Create test case
                test_case = LLMTestCase(
                    input=data.question,
                    actual_output=data.answer,
                    expected_output=data.expected_answer,
                    context=data.context
                )
                
                # Calculate metric
                await geval.a_measure(test_case)
                score = geval.score
                
                normalized_score = max(0.0, min(1.0, score))
                
                logger.info("📊 GEval metric calculated using DeepEval", 
                           score=normalized_score,
                           name=geval_name)
                
                return normalized_score
                
            except Exception as e:
                logger.warning("DeepEval GEval failed, using fallback", error=str(e))
                # Fallback to simple evaluation
                return await self._fallback_geval(data, config)
                
        except Exception as e:
            logger.error("💥 GEval metric calculation failed", error=str(e))
            raise
    
    async def _fallback_geval(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Fallback GEval implementation using simple heuristics"""
        try:
            criteria = config.get("criteria", "").lower()
            
            # Simple heuristic based on criteria keywords
            score = 0.5  # Default neutral score
            
            # Check for quality-related keywords in criteria
            if any(keyword in criteria for keyword in ["quality", "good", "accurate"]):
                # Simple quality check based on length and completeness
                if len(data.answer.strip()) > 50 and data.answer.strip().endswith(('.', '!', '?')):
                    score = 0.8
                else:
                    score = 0.6
            
            elif any(keyword in criteria for keyword in ["relevant", "related"]):
                # Simple relevance check
                if data.question and data.answer:
                    question_words = set(data.question.lower().split())
                    answer_words = set(data.answer.lower().split())
                    overlap = len(question_words.intersection(answer_words))
                    score = min(1.0, overlap / len(question_words) * 2) if len(question_words) > 0 else 0.5
            
            elif any(keyword in criteria for keyword in ["complete", "comprehensive"]):
                # Completeness check based on length
                answer_length = len(data.answer.split())
                if answer_length > 100:
                    score = 0.9
                elif answer_length > 50:
                    score = 0.7
                else:
                    score = 0.5
            
            logger.info("📊 Fallback GEval evaluation", 
                       score=score,
                       criteria_type="heuristic")
            
            return score
            
        except Exception as e:
            logger.error("💥 Fallback GEval evaluation failed", error=str(e))
            return 0.5

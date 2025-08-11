"""
Base Metric Class - Common functionality for all metrics
"""
import time
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any

import structlog

from models import EvaluationData, MetricResult

logger = structlog.get_logger()


class BaseMetric(ABC):
    """Base class for all metrics"""
    
    def __init__(self, metric_name: str):
        self.metric_name = metric_name
        self.timeout_seconds = 60  # Default timeout
    
    async def calculate(self, data: EvaluationData, config: Dict[str, Any]) -> MetricResult:
        """Calculate metric with error handling and timing"""
        start_time = time.time()
        
        try:
            logger.info("🔬 Starting metric calculation", metric=self.metric_name)
            
            # Validate input data
            self._validate_input(data)
            
            # Calculate metric with timeout
            score = await asyncio.wait_for(
                self._calculate_metric(data, config),
                timeout=self.timeout_seconds
            )
            
            execution_time = (time.time() - start_time) * 1000  # ms
            
            logger.info("✅ Metric calculation complete", 
                       metric=self.metric_name, 
                       score=score,
                       execution_time_ms=execution_time)
            
            return MetricResult(
                metric_name=self.metric_name,
                score=score,
                success=True,
                execution_time_ms=execution_time,
                metadata={"calculation_method": self.__class__.__name__}
            )
            
        except asyncio.TimeoutError:
            error_msg = f"Metric calculation timed out after {self.timeout_seconds}s"
            logger.error("⏰ Metric timeout", metric=self.metric_name)
            
            return MetricResult(
                metric_name=self.metric_name,
                score=0.0,
                success=False,
                error_message=error_msg,
                execution_time_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            error_msg = f"Metric calculation failed: {str(e)}"
            logger.error("💥 Metric calculation failed", 
                        metric=self.metric_name, 
                        error=str(e))
            
            return MetricResult(
                metric_name=self.metric_name,
                score=0.0,
                success=False,
                error_message=error_msg,
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    def _validate_input(self, data: EvaluationData):
        """Validate input data (override in subclasses)"""
        if not data.question.strip():
            raise ValueError("Question cannot be empty")
        if not data.answer.strip():
            raise ValueError("Answer cannot be empty")
    
    @abstractmethod
    async def _calculate_metric(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Implement actual metric calculation logic"""
        pass


class DeepEvalMetricWrapper(BaseMetric):
    """Wrapper for DeepEval library metrics"""
    
    def __init__(self, metric_name: str, deepeval_metric_class):
        super().__init__(metric_name)
        self.deepeval_metric = deepeval_metric_class()
    
    async def _calculate_metric(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Use DeepEval library to calculate metric"""
        try:
            # Import DeepEval components
            from deepeval.test_case import LLMTestCase
            
            # Create test case for DeepEval
            test_case = LLMTestCase(
                input=data.question,
                actual_output=data.answer,
                expected_output=data.expected_answer,
                context=data.context
            )
            
            # Calculate metric asynchronously
            await self.deepeval_metric.a_measure(test_case)
            
            # Return score
            return float(self.deepeval_metric.score)
            
        except ImportError as e:
            logger.error("💥 DeepEval import failed", error=str(e))
            raise Exception("DeepEval library not available")
        except Exception as e:
            logger.error("💥 DeepEval metric failed", metric=self.metric_name, error=str(e))
            raise

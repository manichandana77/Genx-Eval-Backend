"""Backends Package - All Metric Classes"""

# RAG Metrics
from .rag_metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric, 
    ContextualRecallMetric,
    ContextualRelevancyMetric
)

# Safety & Ethics Metrics
from .safety_ethics import (
    BiasMetric,
    ToxicityMetric,
    HallucinationMetric
)

# Task-Specific Metrics
from .task_specific import (
    SummarizationMetric,
    ClassificationMetric,
    GenerationMetric
)

# Custom Metrics
from .custom_metrics import (
    GEvalMetric,
    CustomDomainMetric
)

__all__ = [
    # RAG Metrics
    "AnswerRelevancyMetric",
    "FaithfulnessMetric",
    "ContextualPrecisionMetric", 
    "ContextualRecallMetric",
    "ContextualRelevancyMetric",
    
    # Safety & Ethics
    "BiasMetric",
    "ToxicityMetric",
    "HallucinationMetric",
    
    # Task-Specific
    "SummarizationMetric",
    "ClassificationMetric", 
    "GenerationMetric",
    
    # Custom
    "GEvalMetric",
    "CustomDomainMetric"
]

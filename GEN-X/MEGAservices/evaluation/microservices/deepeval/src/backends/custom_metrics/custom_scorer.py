"""
Custom Domain-Specific Metric
🎯 Template for creating domain-specific evaluation metrics
"""
from typing import Dict, Any
import structlog

from backends.core_metric_logic import BaseMetric
from models import EvaluationData, MetricResult

logger = structlog.get_logger()


class CustomDomainMetric(BaseMetric):
    """
    Custom Domain-Specific Metric
    
    Template for creating specialized metrics for specific domains or use cases.
    Can be extended for medical, legal, financial, or other domain-specific evaluations.
    """
    
    def __init__(self, domain_name: str = "custom"):
        super().__init__(f"custom_{domain_name}")
        self.domain = domain_name
        self.timeout_seconds = 120
        
        logger.info("✅ Custom Domain Metric initialized", domain=domain_name)
    
    def _validate_input(self, data: EvaluationData):
        """Validate input data for custom metric"""
        super()._validate_input(data)
        
        # Add domain-specific validation here
        if not data.answer.strip():
            raise ValueError(f"Answer is required for {self.domain} metric")
    
    async def _calculate_metric(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Calculate custom domain metric"""
        try:
            domain_type = config.get("domain_type", self.domain)
            evaluation_criteria = config.get("criteria", [])
            
            logger.info("🔍 Calculating custom domain metric", 
                       domain=domain_type,
                       criteria=evaluation_criteria)
            
            # Implement domain-specific logic here
            score = await self._evaluate_domain_specific(data, config)
            
            normalized_score = max(0.0, min(1.0, score))
            
            logger.info("📊 Custom domain metric calculated", 
                       domain=domain_type,
                       score=normalized_score)
            
            return normalized_score
            
        except Exception as e:
            logger.error("💥 Custom domain metric calculation failed", error=str(e))
            raise
    
    async def _evaluate_domain_specific(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """
        Implement domain-specific evaluation logic here
        
        Examples:
        - Medical: Check for medical accuracy, proper terminology
        - Legal: Check for legal accuracy, proper citations
        - Financial: Check for financial accuracy, compliance
        - Technical: Check for technical accuracy, best practices
        """
        
        domain_type = config.get("domain_type", "general")
        
        if domain_type == "medical":
            return await self._evaluate_medical(data, config)
        elif domain_type == "legal":
            return await self._evaluate_legal(data, config)
        elif domain_type == "financial":
            return await self._evaluate_financial(data, config)
        elif domain_type == "technical":
            return await self._evaluate_technical(data, config)
        else:
            return await self._evaluate_general(data, config)
    
    async def _evaluate_medical(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Medical domain evaluation"""
        # Placeholder for medical-specific evaluation
        # Could check for medical terminology accuracy, safety guidelines, etc.
        
        medical_terms = config.get("medical_terms", [])
        answer_lower = data.answer.lower()
        
        # Simple check for presence of expected medical terms
        if medical_terms:
            found_terms = sum(1 for term in medical_terms if term.lower() in answer_lower)
            score = found_terms / len(medical_terms)
        else:
            score = 0.7  # Default score if no specific terms to check
        
        return score
    
    async def _evaluate_legal(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Legal domain evaluation"""
        # Placeholder for legal-specific evaluation
        # Could check for legal citations, proper legal language, etc.
        
        legal_keywords = ["statute", "case", "precedent", "law", "regulation", "court"]
        answer_lower = data.answer.lower()
        
        found_keywords = sum(1 for keyword in legal_keywords if keyword in answer_lower)
        score = min(1.0, found_keywords / 3)  # Normalize based on expectation of 3+ legal terms
        
        return score
    
    async def _evaluate_financial(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Financial domain evaluation"""
        # Placeholder for financial-specific evaluation
        # Could check for financial accuracy, compliance statements, etc.
        
        financial_keywords = ["investment", "risk", "return", "portfolio", "market", "financial"]
        answer_lower = data.answer.lower()
        
        found_keywords = sum(1 for keyword in financial_keywords if keyword in answer_lower)
        score = min(1.0, found_keywords / 3)
        
        return score
    
    async def _evaluate_technical(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Technical domain evaluation"""
        # Placeholder for technical-specific evaluation
        # Could check for technical accuracy, proper terminology, etc.
        
        # Simple check for code blocks, technical terms, etc.
        answer = data.answer
        technical_indicators = [
            "`" in answer,  # Code blocks
            any(keyword in answer.lower() for keyword in ["algorithm", "function", "method", "class"]),
            len(answer.split()) > 50  # Detailed technical explanation
        ]
        
        score = sum(technical_indicators) / len(technical_indicators)
        return score
    
    async def _evaluate_general(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """General domain evaluation"""
        # Default evaluation for general use cases
        
        # Simple quality heuristic
        answer = data.answer.strip()
        
        quality_indicators = [
            len(answer) > 20,  # Reasonable length
            answer.endswith(('.', '!', '?')),  # Proper ending
            len(answer.split()) > 5,  # Multiple words
            not answer.isupper(),  # Not all caps (shouting)
        ]
        
        score = sum(quality_indicators) / len(quality_indicators)
        return score

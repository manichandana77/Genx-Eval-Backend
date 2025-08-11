"""
Text Generation Quality Metric
🎯 Evaluates the quality of generated text
"""
from typing import Dict, Any
import structlog

from backends.core_metric_logic import BaseMetric
from models import EvaluationData, MetricResult

logger = structlog.get_logger()


class GenerationMetric(BaseMetric):
    """
    Text Generation Quality Metric
    
    Evaluates generated text based on multiple quality aspects:
    - Fluency: How natural and readable the text is
    - Coherence: Logical flow and consistency
    - Relevance: How well it addresses the prompt
    - Creativity: Novel and interesting content (when applicable)
    """
    
    def __init__(self):
        super().__init__("generation")
        self.timeout_seconds = 60
        
        logger.info("✅ Text Generation Quality Metric initialized")
    
    def _validate_input(self, data: EvaluationData):
        """Validate input data for generation quality"""
        super()._validate_input(data)
        
        if not data.answer.strip():
            raise ValueError("Generated text (answer) is required for generation quality evaluation")
    
    async def _calculate_metric(self, data: EvaluationData, config: Dict[str, Any]) -> float:
        """Calculate text generation quality using heuristic methods"""
        try:
            logger.info("🔍 Calculating text generation quality", 
                       text_length=len(data.answer))
            
            generated_text = data.answer.strip()
            prompt = data.question.strip()
            reference = data.expected_answer.strip() if data.expected_answer else ""
            
            # Quality aspects from config
            aspects = config.get("aspects", ["fluency", "coherence", "relevance"])
            
            scores = {}
            
            # Basic fluency check (sentence structure, length)
            if "fluency" in aspects:
                scores["fluency"] = self._calculate_fluency(generated_text)
            
            # Basic coherence check (repetition, structure)
            if "coherence" in aspects:
                scores["coherence"] = self._calculate_coherence(generated_text)
            
            # Relevance to prompt
            if "relevance" in aspects and prompt:
                scores["relevance"] = self._calculate_relevance(generated_text, prompt)
            
            # Creativity (vocabulary diversity)
            if "creativity" in aspects:
                scores["creativity"] = self._calculate_creativity(generated_text)
            
            # Average the scores
            if scores:
                final_score = sum(scores.values()) / len(scores)
            else:
                final_score = 0.5  # Default neutral score
            
            logger.info("📊 Text generation quality calculated", 
                       final_score=final_score,
                       aspect_scores=scores)
            
            return final_score
            
        except Exception as e:
            logger.error("💥 Text generation quality calculation failed", error=str(e))
            raise
    
    def _calculate_fluency(self, text: str) -> float:
        """Simple fluency heuristic"""
        words = text.split()
        sentences = text.split('.')
        
        # Check for reasonable sentence length
        avg_words_per_sentence = len(words) / len(sentences) if len(sentences) > 0 else 0
        
        # Good range is 10-25 words per sentence
        if 10 <= avg_words_per_sentence <= 25:
            fluency_score = 1.0
        elif 5 <= avg_words_per_sentence < 10 or 25 < avg_words_per_sentence <= 35:
            fluency_score = 0.7
        else:
            fluency_score = 0.4
        
        return fluency_score
    
    def _calculate_coherence(self, text: str) -> float:
        """Simple coherence heuristic"""
        words = text.split()
        unique_words = set(words)
        
        # Check for excessive repetition
        repetition_ratio = len(words) / len(unique_words) if len(unique_words) > 0 else 1
        
        if repetition_ratio <= 1.5:
            coherence_score = 1.0
        elif repetition_ratio <= 2.0:
            coherence_score = 0.7
        else:
            coherence_score = 0.4
        
        return coherence_score
    
    def _calculate_relevance(self, text: str, prompt: str) -> float:
        """Simple relevance heuristic"""
        text_words = set(text.lower().split())
        prompt_words = set(prompt.lower().split())
        
        # Calculate word overlap
        overlap = len(text_words.intersection(prompt_words))
        relevance_score = min(1.0, overlap / len(prompt_words) * 2) if len(prompt_words) > 0 else 0.5
        
        return relevance_score
    
    def _calculate_creativity(self, text: str) -> float:
        """Simple creativity heuristic (vocabulary diversity)"""
        words = text.split()
        unique_words = set(words)
        
        # Vocabulary diversity
        diversity_ratio = len(unique_words) / len(words) if len(words) > 0 else 0
        
        # Higher diversity typically indicates more creativity
        creativity_score = min(1.0, diversity_ratio * 1.5)
        
        return creativity_score

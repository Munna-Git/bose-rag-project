"""
Confidence scoring for RAG responses
Provides reliability indicators to users
"""
from typing import Dict, Any, List, Optional
import re

from langchain_core.documents import Document
from src.error_handling.logger import logger


class ConfidenceScorer:
    """
    Calculate confidence scores for RAG answers
    
    Factors considered:
    1. Retrieval quality (similarity scores)
    2. Answer grounding (content from sources)
    3. Technical specificity (numbers, units, models)
    4. Uncertainty indicators in answer
    
    Score ranges:
    - 0.85-1.0: High confidence (reliable answer)
    - 0.70-0.85: Medium confidence (good but verify)
    - 0.50-0.70: Low confidence (uncertain, may need review)
    - 0.0-0.50: Very low confidence (unreliable, insufficient info)
    """
    
    def __init__(self, enable_scoring: bool = True):
        """
        Initialize confidence scorer
        
        Args:
            enable_scoring: If False, always returns neutral confidence
        """
        self.enable_scoring = enable_scoring
        
        if enable_scoring:
            logger.info("Confidence scorer initialized")
        else:
            logger.info("Confidence scoring disabled")
    
    def calculate_confidence(
        self,
        query: str,
        answer: str,
        retrieved_docs: List[Document],
        retrieval_scores: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive confidence score
        
        Args:
            query: User query
            answer: Generated answer
            retrieved_docs: Documents used for answer
            retrieval_scores: Similarity scores from retrieval
        
        Returns:
            Dict with overall score, breakdown, and explanation
        """
        if not self.enable_scoring:
            return {
                'overall': 0.75,
                'label': 'medium',
                'enabled': False
            }
        
        # Component scores (0-1)
        scores = {
            'retrieval': self._score_retrieval(retrieved_docs, retrieval_scores),
            'grounding': self._score_answer_grounding(answer, retrieved_docs),
            'specificity': self._score_specificity(answer),
            'uncertainty': self._score_uncertainty(answer)
        }
        
        # Weighted combination - prioritize grounding and retrieval
        weights = {
            'retrieval': 0.40,      # Quality of source documents
            'grounding': 0.35,      # Answer backed by retrieved content
            'specificity': 0.15,    # Concrete technical details
            'uncertainty': 0.10     # Explicit hedging
        }
        
        overall = sum(scores[k] * weights[k] for k in scores.keys())
        overall = max(0.0, min(1.0, overall))  # Clamp to [0, 1]
        
        # Label and explanation
        label = self._get_confidence_label(overall)
        explanation = self._generate_explanation(overall, scores)
        
        return {
            'overall': round(overall, 3),
            'label': label,
            'breakdown': {k: round(v, 3) for k, v in scores.items()},
            'explanation': explanation,
            'enabled': True
        }
    
    def _score_retrieval(
        self, 
        docs: List[Document], 
        scores: Optional[List[float]]
    ) -> float:
        """Score based on retrieval quality - if we found documents, assume they're relevant"""
        if not docs:
            return 0.0
        
        # If we have similarity scores, use them directly
        if scores and len(scores) > 0:
            # Take the best score (top retrieved document)
            top_score = max(scores)
            # If top doc has high similarity, we have strong evidence
            if top_score > 0.7:
                return 0.95
            elif top_score > 0.5:
                return 0.85
            elif top_score > 0.3:
                return 0.75
            else:
                return 0.65
        
        # Fallback: if retrieval returned documents, assume they matched
        # The fact that ChromaDB/BM25 returned these means they're relevant
        doc_count = len(docs)
        if doc_count >= 3:
            return 0.90  # Multiple sources = high confidence
        elif doc_count == 2:
            return 0.85  # Two sources = good confidence
        else:
            return 0.80  # One source can still be definitive
    
    def _score_answer_grounding(self, answer: str, docs: List[Document]) -> float:
        """
        Score how well the answer is grounded in retrieved documents
        High score = answer content appears in source docs
        """
        if not docs or not answer:
            return 0.5
        
        # Extract meaningful terms from answer (4+ chars, not common words)
        answer_lower = answer.lower()
        answer_terms = set(re.findall(r'\b\w{4,}\b', answer_lower))
        
        # Remove very common words
        common_words = {'that', 'this', 'with', 'from', 'have', 'been', 'were', 
                       'their', 'there', 'which', 'would', 'could', 'should', 
                       'about', 'when', 'what', 'where', 'your', 'does', 'only'}
        answer_terms = answer_terms - common_words
        
        if not answer_terms:
            return 0.7  # Answer too short to judge, assume reasonable
        
        # Count how many answer terms appear in source documents
        doc_text = ' '.join([doc.page_content.lower() for doc in docs])
        
        matched_terms = sum(1 for term in answer_terms if term in doc_text)
        match_ratio = matched_terms / len(answer_terms)
        
        # High grounding = high confidence
        if match_ratio > 0.7:
            return 0.95  # Most answer content from sources
        elif match_ratio > 0.5:
            return 0.85  # Good grounding
        elif match_ratio > 0.3:
            return 0.75  # Reasonable grounding
        else:
            return 0.60  # Lower grounding but could still be correct paraphrasing
    
    def _score_specificity(self, answer: str) -> float:
        """
        Score based on technical specificity
        Specific numbers, units, model names = high confidence
        """
        if not answer or len(answer.strip()) < 10:
            return 0.3
        
        score = 0.5  # Base score
        
        # Technical specifications with units
        tech_patterns = [
            r'\d+\s*(hz|khz|mhz|ghz)',  # Frequency
            r'\d+\s*(db|dba|dbc)',       # Decibels
            r'\d+\s*(ohm|Ω)',            # Impedance
            r'\d+\s*(watt|w|kw)',        # Power
            r'\d+\s*(volt|v|mv)',        # Voltage
            r'\d+\s*(amp|a|ma)',         # Current
            r'\d+\s*(meter|m|cm|mm|feet|ft|inch|in)',  # Distance
            r'\d+\s*(channel|ch)',       # Channels
            r'\d+\s*(bit|kbps|mbps)',   # Data rate
        ]
        
        spec_count = sum(1 for pattern in tech_patterns 
                        if re.search(pattern, answer.lower()))
        
        # More specs = higher confidence (technical details suggest grounded answer)
        if spec_count >= 3:
            score = 0.95
        elif spec_count >= 2:
            score = 0.90
        elif spec_count >= 1:
            score = 0.85
        else:
            # Check for model numbers or specific product names
            has_model = bool(re.search(r'[A-Z]{2,}\d+|[A-Z]+-\d+', answer))
            if has_model:
                score = 0.80
        
        return score
    
    def _score_uncertainty(self, answer: str) -> float:
        """Score based on uncertainty markers - only penalize explicit admissions of not knowing"""
        answer_lower = answer.lower()
        
        # Severe uncertainty (definite lack of knowledge)
        severe_phrases = ["i don't know", "i cannot find", "no information available", 
                         "not mentioned in", "insufficient information"]
        has_severe = any(phrase in answer_lower for phrase in severe_phrases)
        if has_severe:
            return 0.3  # Low confidence if admitting lack of knowledge
        
        # Mild hedging (being cautious, not necessarily uncertain)
        mild_phrases = ["may be", "might be", "possibly", "perhaps", "could be"]
        mild_count = sum(1 for phrase in mild_phrases if phrase in answer_lower)
        
        if mild_count == 0:
            return 1.0  # No hedging = full confidence
        elif mild_count == 1:
            return 0.90  # Slight hedging is just being precise
        else:
            return 0.80  # Multiple hedges = somewhat uncertain
    
    def _get_confidence_label(self, score: float) -> str:
        """Convert numeric score to label"""
        if score >= 0.85:
            return "high"
        elif score >= 0.70:
            return "medium"
        elif score >= 0.50:
            return "low"
        else:
            return "very_low"
    
    def _generate_explanation(self, overall: float, breakdown: Dict[str, float]) -> str:
        """Generate human-readable explanation"""
        if overall >= 0.85:
            return "High confidence. Answer is well-grounded in source documents with specific technical details."
        elif overall >= 0.70:
            return "Medium confidence. Answer appears accurate but verify critical specifications."
        elif overall >= 0.50:
            return "Low confidence. Answer may be incomplete or lack supporting details."
        else:
            return "Very low confidence. Limited information found. Consider rephrasing your question."
    
    def get_recommendation(self, confidence: Dict[str, Any]) -> str:
        """Get user-facing recommendation based on confidence"""
        if not confidence.get('enabled', False):
            return ""
        
        score = confidence['overall']
        
        if score >= 0.85:
            return "✓ This answer is reliable and well-supported by documentation."
        elif score >= 0.70:
            return "⚠ This answer appears accurate but verify critical specifications."
        elif score >= 0.50:
            return "⚠ Information may be incomplete. Consider checking source documents."
        else:
            return "✗ Limited information found. Try rephrasing your question or check if relevant documents are available."


class ConfidenceManager:
    """
    Singleton confidence scorer manager
    """
    
    _instance: Optional['ConfidenceManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.scorer: Optional[ConfidenceScorer] = None
        self._initialized = True
    
    def initialize(self, enable_scoring: bool = True):
        """Initialize the confidence scorer"""
        self.scorer = ConfidenceScorer(enable_scoring=enable_scoring)
    
    def get_scorer(self) -> ConfidenceScorer:
        """Get the confidence scorer instance"""
        if self.scorer is None:
            # Initialize with defaults if not done yet
            self.initialize()
        return self.scorer


# Global confidence manager instance
confidence_manager = ConfidenceManager()

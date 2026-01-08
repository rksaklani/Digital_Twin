"""
Facial expression system.
Rule-based expression mapping from emotion and intent.
"""

import logging
from typing import Dict, Any, Optional
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExpressionSystem:
    """Manages facial expressions"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.current_expression = 'neutral'
        self.expression_map = self._create_expression_map()
    
    def _create_expression_map(self) -> Dict[str, Dict[str, float]]:
        """Create mapping from emotion to facial expression parameters"""
        # Simplified expression parameters
        # In production, this would map to actual facial animation parameters
        return {
            'neutral': {
                'mouth_open': 0.0,
                'eyebrow_raise': 0.0,
                'eye_open': 1.0,
                'smile': 0.0,
            },
            'positive': {
                'mouth_open': 0.2,
                'eyebrow_raise': 0.1,
                'eye_open': 1.0,
                'smile': 0.6,
            },
            'negative': {
                'mouth_open': 0.1,
                'eyebrow_raise': -0.1,
                'eye_open': 0.8,
                'smile': -0.3,
            },
            'question': {
                'mouth_open': 0.3,
                'eyebrow_raise': 0.3,
                'eye_open': 1.0,
                'smile': 0.1,
            },
            'excited': {
                'mouth_open': 0.4,
                'eyebrow_raise': 0.4,
                'eye_open': 1.2,
                'smile': 0.8,
            },
        }
    
    def get_expression(self, emotion: Optional[str], intent: Optional[str]) -> Dict[str, float]:
        """Get expression parameters based on emotion and intent"""
        # Determine base expression from emotion
        base_emotion = emotion or 'neutral'
        
        # Override with intent-specific expressions
        if intent == 'question':
            base_emotion = 'question'
        
        expression = self.expression_map.get(base_emotion, self.expression_map['neutral']).copy()
        self.current_expression = base_emotion
        
        return expression
    
    def blend_expressions(self, expr1: Dict[str, float], expr2: Dict[str, float], blend_factor: float) -> Dict[str, float]:
        """Blend two expressions"""
        blended = {}
        for key in expr1:
            if key in expr2:
                blended[key] = expr1[key] * (1 - blend_factor) + expr2[key] * blend_factor
            else:
                blended[key] = expr1[key]
        return blended
    
    def get_micro_expression(self) -> Dict[str, float]:
        """Get subtle micro-expression variation"""
        import random
        base = self.expression_map.get(self.current_expression, self.expression_map['neutral'])
        micro = {}
        for key, value in base.items():
            # Add small random variation
            variation = random.uniform(-0.05, 0.05)
            micro[key] = max(0.0, min(1.0, value + variation))
        return micro


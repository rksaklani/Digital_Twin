"""
Response planner for LLM.
Controls response structure, length, and style.
"""

import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResponsePlanner:
    """Plans and structures LLM responses"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_length = config.get('max_length', 200)
        self.min_length = config.get('min_length', 10)
    
    def plan_response(self, user_input: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Plan response structure based on intent"""
        intent_type = intent.get('intent', 'statement')
        emotion = intent.get('emotion', 'neutral')
        
        plan = {
            'style': 'conversational',
            'length': 'medium',
            'tone': emotion,
            'structure': 'simple',
        }
        
        # Adjust based on intent
        if intent_type == 'question':
            plan['structure'] = 'answer'
            plan['length'] = 'medium'
        elif intent_type == 'command':
            plan['structure'] = 'acknowledgment'
            plan['length'] = 'short'
        else:
            plan['structure'] = 'response'
            plan['length'] = 'medium'
        
        # Adjust based on emotion
        if emotion == 'positive':
            plan['tone'] = 'friendly'
        elif emotion == 'negative':
            plan['tone'] = 'empathetic'
        
        return plan
    
    def estimate_length(self, plan: Dict[str, Any]) -> int:
        """Estimate response length in tokens"""
        length_map = {
            'short': 50,
            'medium': 150,
            'long': 300,
        }
        return length_map.get(plan.get('length', 'medium'), 150)
    
    def validate_response(self, response: str, plan: Dict[str, Any]) -> bool:
        """Validate response matches plan"""
        # Simple validation
        if len(response) < self.min_length:
            return False
        if len(response) > self.max_length * 2:  # Allow some flexibility
            return False
        return True


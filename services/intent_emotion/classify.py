"""
Intent and emotion classification service.
Uses lightweight models for fast classification.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
import yaml
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentEmotionClassifier:
    """Classifies intent and emotion from text"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('models', {}).get('intent_emotion', {})
        self.model = None
        self.tokenizer = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, Any]:
        """Load rules from YAML file"""
        rules_path = Path(__file__).parent / 'rules.yaml'
        if rules_path.exists():
            with open(rules_path, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    async def initialize(self):
        """Initialize classification model"""
        logger.info("Initializing intent/emotion classifier...")
        
        model_name = self.config.get('model_name', 'distilbert-base-uncased-finetuned-sst-2-english')
        device = self.config.get('device', self.device)
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(device)
            self.model.eval()
            logger.info(f"Intent/emotion model loaded: {model_name} on {device}")
        except Exception as e:
            logger.error(f"Failed to load classification model: {e}")
            # Continue without model - will use rule-based only
            logger.warning("Using rule-based classification only")
    
    async def classify(self, text: str) -> Dict[str, Any]:
        """Classify intent and emotion from text"""
        result = {
            'intent': 'statement',
            'emotion': 'neutral',
            'confidence': 0.5,
            'keywords': [],
        }
        
        # Rule-based classification first
        rule_result = self._rule_based_classify(text)
        if rule_result:
            result.update(rule_result)
        
        # Model-based classification if available
        if self.model and self.tokenizer:
            model_result = await self._model_classify(text)
            if model_result:
                # Merge results (model takes precedence for emotion)
                result['emotion'] = model_result.get('emotion', result['emotion'])
                result['confidence'] = model_result.get('confidence', result['confidence'])
        
        return result
    
    def _rule_based_classify(self, text: str) -> Optional[Dict[str, Any]]:
        """Rule-based classification"""
        text_lower = text.lower()
        
        # Intent detection
        intent = 'statement'
        if any(word in text_lower for word in ['?', 'what', 'how', 'why', 'when', 'where', 'who']):
            intent = 'question'
        elif any(word in text_lower for word in ['please', 'can you', 'could you', 'would you']):
            intent = 'command'
        
        # Emotion detection (simple keyword matching)
        emotion = 'neutral'
        positive_words = ['happy', 'good', 'great', 'excellent', 'love', 'like', 'thanks']
        negative_words = ['sad', 'bad', 'hate', 'angry', 'frustrated', 'disappointed']
        
        if any(word in text_lower for word in positive_words):
            emotion = 'positive'
        elif any(word in text_lower for word in negative_words):
            emotion = 'negative'
        
        # Extract keywords
        keywords = []
        for word in text_lower.split():
            if len(word) > 4 and word not in ['that', 'this', 'with', 'from', 'have', 'been']:
                keywords.append(word)
        
        return {
            'intent': intent,
            'emotion': emotion,
            'keywords': keywords[:5],  # Top 5 keywords
        }
    
    async def _model_classify(self, text: str) -> Optional[Dict[str, Any]]:
        """Model-based classification"""
        if not self.model or not self.tokenizer:
            return None
        
        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors='pt',
                truncation=True,
                max_length=self.config.get('max_length', 128),
                padding=True,
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Run model
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
            
            # Get prediction
            predicted_class = torch.argmax(probabilities, dim=-1).item()
            confidence = probabilities[0][predicted_class].item()
            
            # Map to emotion (this is a simplified mapping - adjust based on your model)
            emotion_map = {0: 'negative', 1: 'positive'}
            emotion = emotion_map.get(predicted_class, 'neutral')
            
            return {
                'emotion': emotion,
                'confidence': confidence,
            }
        
        except Exception as e:
            logger.error(f"Error in model classification: {e}")
            return None
    
    async def shutdown(self):
        """Shutdown the classifier"""
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        logger.info("Intent/emotion classifier shutdown")


"""
Session memory for short-term conversation context.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Exchange:
    """A single conversation exchange"""
    user_input: str
    assistant_response: str
    timestamp: float
    intent: Optional[Dict[str, Any]] = None


class SessionMemory:
    """Manages short-term conversation memory"""
    
    def __init__(self, max_exchanges: int = 20):
        self.max_exchanges = max_exchanges
        self.exchanges: List[Exchange] = []
        self.session_start = datetime.now()
    
    def add_exchange(self, user_input: str, assistant_response: str, intent: Optional[Dict[str, Any]] = None):
        """Add a conversation exchange"""
        import time
        exchange = Exchange(
            user_input=user_input,
            assistant_response=assistant_response,
            timestamp=time.time(),
            intent=intent,
        )
        self.exchanges.append(exchange)
        
        # Keep only recent exchanges
        if len(self.exchanges) > self.max_exchanges:
            self.exchanges = self.exchanges[-self.max_exchanges:]
    
    def get_recent_history(self, max_turns: int = 5) -> str:
        """Get recent conversation history as formatted text"""
        if not self.exchanges:
            return ""
        
        recent = self.exchanges[-max_turns:]
        history_parts = []
        
        for exchange in recent:
            history_parts.append(f"User: {exchange.user_input}")
            history_parts.append(f"Assistant: {exchange.assistant_response}")
        
        return "\n".join(history_parts)
    
    def get_context(self) -> Dict[str, Any]:
        """Get full session context"""
        return {
            'exchanges': len(self.exchanges),
            'session_duration': (datetime.now() - self.session_start).total_seconds(),
            'recent_topics': self._extract_topics(),
        }
    
    def _extract_topics(self) -> List[str]:
        """Extract topics from recent exchanges"""
        # Simple keyword extraction
        topics = []
        for exchange in self.exchanges[-5:]:
            # Extract key words (simplified)
            words = exchange.user_input.lower().split()
            topics.extend([w for w in words if len(w) > 4][:3])
        return list(set(topics))[:5]
    
    def clear(self):
        """Clear all memory"""
        self.exchanges.clear()
        logger.info("Session memory cleared")


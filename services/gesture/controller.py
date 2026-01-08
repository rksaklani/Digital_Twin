"""
Gesture controller for head movements and micro-gestures.
Rule-based gesture generation based on intent and emotion.
"""

import asyncio
import logging
import random
from typing import Dict, Any, Optional
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GestureController:
    """Controls head gestures and micro-movements"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.current_gesture = None
        self.gesture_queue = asyncio.Queue()
        self.active_gestures = []
    
    def trigger_gesture(self, gesture_type: str, intensity: float = 1.0):
        """Trigger a gesture"""
        gesture = {
            'type': gesture_type,
            'intensity': intensity,
            'duration': self._get_gesture_duration(gesture_type),
            'start_time': asyncio.get_event_loop().time(),
        }
        self.gesture_queue.put_nowait(gesture)
        logger.debug(f"Gesture triggered: {gesture_type}")
    
    def _get_gesture_duration(self, gesture_type: str) -> float:
        """Get duration for a gesture type"""
        durations = {
            'nod': 0.5,
            'head_shake': 0.5,
            'head_tilt': 0.3,
            'eyebrow_raise': 0.2,
            'smile': 1.0,
        }
        return durations.get(gesture_type, 0.5)
    
    def get_gesture_for_intent(self, intent: str, emotion: Optional[str] = None) -> Optional[str]:
        """Get appropriate gesture for intent/emotion"""
        gesture_map = {
            'question': 'head_tilt',
            'command': 'nod',
            'positive': 'smile',
            'negative': 'head_shake',
        }
        
        # Check emotion first
        if emotion and emotion in gesture_map:
            return gesture_map[emotion]
        
        # Then check intent
        if intent in gesture_map:
            return gesture_map[intent]
        
        return None
    
    async def process_gestures(self, intent: Dict[str, Any]):
        """Process gestures based on intent"""
        intent_type = intent.get('intent', 'statement')
        emotion = intent.get('emotion', 'neutral')
        
        # Get appropriate gesture
        gesture_type = self.get_gesture_for_intent(intent_type, emotion)
        
        if gesture_type:
            # Randomly trigger gesture (not always, for naturalness)
            if random.random() < 0.7:  # 70% chance
                self.trigger_gesture(gesture_type)
    
    def get_current_gesture_state(self) -> Dict[str, Any]:
        """Get current gesture state"""
        current_time = asyncio.get_event_loop().time()
        
        # Update active gestures
        self.active_gestures = [
            g for g in self.active_gestures
            if (current_time - g['start_time']) < g['duration']
        ]
        
        if not self.active_gestures:
            return {
                'head_rotation': 0.0,
                'head_tilt': 0.0,
                'eyebrow_raise': 0.0,
            }
        
        # Combine active gestures
        state = {
            'head_rotation': 0.0,
            'head_tilt': 0.0,
            'eyebrow_raise': 0.0,
        }
        
        for gesture in self.active_gestures:
            elapsed = current_time - gesture['start_time']
            progress = elapsed / gesture['duration']
            
            # Apply gesture based on type
            if gesture['type'] == 'nod':
                # Nodding motion
                state['head_rotation'] += np.sin(progress * np.pi) * gesture['intensity'] * 0.1
            elif gesture['type'] == 'head_shake':
                # Shaking motion
                state['head_rotation'] += np.sin(progress * np.pi * 2) * gesture['intensity'] * 0.1
            elif gesture['type'] == 'head_tilt':
                # Tilting motion
                state['head_tilt'] += np.sin(progress * np.pi) * gesture['intensity'] * 0.15
            elif gesture['type'] == 'eyebrow_raise':
                # Eyebrow raise
                state['eyebrow_raise'] = np.sin(progress * np.pi) * gesture['intensity']
        
        return state
    
    async def start(self):
        """Start gesture processing"""
        # Process gesture queue
        while True:
            try:
                gesture = await asyncio.wait_for(self.gesture_queue.get(), timeout=1.0)
                self.active_gestures.append(gesture)
            except asyncio.TimeoutError:
                continue
    
    def reset(self):
        """Reset gesture state"""
        self.active_gestures.clear()
        while not self.gesture_queue.empty():
            try:
                self.gesture_queue.get_nowait()
            except asyncio.QueueEmpty:
                break


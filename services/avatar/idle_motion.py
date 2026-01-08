"""
Idle motion generator for natural avatar behavior.
Generates blinks, head micro-movements, and breathing-like motions.
"""

import asyncio
import logging
import time
import random
from typing import Dict, Any
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IdleMotion:
    """Generates natural idle animations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.last_blink_time = time.time()
        self.blink_interval = random.uniform(2.0, 5.0)  # Random blink interval
        self.blink_duration = 0.15  # Blink duration in seconds
        self.is_blinking = False
        self.head_position = np.array([0.0, 0.0, 0.0])  # x, y, rotation
        self.head_velocity = np.array([0.0, 0.0, 0.0])
        self.last_update = time.time()
    
    def update(self) -> Dict[str, Any]:
        """Update idle motion state"""
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        motion = {
            'blink': False,
            'head_position': self.head_position.copy(),
            'breathing': 0.0,
        }
        
        # Blink logic
        if not self.is_blinking and (current_time - self.last_blink_time) >= self.blink_interval:
            self.is_blinking = True
            self.blink_start_time = current_time
            motion['blink'] = True
        
        if self.is_blinking:
            if (current_time - self.blink_start_time) >= self.blink_duration:
                self.is_blinking = False
                self.last_blink_time = current_time
                self.blink_interval = random.uniform(2.0, 5.0)
            else:
                # Blink in progress
                motion['blink'] = True
        
        # Head micro-movements
        self._update_head_motion(dt)
        motion['head_position'] = self.head_position.copy()
        
        # Breathing-like motion (subtle scale variation)
        motion['breathing'] = np.sin(current_time * 2.0) * 0.01  # Very subtle
        
        return motion
    
    def _update_head_motion(self, dt: float):
        """Update head position with natural micro-movements"""
        # Simple physics-based head movement
        target_position = np.array([
            random.uniform(-0.02, 0.02),  # Small x movement
            random.uniform(-0.01, 0.01),  # Small y movement
            random.uniform(-0.05, 0.05),  # Small rotation
        ])
        
        # Smooth interpolation towards target
        spring_constant = 5.0
        damping = 0.8
        
        force = (target_position - self.head_position) * spring_constant
        self.head_velocity = self.head_velocity * damping + force * dt
        self.head_position += self.head_velocity * dt
        
        # Occasionally reset target
        if random.random() < 0.01:  # 1% chance per frame
            target_position = np.array([0.0, 0.0, 0.0])
    
    def trigger_blink(self):
        """Manually trigger a blink"""
        self.is_blinking = True
        self.blink_start_time = time.time()
    
    def reset(self):
        """Reset idle motion state"""
        self.head_position = np.array([0.0, 0.0, 0.0])
        self.head_velocity = np.array([0.0, 0.0, 0.0])
        self.is_blinking = False
        self.last_blink_time = time.time()


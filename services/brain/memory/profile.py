"""
User profile management (read-only, not learned).
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserProfile:
    """User profile (static, not learned)"""
    
    def __init__(self, profile_path: Optional[str] = None):
        self.profile_path = Path(profile_path) if profile_path else None
        self.profile: Dict[str, Any] = self._load_profile()
    
    def _load_profile(self) -> Dict[str, Any]:
        """Load user profile from file"""
        if self.profile_path and self.profile_path.exists():
            try:
                with open(self.profile_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading profile: {e}")
        
        # Default profile
        return {
            'name': 'User',
            'preferences': {
                'response_style': 'conversational',
                'formality': 'casual',
            },
            'voice_settings': {
                'reference_audio': None,
            },
            'avatar_settings': {
                'face_source': None,
            },
        }
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference"""
        keys = key.split('.')
        value = self.profile
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def update_preference(self, key: str, value: Any):
        """Update a preference (does not persist)"""
        keys = key.split('.')
        profile = self.profile
        for k in keys[:-1]:
            if k not in profile:
                profile[k] = {}
            profile = profile[k]
        profile[keys[-1]] = value


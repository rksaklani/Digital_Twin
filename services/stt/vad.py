"""
Voice Activity Detection using Silero VAD.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Tuple
import numpy as np
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VAD:
    """Voice Activity Detection service"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('models', {}).get('vad', {})
        self.model = None
        self.utils = None
        self.threshold = self.config.get('threshold', 0.5)
        self.min_speech_duration_ms = self.config.get('min_speech_duration_ms', 250)
        self.min_silence_duration_ms = self.config.get('min_silence_duration_ms', 100)
        self.speech_pad_ms = self.config.get('speech_pad_ms', 30)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    async def initialize(self):
        """Initialize Silero VAD model"""
        logger.info("Initializing VAD...")
        
        try:
            # Load Silero VAD model
            model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False,
            )
            
            self.model = model.to(self.device)
            self.model.eval()
            self.utils = utils
            
            logger.info(f"VAD model loaded on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load VAD model: {e}")
            # Fallback to simple energy-based VAD
            logger.warning("Using fallback energy-based VAD")
            self.model = None
    
    def detect_speech(self, audio: np.ndarray, sample_rate: int = 16000) -> Tuple[bool, float]:
        """
        Detect if audio contains speech.
        Returns (is_speech, confidence)
        """
        if self.model is None:
            # Fallback: simple energy-based detection
            return self._energy_based_vad(audio)
        
        try:
            # Convert to tensor
            if isinstance(audio, np.ndarray):
                audio_tensor = torch.from_numpy(audio).float()
            else:
                audio_tensor = torch.tensor(audio, dtype=torch.float32)
            
            # Ensure correct shape
            if audio_tensor.dim() == 1:
                audio_tensor = audio_tensor.unsqueeze(0)
            
            # Move to device
            audio_tensor = audio_tensor.to(self.device)
            
            # Run VAD
            with torch.no_grad():
                speech_prob = self.model(audio_tensor, sample_rate).item()
            
            is_speech = speech_prob >= self.threshold
            return is_speech, speech_prob
        
        except Exception as e:
            logger.error(f"Error in VAD detection: {e}")
            return self._energy_based_vad(audio)
    
    def _energy_based_vad(self, audio: np.ndarray) -> Tuple[bool, float]:
        """Fallback energy-based VAD"""
        if len(audio) == 0:
            return False, 0.0
        
        # Calculate RMS energy
        energy = np.sqrt(np.mean(audio ** 2))
        
        # Simple threshold (adjust based on your audio levels)
        threshold = 0.01
        is_speech = energy > threshold
        
        # Normalize confidence
        confidence = min(energy / (threshold * 2), 1.0)
        
        return is_speech, confidence
    
    def filter_silence(self, audio: np.ndarray, sample_rate: int = 16000) -> Optional[np.ndarray]:
        """Filter out silence from audio"""
        is_speech, confidence = self.detect_speech(audio, sample_rate)
        
        if is_speech:
            return audio
        else:
            return None


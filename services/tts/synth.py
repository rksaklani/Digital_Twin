"""
TTS service with voice cloning using XTTS.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech service with voice cloning"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('models', {}).get('tts', {})
        self.model = None
        self.router = None
        self.reference_audio = None
        self.reference_audio_path = self.config.get('voice_clone_reference')
        self.sample_rate = self.config.get('sample_rate', 24000)
        self.language = self.config.get('language', 'en')
        self.interrupted = False
    
    async def initialize(self):
        """Initialize TTS model"""
        logger.info("Initializing TTS service...")
        
        try:
            # Try to use Coqui TTS
            from TTS.api import TTS
            
            model_name = self.config.get('model_name', 'tts_models/multilingual/multi-dataset/xtts_v2')
            device = self.config.get('device', 'cuda')
            
            self.model = TTS(model_name=model_name)
            self.model.to(device)
            
            # Load reference audio if provided
            if self.reference_audio_path and Path(self.reference_audio_path).exists():
                # Load reference audio for voice cloning
                import soundfile as sf
                self.reference_audio, _ = sf.read(self.reference_audio_path)
                logger.info(f"Loaded reference audio: {self.reference_audio_path}")
            else:
                logger.warning("No reference audio provided for voice cloning")
            
            logger.info(f"TTS model loaded: {model_name} on {device}")
        
        except ImportError:
            logger.warning("Coqui TTS not available, using fallback")
        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            logger.warning("TTS service will use fallback mode")
    
    def set_router(self, router):
        """Set event router"""
        self.router = router
    
    async def synthesize(self, text: str, emotion: Optional[str] = None):
        """Synthesize speech from text"""
        self.interrupted = False
        
        if not self.model:
            logger.warning("TTS model not available")
            return
        
        try:
            # Use streaming synthesis for low latency
            await self._synthesize_streaming(text, emotion)
        
        except Exception as e:
            logger.error(f"Error in TTS synthesis: {e}")
    
    async def _synthesize_streaming(self, text: str, emotion: Optional[str] = None):
        """Synthesize speech with streaming output"""
        if not self.model or not self.router:
            return
        
        # Adjust prosody based on emotion
        prosody_settings = self._get_prosody_settings(emotion)
        
        # Run synthesis in executor
        loop = asyncio.get_event_loop()
        
        def _synthesize():
            try:
                # Synthesize with voice cloning
                if self.reference_audio is not None:
                    wav = self.model.tts(
                        text=text,
                        speaker_wav=self.reference_audio,
                        language=self.language,
                    )
                else:
                    wav = self.model.tts(
                        text=text,
                        language=self.language,
                    )
                
                # Convert to numpy array
                if isinstance(wav, list):
                    wav = np.array(wav)
                
                # Apply prosody adjustments if needed
                if prosody_settings:
                    wav = self._apply_prosody(wav, prosody_settings)
                
                return wav
            
            except Exception as e:
                logger.error(f"Error in TTS synthesis: {e}")
                return None
        
        audio_data = await loop.run_in_executor(None, _synthesize)
        
        if audio_data is not None and not self.interrupted:
            # Stream audio in chunks
            chunk_size = self.config.get('stream_chunk_size', 512)
            for i in range(0, len(audio_data), chunk_size):
                if self.interrupted:
                    break
                
                chunk = audio_data[i:i + chunk_size]
                
                # Emit audio chunk
                await self.router.emit('tts_audio', {
                    'data': chunk,
                    'timestamp': asyncio.get_event_loop().time(),
                    'sample_rate': self.sample_rate,
                })
    
    def _get_prosody_settings(self, emotion: Optional[str]) -> Optional[Dict[str, Any]]:
        """Get prosody settings based on emotion"""
        if not emotion:
            return None
        
        # Simple prosody mapping
        prosody_map = {
            'positive': {'speed': 1.1, 'pitch_shift': 0.1},
            'negative': {'speed': 0.9, 'pitch_shift': -0.1},
            'neutral': {'speed': 1.0, 'pitch_shift': 0.0},
        }
        
        return prosody_map.get(emotion, prosody_map['neutral'])
    
    def _apply_prosody(self, audio: np.ndarray, settings: Dict[str, Any]) -> np.ndarray:
        """Apply prosody adjustments to audio"""
        # Simple prosody adjustment (placeholder)
        # In production, use proper audio processing libraries
        speed = settings.get('speed', 1.0)
        pitch_shift = settings.get('pitch_shift', 0.0)
        
        # For now, just return audio as-is
        # Proper implementation would use librosa or similar
        return audio
    
    async def interrupt(self):
        """Interrupt current synthesis"""
        self.interrupted = True
        logger.info("TTS synthesis interrupted")
    
    async def shutdown(self):
        """Shutdown TTS service"""
        if self.model:
            del self.model
        logger.info("TTS service shutdown")


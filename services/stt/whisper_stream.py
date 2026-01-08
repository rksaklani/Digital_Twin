"""
Streaming Whisper STT service.
Uses faster-whisper for real-time transcription.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Callable
import numpy as np
from faster_whisper import WhisperModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhisperStream:
    """Streaming Whisper STT service"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('models', {}).get('stt', {})
        self.model: Optional[WhisperModel] = None
        self.router = None  # Will be set by orchestrator
        self.audio_buffer: list = []
        self.buffer_size = 16000  # 1 second at 16kHz
        self.running = False
        self._process_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize Whisper model"""
        logger.info("Initializing Whisper STT...")
        
        model_size = self.config.get('model_size', 'medium')
        device = self.config.get('device', 'cuda')
        compute_type = self.config.get('compute_type', 'float16')
        
        try:
            self.model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
            )
            logger.info(f"Whisper model loaded: {model_size} on {device}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def set_router(self, router):
        """Set event router for sending transcriptions"""
        self.router = router
    
    async def process_audio(self, audio_data: np.ndarray):
        """Process audio chunk"""
        if not self.running:
            return
        
        # Add to buffer
        if isinstance(audio_data, np.ndarray):
            self.audio_buffer.extend(audio_data.flatten())
        else:
            self.audio_buffer.extend(audio_data)
        
        # Process if buffer is large enough
        if len(self.audio_buffer) >= self.buffer_size:
            await self._process_buffer()
    
    async def _process_buffer(self):
        """Process accumulated audio buffer"""
        if not self.model or not self.router:
            return
        
        # Convert buffer to numpy array
        audio_array = np.array(self.audio_buffer[:self.buffer_size], dtype=np.float32)
        
        # Normalize if needed
        if audio_array.max() > 1.0:
            audio_array = audio_array / 32768.0
        
        # Clear buffer (keep overlap for continuity)
        overlap_size = self.buffer_size // 4
        self.audio_buffer = self.audio_buffer[-overlap_size:]
        
        # Run transcription in executor to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            segments, info = await loop.run_in_executor(
                None,
                self._transcribe,
                audio_array
            )
            
            # Process segments
            for segment in segments:
                text = segment.text.strip()
                if text:
                    await self.router.emit('transcription', {
                        'text': text,
                        'is_final': True,
                        'timestamp': asyncio.get_event_loop().time(),
                        'language': info.language,
                        'probability': segment.probability,
                    })
                    logger.info(f"Transcription: {text}")
        
        except Exception as e:
            logger.error(f"Error in transcription: {e}")
    
    def _transcribe(self, audio: np.ndarray):
        """Run Whisper transcription (blocking)"""
        segments, info = self.model.transcribe(
            audio,
            beam_size=self.config.get('beam_size', 5),
            best_of=self.config.get('best_of', 5),
            temperature=self.config.get('temperature', 0.0),
            compression_ratio_threshold=self.config.get('compression_ratio_threshold', 2.4),
            logprob_threshold=self.config.get('logprob_threshold', -1.0),
            no_speech_threshold=self.config.get('no_speech_threshold', 0.6),
        )
        return list(segments), info
    
    async def start(self):
        """Start the STT service"""
        self.running = True
        logger.info("STT service started")
    
    async def shutdown(self):
        """Shutdown the STT service"""
        self.running = False
        if self._process_task:
            self._process_task.cancel()
            try:
                await self._process_task
            except asyncio.CancelledError:
                pass
        logger.info("STT service shutdown")


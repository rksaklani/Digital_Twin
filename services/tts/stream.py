"""
Streaming TTS for low-latency audio output.
"""

import asyncio
import logging
from typing import AsyncIterator, Optional
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StreamingTTS:
    """Streaming TTS output handler"""
    
    def __init__(self, chunk_size: int = 512, sample_rate: int = 24000):
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.queue = asyncio.Queue()
        self.running = False
    
    async def stream_audio(self, audio_data: np.ndarray) -> AsyncIterator[np.ndarray]:
        """Stream audio data in chunks"""
        for i in range(0, len(audio_data), self.chunk_size):
            chunk = audio_data[i:i + self.chunk_size]
            yield chunk
    
    async def put_chunk(self, chunk: np.ndarray):
        """Put audio chunk into queue"""
        await self.queue.put(chunk)
    
    async def get_chunk(self) -> Optional[np.ndarray]:
        """Get next audio chunk from queue"""
        try:
            return await asyncio.wait_for(self.queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return None
    
    def start(self):
        """Start streaming"""
        self.running = True
    
    def stop(self):
        """Stop streaming"""
        self.running = False
        # Clear queue
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except asyncio.QueueEmpty:
                break


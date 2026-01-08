"""
Audio input track for receiving microphone audio from browser.
"""

import asyncio
import logging
from typing import Callable, Optional
from aiortc import MediaStreamTrack
from av import AudioFrame
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioInputTrack(MediaStreamTrack):
    """Audio track that receives input from browser"""
    
    kind = "audio"
    
    def __init__(self, on_frame_callback: Optional[Callable] = None):
        super().__init__()
        self.on_frame_callback = on_frame_callback
        self._queue = asyncio.Queue()
        self._running = True
    
    async def recv(self):
        """Receive audio frame"""
        if not self._running:
            raise Exception("Track stopped")
        
        # Get frame from queue (populated by WebRTC)
        try:
            frame = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            
            # Call callback if provided
            if self.on_frame_callback:
                try:
                    self.on_frame_callback(frame)
                except Exception as e:
                    logger.error(f"Error in audio frame callback: {e}")
            
            return frame
        except asyncio.TimeoutError:
            # Return silence if no frame available
            return self._create_silence_frame()
    
    def put_frame(self, frame: AudioFrame):
        """Put a frame into the queue (called by WebRTC)"""
        if self._running:
            self._queue.put_nowait(frame)
    
    def _create_silence_frame(self) -> AudioFrame:
        """Create a silence frame"""
        frame = AudioFrame.from_ndarray(
            np.zeros((160, 1), dtype=np.int16),
            layout="mono",
        )
        frame.sample_rate = 16000
        frame.time_base = (1, 16000)
        return frame
    
    def stop(self):
        """Stop the track"""
        self._running = False
        # Clear queue
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except asyncio.QueueEmpty:
                break


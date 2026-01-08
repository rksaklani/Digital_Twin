"""
Video output track for sending avatar video to browser.
"""

import asyncio
import logging
from typing import Optional
from aiortc import VideoStreamTrack
from av import VideoFrame
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AvatarVideoTrack(VideoStreamTrack):
    """Video track that sends avatar frames to browser"""
    
    def __init__(self):
        super().__init__()
        self._queue = asyncio.Queue(maxsize=10)
        self._running = True
        self._frame_count = 0
        self._fps = 25
        self._time_base = (1, self._fps)
    
    async def recv(self):
        """Send video frame to browser"""
        if not self._running:
            raise Exception("Track stopped")
        
        try:
            frame = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            frame.pts = self._frame_count
            frame.time_base = self._time_base
            self._frame_count += 1
            return frame
        except asyncio.TimeoutError:
            # Return black frame if no frame available
            return self._create_black_frame()
    
    async def put_frame(self, frame_data: np.ndarray):
        """Put a frame into the queue (called by avatar renderer)"""
        if not self._running:
            return
        
        try:
            # Convert numpy array to VideoFrame
            if isinstance(frame_data, np.ndarray):
                frame = VideoFrame.from_ndarray(frame_data, format="rgb24")
            else:
                frame = frame_data
            
            # Non-blocking put
            try:
                self._queue.put_nowait(frame)
            except asyncio.QueueFull:
                # Drop oldest frame if queue is full
                try:
                    self._queue.get_nowait()
                    self._queue.put_nowait(frame)
                except asyncio.QueueEmpty:
                    pass
        except Exception as e:
            logger.error(f"Error putting frame: {e}")
    
    def _create_black_frame(self) -> VideoFrame:
        """Create a black frame"""
        frame = VideoFrame.from_ndarray(
            np.zeros((512, 512, 3), dtype=np.uint8),
            format="rgb24",
        )
        frame.pts = self._frame_count
        frame.time_base = self._time_base
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


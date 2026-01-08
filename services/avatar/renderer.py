"""
Avatar renderer.
Combines lip sync, expressions, and idle motion into video frames.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
import numpy as np
import cv2
from pathlib import Path

from .lip_sync import LipSync
from .expression import ExpressionSystem
from .idle_motion import IdleMotion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AvatarRenderer:
    """Renders avatar video frames"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('models', {}).get('avatar', {})
        self.lip_sync = LipSync(config)
        self.expression = ExpressionSystem(config)
        self.idle_motion = IdleMotion(config)
        
        self.face_source = None
        self.face_source_path = self.config.get('face_source', {}).get('path')
        self.output_width = self.config.get('render', {}).get('output_width', 512)
        self.output_height = self.config.get('render', {}).get('output_height', 512)
        self.fps = self.config.get('render', {}).get('fps', 25)
        
        self.current_frame = None
        self.router = None
        self.running = False
        self._render_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize avatar renderer"""
        logger.info("Initializing avatar renderer...")
        
        await self.lip_sync.initialize()
        
        # Load face source
        if self.face_source_path and Path(self.face_source_path).exists():
            # Load video or image
            if self.face_source_path.endswith('.mp4') or self.face_source_path.endswith('.avi'):
                # Load video frame
                cap = cv2.VideoCapture(self.face_source_path)
                ret, frame = cap.read()
                if ret:
                    self.face_source = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                cap.release()
            else:
                # Load image
                img = cv2.imread(self.face_source_path)
                if img is not None:
                    self.face_source = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        if self.face_source is None:
            # Create placeholder face
            self.face_source = np.zeros((512, 512, 3), dtype=np.uint8)
            self.face_source[:] = (100, 100, 100)  # Gray background
            logger.warning("No face source provided, using placeholder")
        
        logger.info("Avatar renderer initialized")
    
    def set_router(self, router):
        """Set event router"""
        self.router = router
    
    async def process_audio(self, audio_data: np.ndarray):
        """Process audio for lip sync"""
        if not self.running:
            return
        
        # Generate visemes from audio
        visemes = await self.lip_sync.generate_visemes(audio_data)
        
        # Update current frame with lip sync
        # This is a placeholder - actual implementation would apply visemes to face
        await self._render_frame(visemes=visemes)
    
    async def _render_frame(self, visemes: Optional[np.ndarray] = None, emotion: Optional[str] = None):
        """Render a single frame"""
        # Start with face source
        frame = self.face_source.copy()
        
        # Apply expressions
        if emotion:
            expr_params = self.expression.get_expression(emotion, None)
            # Apply expression to frame (placeholder)
        
        # Apply idle motion
        idle = self.idle_motion.update()
        if idle['blink']:
            # Apply blink (placeholder)
            pass
        
        # Apply lip sync
        if visemes is not None and len(visemes) > 0:
            # Apply visemes to frame (placeholder)
            # In production, this would use Wav2Lip or similar
            pass
        
        # Resize to output dimensions
        frame = cv2.resize(frame, (self.output_width, self.output_height))
        
        self.current_frame = frame
        
        # Send to WebRTC
        if self.router:
            await self.router.emit('video_frame', {
                'data': frame,
                'timestamp': asyncio.get_event_loop().time(),
            })
    
    async def start(self):
        """Start rendering loop"""
        self.running = True
        self._render_task = asyncio.create_task(self._render_loop())
        logger.info("Avatar renderer started")
    
    async def _render_loop(self):
        """Main rendering loop"""
        frame_time = 1.0 / self.fps
        
        while self.running:
            start_time = asyncio.get_event_loop().time()
            
            # Render frame with current state
            await self._render_frame()
            
            # Sleep to maintain FPS
            elapsed = asyncio.get_event_loop().time() - start_time
            sleep_time = max(0, frame_time - elapsed)
            await asyncio.sleep(sleep_time)
    
    async def interrupt(self):
        """Interrupt rendering"""
        self.running = False
        if self._render_task:
            self._render_task.cancel()
            try:
                await self._render_task
            except asyncio.CancelledError:
                pass
    
    async def shutdown(self):
        """Shutdown renderer"""
        self.running = False
        if self._render_task:
            self._render_task.cancel()
            try:
                await self._render_task
            except asyncio.CancelledError:
                pass
        
        await self.lip_sync.shutdown()
        logger.info("Avatar renderer shutdown")


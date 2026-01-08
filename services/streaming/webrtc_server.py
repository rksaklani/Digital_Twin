"""
WebRTC server using aiortc.
Handles peer connections, audio input, and video output.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
from aiortc.contrib.media import MediaPlayer, MediaRelay

from .audio_track import AudioInputTrack
from .video_track import AvatarVideoTrack

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebRTCServer:
    """WebRTC server for handling browser connections"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.peer_connections: Dict[str, RTCPeerConnection] = {}
        self.audio_track: Optional[AudioInputTrack] = None
        self.video_track: Optional[AvatarVideoTrack] = None
        self.router = None  # Will be set by orchestrator
        self.running = False
    
    async def initialize(self):
        """Initialize WebRTC server"""
        logger.info("Initializing WebRTC server...")
        
        # Create audio and video tracks
        self.audio_track = AudioInputTrack(self._on_audio_frame)
        self.video_track = AvatarVideoTrack()
        
        logger.info("WebRTC server initialized")
    
    def set_router(self, router):
        """Set event router for sending events"""
        self.router = router
    
    def _on_audio_frame(self, frame):
        """Callback when audio frame is received"""
        if self.router:
            # Convert frame to audio data
            import numpy as np
            audio_data = frame.to_ndarray()
            
            # Emit audio input event
            asyncio.create_task(self.router.emit('audio_input', {
                'data': audio_data,
                'timestamp': asyncio.get_event_loop().time(),
            }))
    
    async def handle_offer(self, offer_sdp: str, session_id: str) -> str:
        """Handle WebRTC offer and return answer"""
        logger.info(f"Handling offer for session {session_id}")
        
        # Create peer connection
        webrtc_config = self.config.get('webrtc', {})
        ice_servers = []
        
        for server_config in webrtc_config.get('ice_servers', []):
            ice_servers.append(RTCIceServer(
                urls=server_config.get('urls', []),
                username=server_config.get('username'),
                credential=server_config.get('credential'),
            ))
        
        pc = RTCPeerConnection(
            configuration=RTCConfiguration(iceServers=ice_servers)
        )
        
        self.peer_connections[session_id] = pc
        
        # Handle connection state changes
        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            logger.info(f"Connection state: {pc.connectionState}")
            if pc.connectionState in ["failed", "closed"]:
                await self._cleanup_session(session_id)
        
        # Add tracks
        if self.audio_track:
            pc.addTrack(self.audio_track)
        if self.video_track:
            pc.addTrack(self.video_track)
        
        # Set remote description
        offer = RTCSessionDescription(sdp=offer_sdp, type="offer")
        await pc.setRemoteDescription(offer)
        
        # Create answer
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        
        logger.info(f"Created answer for session {session_id}")
        return pc.localDescription.sdp
    
    async def handle_ice_candidate(self, candidate: Dict[str, Any], session_id: str):
        """Handle ICE candidate"""
        if session_id not in self.peer_connections:
            logger.warning(f"Session {session_id} not found for ICE candidate")
            return
        
        pc = self.peer_connections[session_id]
        # Add ICE candidate to peer connection
        # Note: aiortc handles this automatically, but we can process if needed
        logger.debug(f"Received ICE candidate for session {session_id}")
    
    async def send_audio(self, audio_data: Any):
        """Send audio data to WebRTC output"""
        if self.video_track:
            # Audio is sent via video track for lip sync
            # The video track will handle audio-to-viseme conversion
            pass
        
        # For now, we'll send audio through a separate audio track if needed
        # This is a placeholder - actual implementation depends on aiortc audio track setup
    
    async def send_video_frame(self, frame: Any):
        """Send video frame to WebRTC output"""
        if self.video_track:
            await self.video_track.put_frame(frame)
    
    async def _cleanup_session(self, session_id: str):
        """Clean up a session"""
        if session_id in self.peer_connections:
            pc = self.peer_connections[session_id]
            await pc.close()
            del self.peer_connections[session_id]
            logger.info(f"Cleaned up session {session_id}")
    
    async def start(self):
        """Start the WebRTC server"""
        logger.info("WebRTC server started")
        self.running = True
        
        # In a real implementation, this would set up a signaling endpoint
        # For now, we'll integrate with the orchestrator's event system
    
    async def shutdown(self):
        """Shutdown the WebRTC server"""
        logger.info("Shutting down WebRTC server...")
        self.running = False
        
        # Close all peer connections
        for session_id in list(self.peer_connections.keys()):
            await self._cleanup_session(session_id)
        
        logger.info("WebRTC server shutdown complete")


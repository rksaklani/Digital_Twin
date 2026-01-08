"""
Core orchestration pipeline.
Coordinates all services for real-time digital clone operation.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import yaml

from .router import EventRouter
from .interrupt import InterruptHandler
from .latency import LatencyMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Pipeline:
    """Main pipeline orchestrator"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.config = self._load_configs()
        
        self.router = EventRouter()
        self.interrupt_handler = InterruptHandler()
        self.latency_monitor = LatencyMonitor()
        
        self.services: Dict[str, Any] = {}
        self.running = False
        
    def _load_configs(self) -> Dict[str, Any]:
        """Load all configuration files"""
        configs = {}
        config_files = ['models.yaml', 'gpu.yaml', 'latency.yaml', 'webrtc.yaml']
        
        for config_file in config_files:
            config_path = self.config_dir / config_file
            if config_path.exists():
                with open(config_path, 'r') as f:
                    configs[config_file.replace('.yaml', '')] = yaml.safe_load(f)
            else:
                logger.warning(f"Config file not found: {config_path}")
        
        return configs
    
    async def initialize_services(self):
        """Initialize all AI services"""
        logger.info("Initializing services...")
        
        # Import services lazily to avoid circular dependencies
        from services.streaming.webrtc_server import WebRTCServer
        from services.stt.whisper_stream import WhisperStream
        from services.intent_emotion.classify import IntentEmotionClassifier
        from services.brain.llm import LLMService
        from services.tts.synth import TTSService
        from services.avatar.renderer import AvatarRenderer
        
        # Initialize services in order
        self.services['webrtc'] = WebRTCServer(self.config)
        await self.services['webrtc'].initialize()
        
        self.services['stt'] = WhisperStream(self.config)
        await self.services['stt'].initialize()
        
        self.services['intent'] = IntentEmotionClassifier(self.config)
        await self.services['intent'].initialize()
        
        self.services['llm'] = LLMService(self.config)
        await self.services['llm'].initialize()
        
        self.services['tts'] = TTSService(self.config)
        await self.services['tts'].initialize()
        
        self.services['avatar'] = AvatarRenderer(self.config)
        await self.services['avatar'].initialize()
        
        # Set routers for all services
        self.services['webrtc'].set_router(self.router)
        self.services['stt'].set_router(self.router)
        self.services['llm'].set_router(self.router)
        self.services['tts'].set_router(self.router)
        self.services['avatar'].set_router(self.router)
        
        # Set memory for LLM
        from services.brain.memory.session import SessionMemory
        memory = SessionMemory()
        self.services['llm'].set_memory(memory)
        
        # Register service handlers with router
        self._register_handlers()
        
        # Register video frame handler
        self.router.register('video_frame', self._handle_video_frame)
        
        # Start router
        await self.router.start()
        
        logger.info("All services initialized")
    
    async def _handle_video_frame(self, event: Dict[str, Any]):
        """Handle video frame from avatar renderer"""
        frame_data = event.get('data')
        if frame_data is not None and 'webrtc' in self.services:
            await self.services['webrtc'].send_video_frame(frame_data)
    
    def _register_handlers(self):
        """Register event handlers for each service"""
        self.router.register('audio_input', self._handle_audio_input)
        self.router.register('transcription', self._handle_transcription)
        self.router.register('intent', self._handle_intent)
        self.router.register('llm_response', self._handle_llm_response)
        self.router.register('tts_audio', self._handle_tts_audio)
        self.router.register('interrupt', self._handle_interrupt)
    
    async def _handle_audio_input(self, event: Dict[str, Any]):
        """Handle incoming audio from WebRTC"""
        audio_data = event.get('data')
        timestamp = event.get('timestamp', asyncio.get_event_loop().time())
        
        # Track latency
        self.latency_monitor.mark('audio_received', timestamp)
        
        # Send to STT
        await self.services['stt'].process_audio(audio_data)
    
    async def _handle_transcription(self, event: Dict[str, Any]):
        """Handle STT transcription"""
        text = event.get('text')
        is_final = event.get('is_final', False)
        timestamp = event.get('timestamp')
        
        if not text:
            return
        
        # Check for interrupt
        if self.interrupt_handler.should_interrupt(text):
            await self._handle_interrupt({'reason': 'user_speech'})
            return
        
        # Track latency
        self.latency_monitor.mark('transcription_complete', timestamp)
        
        # Send to intent classifier
        intent_result = await self.services['intent'].classify(text)
        
        # Route to LLM with intent
        await self.router.emit('intent', {
            'text': text,
            'intent': intent_result,
            'timestamp': timestamp,
        })
    
    async def _handle_intent(self, event: Dict[str, Any]):
        """Handle intent classification result"""
        text = event.get('text')
        intent = event.get('intent')
        timestamp = event.get('timestamp')
        
        # Generate response with LLM
        response = await self.services['llm'].generate(text, intent)
        
        await self.router.emit('llm_response', {
            'text': response,
            'intent': intent,
            'timestamp': timestamp,
        })
    
    async def _handle_llm_response(self, event: Dict[str, Any]):
        """Handle LLM response"""
        text = event.get('text')
        intent = event.get('intent')
        timestamp = event.get('timestamp')
        
        if not text:
            return
        
        # Track latency
        self.latency_monitor.mark('llm_complete', timestamp)
        
        # Get emotion from intent for TTS prosody
        emotion = intent.get('emotion', 'neutral') if intent else 'neutral'
        
        # Synthesize speech
        await self.services['tts'].synthesize(text, emotion=emotion)
    
    async def _handle_tts_audio(self, event: Dict[str, Any]):
        """Handle TTS audio output"""
        audio_data = event.get('data')
        timestamp = event.get('timestamp')
        
        # Track latency
        self.latency_monitor.mark('tts_complete', timestamp)
        
        # Send to avatar for lip sync
        await self.services['avatar'].process_audio(audio_data)
        
        # Send audio to WebRTC for output (via video track)
        # The avatar renderer will send video frames with lip sync
    
    async def _handle_interrupt(self, event: Dict[str, Any]):
        """Handle interrupt signal"""
        reason = event.get('reason', 'unknown')
        logger.info(f"Interrupt triggered: {reason}")
        
        # Cancel all in-flight operations
        await self.interrupt_handler.cancel_all()
        
        # Cancel specific services
        if 'tts' in self.services:
            await self.services['tts'].interrupt()
        if 'llm' in self.services:
            await self.services['llm'].interrupt()
        if 'avatar' in self.services:
            await self.services['avatar'].interrupt()
        
        # Reset state
        self.latency_monitor.reset()
    
    async def run(self):
        """Main pipeline loop"""
        logger.info("Starting pipeline...")
        
        try:
            await self.initialize_services()
            self.running = True
            
        # Start avatar renderer
        await self.services['avatar'].start()
        
        # Start WebRTC server (this will handle connections)
        await self.services['webrtc'].start()
        
        # Start STT service
        await self.services['stt'].start()
            
            # Main event loop
            while self.running:
                await asyncio.sleep(0.1)
                
                # Check latency metrics
                metrics = self.latency_monitor.get_metrics()
                if metrics:
                    logger.debug(f"Latency metrics: {metrics}")
        
        except KeyboardInterrupt:
            logger.info("Pipeline interrupted by user")
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown all services"""
        logger.info("Shutting down pipeline...")
        self.running = False
        
        # Stop router
        await self.router.stop()
        
        # Shutdown services in reverse order
        for service_name in reversed(list(self.services.keys())):
            if hasattr(self.services[service_name], 'shutdown'):
                await self.services[service_name].shutdown()
        
        logger.info("Pipeline shutdown complete")


async def main():
    """Entry point"""
    pipeline = Pipeline()
    await pipeline.run()


if __name__ == "__main__":
    asyncio.run(main())


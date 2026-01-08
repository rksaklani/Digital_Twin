"""
Interrupt handler for real-time cancellation of in-flight operations.
Handles TTS stream interruption, LLM generation cancellation, and state cleanup.
"""

import asyncio
import logging
from typing import Set, Optional
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InterruptReason(Enum):
    """Reasons for interruption"""
    USER_SPEECH = "user_speech"
    TIMEOUT = "timeout"
    ERROR = "error"
    MANUAL = "manual"


class InterruptHandler:
    """Handles interrupts and cancellation"""
    
    def __init__(self):
        self.active_tasks: Set[asyncio.Task] = set()
        self.interrupt_flag = asyncio.Event()
        self.interrupt_reason: Optional[InterruptReason] = None
        self.lock = asyncio.Lock()
    
    def register_task(self, task: asyncio.Task):
        """Register a task that can be cancelled"""
        self.active_tasks.add(task)
        task.add_done_callback(lambda t: self.active_tasks.discard(t))
    
    async def cancel_all(self):
        """Cancel all registered tasks"""
        async with self.lock:
            logger.info(f"Cancelling {len(self.active_tasks)} active tasks")
            
            # Set interrupt flag
            self.interrupt_flag.set()
            
            # Cancel all tasks
            for task in list(self.active_tasks):
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Clear interrupt flag after a short delay
            await asyncio.sleep(0.1)
            self.interrupt_flag.clear()
            
            logger.info("All tasks cancelled")
    
    def is_interrupted(self) -> bool:
        """Check if interrupt flag is set"""
        return self.interrupt_flag.is_set()
    
    async def wait_if_interrupted(self):
        """Wait if interrupted, raise CancelledError if so"""
        if self.interrupt_flag.is_set():
            raise asyncio.CancelledError("Operation interrupted")
    
    def should_interrupt(self, text: str) -> bool:
        """Determine if user speech should trigger interrupt"""
        # Simple heuristic: if we detect new user speech, interrupt
        # This is a placeholder - actual implementation would check
        # if TTS/LLM is currently active
        return False  # Will be enhanced with state tracking
    
    def set_reason(self, reason: InterruptReason):
        """Set the reason for interruption"""
        self.interrupt_reason = reason
    
    def get_reason(self) -> Optional[InterruptReason]:
        """Get the reason for interruption"""
        return self.interrupt_reason
    
    def reset(self):
        """Reset interrupt state"""
        self.interrupt_flag.clear()
        self.interrupt_reason = None
        self.active_tasks.clear()
        logger.debug("Interrupt handler reset")


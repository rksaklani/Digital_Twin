"""
Event router for inter-service communication.
Provides event bus with message queuing and prioritization.
"""

import asyncio
import logging
from typing import Dict, Any, Callable, List, Optional
from collections import deque
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Priority(Enum):
    """Event priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event:
    """Event data structure"""
    type: str
    data: Dict[str, Any]
    priority: Priority = Priority.NORMAL
    timestamp: float = 0.0


class EventRouter:
    """Event bus for service communication"""
    
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}
        self.queue: deque = deque()
        self.running = False
        self._loop_task: Optional[asyncio.Task] = None
    
    def register(self, event_type: str, handler: Callable):
        """Register a handler for an event type"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        logger.debug(f"Registered handler for {event_type}")
    
    def unregister(self, event_type: str, handler: Callable):
        """Unregister a handler"""
        if event_type in self.handlers:
            try:
                self.handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    async def emit(self, event_type: str, data: Dict[str, Any], priority: Priority = Priority.NORMAL):
        """Emit an event"""
        import time
        event = Event(
            type=event_type,
            data=data,
            priority=priority,
            timestamp=time.time(),
        )
        
        # Add to queue (sorted by priority)
        self._insert_by_priority(event)
        
        # Process immediately if not running queue processor
        if not self.running:
            await self._process_event(event)
    
    def _insert_by_priority(self, event: Event):
        """Insert event into queue by priority"""
        # Simple insertion - higher priority first
        inserted = False
        for i, queued_event in enumerate(self.queue):
            if event.priority.value > queued_event.priority.value:
                self.queue.insert(i, event)
                inserted = True
                break
        
        if not inserted:
            self.queue.append(event)
    
    async def _process_event(self, event: Event):
        """Process a single event"""
        event_type = event.type
        
        if event_type not in self.handlers:
            logger.warning(f"No handlers registered for event type: {event_type}")
            return
        
        # Call all handlers for this event type
        for handler in self.handlers.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event.data)
                else:
                    handler(event.data)
            except Exception as e:
                logger.error(f"Error in handler for {event_type}: {e}", exc_info=True)
    
    async def start(self):
        """Start the event loop processor"""
        if self.running:
            return
        
        self.running = True
        self._loop_task = asyncio.create_task(self._process_queue())
    
    async def stop(self):
        """Stop the event loop processor"""
        self.running = False
        if self._loop_task:
            await self._loop_task
    
    async def _process_queue(self):
        """Process events from queue"""
        while self.running:
            if self.queue:
                event = self.queue.popleft()
                await self._process_event(event)
            else:
                await asyncio.sleep(0.001)  # Small delay when queue is empty
    
    def clear(self):
        """Clear all events from queue"""
        self.queue.clear()
        logger.info("Event queue cleared")


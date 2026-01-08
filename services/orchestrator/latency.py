"""
Latency monitoring and tracking.
Measures end-to-end latency and per-component latency.
"""

import time
import logging
from typing import Dict, Optional, List
from collections import deque
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LatencyPoint:
    """A single latency measurement point"""
    name: str
    timestamp: float
    value: Optional[float] = None  # Latency in ms if calculated


class LatencyMonitor:
    """Tracks latency across the pipeline"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.points: Dict[str, deque] = {}  # Track points by name
        self.start_times: Dict[str, float] = {}  # Track start times for intervals
        self.measurements: deque = deque(maxlen=window_size)
    
    def mark(self, point_name: str, timestamp: Optional[float] = None):
        """Mark a latency measurement point"""
        if timestamp is None:
            timestamp = time.time()
        
        if point_name not in self.points:
            self.points[point_name] = deque(maxlen=self.window_size)
        
        self.points[point_name].append(timestamp)
        logger.debug(f"Latency point marked: {point_name} at {timestamp}")
    
    def start_interval(self, interval_name: str):
        """Start timing an interval"""
        self.start_times[interval_name] = time.time()
    
    def end_interval(self, interval_name: str) -> Optional[float]:
        """End timing an interval, returns latency in ms"""
        if interval_name not in self.start_times:
            logger.warning(f"Interval {interval_name} was not started")
            return None
        
        start_time = self.start_times.pop(interval_name)
        latency_ms = (time.time() - start_time) * 1000
        
        # Store measurement
        measurement = {
            'interval': interval_name,
            'latency_ms': latency_ms,
            'timestamp': time.time(),
        }
        self.measurements.append(measurement)
        
        logger.debug(f"Interval {interval_name}: {latency_ms:.2f}ms")
        return latency_ms
    
    def calculate_latency(self, start_point: str, end_point: str) -> Optional[float]:
        """Calculate latency between two points in ms"""
        if start_point not in self.points or end_point not in self.points:
            return None
        
        start_points = self.points[start_point]
        end_points = self.points[end_point]
        
        if not start_points or not end_points:
            return None
        
        # Get most recent points
        start_time = start_points[-1]
        end_time = end_points[-1]
        
        if end_time < start_time:
            return None
        
        latency_ms = (end_time - start_time) * 1000
        return latency_ms
    
    def get_metrics(self) -> Dict[str, float]:
        """Get current latency metrics"""
        metrics = {}
        
        # Calculate end-to-end latency if we have the points
        e2e_latency = self.calculate_latency('audio_received', 'tts_complete')
        if e2e_latency:
            metrics['end_to_end_ms'] = e2e_latency
        
        # Calculate component latencies
        component_pairs = [
            ('audio_received', 'transcription_complete', 'stt_ms'),
            ('transcription_complete', 'llm_complete', 'llm_ms'),
            ('llm_complete', 'tts_complete', 'tts_ms'),
        ]
        
        for start, end, name in component_pairs:
            latency = self.calculate_latency(start, end)
            if latency:
                metrics[name] = latency
        
        # Calculate averages from measurements
        if self.measurements:
            intervals = {}
            for m in self.measurements:
                interval = m['interval']
                if interval not in intervals:
                    intervals[interval] = []
                intervals[interval].append(m['latency_ms'])
            
            for interval, latencies in intervals.items():
                avg = sum(latencies) / len(latencies)
                metrics[f'{interval}_avg_ms'] = avg
        
        return metrics
    
    def reset(self):
        """Reset all latency tracking"""
        self.points.clear()
        self.start_times.clear()
        self.measurements.clear()
        logger.debug("Latency monitor reset")


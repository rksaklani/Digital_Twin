#!/usr/bin/env python3
"""
Latency profiling script.
Measures and reports latency across all components.
"""

import asyncio
import time
import json
from pathlib import Path
from typing import Dict, List


class LatencyProfiler:
    """Profiles latency across components"""
    
    def __init__(self):
        self.measurements: List[Dict] = []
        self.start_time = None
    
    def start(self):
        """Start profiling"""
        self.start_time = time.time()
        self.measurements = []
    
    def mark(self, component: str, timestamp: float = None):
        """Mark a latency point"""
        if timestamp is None:
            timestamp = time.time()
        
        self.measurements.append({
            'component': component,
            'timestamp': timestamp,
            'elapsed': timestamp - self.start_time if self.start_time else 0,
        })
    
    def get_report(self) -> Dict:
        """Generate latency report"""
        if not self.measurements:
            return {}
        
        # Calculate intervals
        intervals = []
        for i in range(1, len(self.measurements)):
            prev = self.measurements[i-1]
            curr = self.measurements[i]
            intervals.append({
                'from': prev['component'],
                'to': curr['component'],
                'latency_ms': (curr['timestamp'] - prev['timestamp']) * 1000,
            })
        
        # Calculate totals
        total_latency = (self.measurements[-1]['timestamp'] - self.start_time) * 1000
        
        return {
            'total_latency_ms': total_latency,
            'intervals': intervals,
            'measurements': self.measurements,
        }
    
    def save_report(self, filepath: str):
        """Save report to file"""
        report = self.get_report()
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Latency report saved to {filepath}")


def main():
    """Example usage"""
    profiler = LatencyProfiler()
    profiler.start()
    
    # Simulate measurements
    time.sleep(0.1)
    profiler.mark('audio_received')
    
    time.sleep(0.2)
    profiler.mark('stt_complete')
    
    time.sleep(0.5)
    profiler.mark('llm_complete')
    
    time.sleep(0.1)
    profiler.mark('tts_complete')
    
    # Generate report
    report = profiler.get_report()
    print(json.dumps(report, indent=2))
    
    # Save report
    profiler.save_report('latency_report.json')


if __name__ == "__main__":
    main()


"""Metrics and timing utilities for Doc Assist."""

import time
from contextlib import contextmanager
from typing import Dict, List, Any
import numpy as np


@contextmanager
def timer(name: str, collector: dict):
    """
    Context manager for timing code blocks.
    
    Args:
        name: Name of the timer
        collector: Dictionary to collect timing results
        
    Yields:
        None
    """
    t0 = time.time()
    yield
    dt = time.time() - t0
    collector.setdefault(name, []).append(dt)


class MetricsCollector:
    """
    Collector for various metrics.
    """
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.timings = {}
        self.counters = {}
        self.histograms = {}
    
    @contextmanager
    def time(self, name: str):
        """
        Context manager for timing operations.
        
        Args:
            name: Name of the operation
            
        Yields:
            None
        """
        with timer(name, self.timings):
            yield
    
    def increment(self, name: str, value: int = 1):
        """
        Increment a counter.
        
        Args:
            name: Name of the counter
            value: Value to increment by
        """
        self.counters[name] = self.counters.get(name, 0) + value
    
    def observe(self, name: str, value: float):
        """
        Observe a value for a histogram.
        
        Args:
            name: Name of the histogram
            value: Value to observe
        """
        self.histograms.setdefault(name, []).append(value)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics for all metrics.
        
        Returns:
            Dictionary of statistics
        """
        stats = {}
        
        # Process timings
        for name, values in self.timings.items():
            stats[f"{name}_mean"] = np.mean(values)
            stats[f"{name}_p50"] = np.percentile(values, 50)
            stats[f"{name}_p95"] = np.percentile(values, 95)
            stats[f"{name}_p99"] = np.percentile(values, 99)
        
        # Process counters
        for name, value in self.counters.items():
            stats[name] = value
        
        # Process histograms
        for name, values in self.histograms.items():
            stats[f"{name}_mean"] = np.mean(values)
            stats[f"{name}_p50"] = np.percentile(values, 50)
            stats[f"{name}_p95"] = np.percentile(values, 95)
            stats[f"{name}_p99"] = np.percentile(values, 99)
        
        return stats

"""
Metrics collection and monitoring for RAG system
Tracks performance, quality, and usage metrics
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import time
import statistics

from src.error_handling.logger import logger


class MetricsCollector:
    """
    Collect and aggregate system metrics
    
    Metrics tracked:
    - Query latency (overall and per component)
    - Retrieval quality (scores, relevance)
    - Cache performance (hit rate, savings)
    - Error rates and types
    - Token usage
    - System health
    """
    
    def __init__(self, window_size: int = 100, enable_metrics: bool = True):
        """
        Initialize metrics collector
        
        Args:
            window_size: Number of recent queries to track in detail
            enable_metrics: If False, metrics collection is disabled
        """
        self.window_size = window_size
        self.enable_metrics = enable_metrics
        
        # Query metrics (rolling window)
        self.query_history: deque = deque(maxlen=window_size)
        
        # Aggregated metrics
        self.metrics = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_latency': 0.0,
            'total_tokens': 0,
            'errors_by_type': defaultdict(int)
        }
        
        # Component-level latency tracking
        self.component_latency = {
            'retrieval': [],
            'embedding': [],
            'llm_generation': [],
            'total': []
        }
        
        # System start time
        self.start_time = datetime.now()
        
        if enable_metrics:
            logger.info("Metrics collector initialized")
        else:
            logger.info("Metrics collection disabled")
    
    def record_query(
        self,
        query: str,
        success: bool,
        latency: float,
        cache_hit: bool = False,
        retrieval_scores: Optional[List[float]] = None,
        tokens_used: Optional[int] = None,
        confidence: Optional[float] = None,
        error: Optional[str] = None,
        component_times: Optional[Dict[str, float]] = None
    ):
        """
        Record a query execution
        
        Args:
            query: User query
            success: Whether query succeeded
            latency: Total query latency in seconds
            cache_hit: Whether result came from cache
            retrieval_scores: List of similarity scores for retrieved docs
            tokens_used: Number of tokens used
            confidence: Confidence score (0-1)
            error: Error message if failed
            component_times: Dict of component execution times
        """
        if not self.enable_metrics:
            return
        
        timestamp = datetime.now()
        
        # Update aggregated metrics
        self.metrics['total_queries'] += 1
        if success:
            self.metrics['successful_queries'] += 1
        else:
            self.metrics['failed_queries'] += 1
        
        if cache_hit:
            self.metrics['cache_hits'] += 1
        else:
            self.metrics['cache_misses'] += 1
        
        self.metrics['total_latency'] += latency
        
        if tokens_used:
            self.metrics['total_tokens'] += tokens_used
        
        # Record query details
        query_record = {
            'timestamp': timestamp.isoformat(),
            'query': query[:100],  # Truncate for storage
            'success': success,
            'latency': round(latency, 3),
            'cache_hit': cache_hit,
            'retrieval_scores': retrieval_scores,
            'tokens_used': tokens_used,
            'confidence': confidence,
            'error': error
        }
        
        # Add component times if provided
        if component_times:
            query_record['component_times'] = component_times
            for component, comp_time in component_times.items():
                if component in self.component_latency:
                    self.component_latency[component].append(comp_time)
        
        self.query_history.append(query_record)
        self.component_latency['total'].append(latency)
    
    def record_error(self, error_type: str, error_message: str):
        """Record an error occurrence"""
        if not self.enable_metrics:
            return
        
        self.metrics['errors_by_type'][error_type] += 1
        logger.debug(f"Recorded error: {error_type}")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary metrics
        
        Returns:
            Dict with aggregated metrics and statistics
        """
        if not self.enable_metrics:
            return {'enabled': False}
        
        total = self.metrics['total_queries']
        if total == 0:
            return {
                'enabled': True,
                'total_queries': 0,
                'message': 'No queries processed yet'
            }
        
        # Calculate rates and averages
        success_rate = (self.metrics['successful_queries'] / total) * 100
        cache_hit_rate = (self.metrics['cache_hits'] / total) * 100 if total > 0 else 0.0
        avg_latency = self.metrics['total_latency'] / total
        avg_tokens = self.metrics['total_tokens'] / total if self.metrics['total_tokens'] > 0 else 0
        
        # Latency percentiles
        latencies = [q['latency'] for q in self.query_history if q.get('latency')]
        latency_stats = {}
        if latencies:
            latency_stats = {
                'min': round(min(latencies), 3),
                'max': round(max(latencies), 3),
                'mean': round(statistics.mean(latencies), 3),
                'median': round(statistics.median(latencies), 3),
                'p95': round(statistics.quantiles(latencies, n=20)[18], 3) if len(latencies) > 20 else None,
                'p99': round(statistics.quantiles(latencies, n=100)[98], 3) if len(latencies) > 100 else None
            }
        
        # Component breakdown
        component_breakdown = {}
        for component, times in self.component_latency.items():
            if times:
                component_breakdown[component] = {
                    'mean': round(statistics.mean(times), 3),
                    'median': round(statistics.median(times), 3),
                    'samples': len(times)
                }
        
        # Uptime
        uptime = datetime.now() - self.start_time
        
        return {
            'enabled': True,
            'overview': {
                'total_queries': total,
                'successful': self.metrics['successful_queries'],
                'failed': self.metrics['failed_queries'],
                'success_rate': round(success_rate, 2),
                'uptime_seconds': uptime.total_seconds()
            },
            'cache': {
                'hits': self.metrics['cache_hits'],
                'misses': self.metrics['cache_misses'],
                'hit_rate': round(cache_hit_rate, 2)
            },
            'latency': {
                'average': round(avg_latency, 3),
                **latency_stats
            },
            'components': component_breakdown,
            'tokens': {
                'total': self.metrics['total_tokens'],
                'average_per_query': round(avg_tokens, 1)
            },
            'errors': dict(self.metrics['errors_by_type'])
        }
    
    def get_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent queries with details"""
        if not self.enable_metrics:
            return []
        
        return list(self.query_history)[-limit:]
    
    def get_time_series(self, interval_minutes: int = 5) -> Dict[str, List]:
        """
        Get time-series data for visualization
        
        Args:
            interval_minutes: Bucket size for grouping queries
        
        Returns:
            Dict with timestamps and corresponding metrics
        """
        if not self.enable_metrics or not self.query_history:
            return {'timestamps': [], 'latencies': [], 'success_rates': []}
        
        # Group queries by time interval
        interval = timedelta(minutes=interval_minutes)
        buckets = defaultdict(lambda: {'latencies': [], 'successes': 0, 'total': 0})
        
        for query in self.query_history:
            timestamp = datetime.fromisoformat(query['timestamp'])
            bucket_key = timestamp.replace(second=0, microsecond=0)
            bucket_key = bucket_key.replace(minute=(bucket_key.minute // interval_minutes) * interval_minutes)
            
            buckets[bucket_key]['latencies'].append(query['latency'])
            buckets[bucket_key]['total'] += 1
            if query['success']:
                buckets[bucket_key]['successes'] += 1
        
        # Convert to lists for plotting
        sorted_buckets = sorted(buckets.items())
        timestamps = [bucket[0].isoformat() for bucket in sorted_buckets]
        avg_latencies = [
            round(statistics.mean(bucket[1]['latencies']), 3) 
            for bucket in sorted_buckets
        ]
        success_rates = [
            round((bucket[1]['successes'] / bucket[1]['total']) * 100, 1)
            for bucket in sorted_buckets
        ]
        
        return {
            'timestamps': timestamps,
            'latencies': avg_latencies,
            'success_rates': success_rates
        }
    
    def reset(self):
        """Reset all metrics (useful for testing)"""
        if not self.enable_metrics:
            return
        
        self.query_history.clear()
        self.metrics = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_latency': 0.0,
            'total_tokens': 0,
            'errors_by_type': defaultdict(int)
        }
        self.component_latency = {
            'retrieval': [],
            'embedding': [],
            'llm_generation': [],
            'total': []
        }
        self.start_time = datetime.now()
        logger.info("Metrics reset")


class MetricsManager:
    """
    Singleton metrics manager for global access
    """
    
    _instance: Optional['MetricsManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.collector: Optional[MetricsCollector] = None
        self._initialized = True
    
    def initialize(self, window_size: int = 100, enable_metrics: bool = True):
        """Initialize the metrics collector"""
        self.collector = MetricsCollector(
            window_size=window_size,
            enable_metrics=enable_metrics
        )
    
    def get_collector(self) -> MetricsCollector:
        """Get the metrics collector instance"""
        if self.collector is None:
            # Initialize with defaults if not done yet
            self.initialize()
        return self.collector


# Global metrics manager instance
metrics_manager = MetricsManager()

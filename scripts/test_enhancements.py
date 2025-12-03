"""
Quick diagnostic script to verify enhancements are working
Run this after restarting the system to check configuration
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config
from src.retrieval.query_cache import cache_manager
from src.monitoring.metrics_collector import metrics_manager
from src.generation.confidence_scorer import confidence_manager

print("=" * 70)
print("🔍 PHASE 1 ENHANCEMENTS DIAGNOSTIC")
print("=" * 70)
print()

# Check configuration
print("📝 Configuration Status:")
print(f"   Hybrid Search:        {'✅ ENABLED' if config.ENABLE_HYBRID_SEARCH else '❌ DISABLED'}")
print(f"   Query Cache:          {'✅ ENABLED' if config.ENABLE_QUERY_CACHE else '❌ DISABLED'}")
print(f"   Confidence Scoring:   {'✅ ENABLED' if config.ENABLE_CONFIDENCE_SCORING else '❌ DISABLED'}")
print(f"   Metrics Dashboard:    {'✅ ENABLED' if config.ENABLE_METRICS else '❌ DISABLED'}")
print()

# Check managers initialized
print("🔧 Manager Initialization:")
cache_manager.initialize(
    max_size=config.CACHE_MAX_SIZE,
    ttl_seconds=config.CACHE_TTL_SECONDS,
    enable_cache=config.ENABLE_QUERY_CACHE
)
cache = cache_manager.get_query_cache()
print(f"   Cache Manager:        ✅ Initialized (size={cache.max_size}, TTL={cache.ttl.seconds}s)")

confidence_manager.initialize(enable_scoring=config.ENABLE_CONFIDENCE_SCORING)
scorer = confidence_manager.get_scorer()
print(f"   Confidence Manager:   ✅ Initialized (enabled={scorer.enable_scoring})")

metrics_manager.initialize(
    window_size=config.METRICS_WINDOW_SIZE,
    enable_metrics=config.ENABLE_METRICS
)
metrics = metrics_manager.get_collector()
print(f"   Metrics Manager:      ✅ Initialized (enabled={metrics.enable_metrics}, window={metrics.window_size})")
print()

# Test confidence scoring
if config.ENABLE_CONFIDENCE_SCORING:
    print("🎯 Testing Confidence Scoring:")
    from langchain_core.documents import Document
    
    test_docs = [
        Document(page_content="Test document 1", metadata={'page': 1}),
        Document(page_content="Test document 2", metadata={'page': 2})
    ]
    
    confidence_result = scorer.calculate_confidence(
        query="test query",
        answer="This is a test answer with specific details.",
        retrieved_docs=test_docs,
        retrieval_scores=[0.9, 0.8]
    )
    
    print(f"   Sample confidence:    {confidence_result['overall']:.2f} ({confidence_result['label']})")
    print(f"   Has 'enabled' flag:   {confidence_result.get('enabled', False)}")
    print(f"   Has 'overall' score:  {confidence_result.get('overall') is not None}")
    print()

# Test cache
if config.ENABLE_QUERY_CACHE:
    print("💾 Testing Query Cache:")
    test_result = {'answer': 'test', 'status': 'success', 'time': '25.0s'}
    cache.set("test query", test_result)
    cached = cache.get("test query")
    print(f"   Cache set/get:        {'✅ WORKING' if cached else '❌ FAILED'}")
    stats = cache.get_stats()
    print(f"   Cache stats:          {stats}")
    cache.clear()
    print()

# Test metrics
if config.ENABLE_METRICS:
    print("📊 Testing Metrics Collection:")
    metrics.record_query(
        query="test query",
        success=True,
        latency=1.5,
        cache_hit=False,
        confidence=0.85
    )
    summary = metrics.get_summary()
    print(f"   Metrics enabled:      {summary.get('enabled', False)}")
    print(f"   Queries recorded:     {summary.get('overview', {}).get('total_queries', 0)}")
    print()

print("=" * 70)
print("✅ DIAGNOSTIC COMPLETE")
print("=" * 70)
print()

# Recommendations
print("💡 Recommendations:")
if not config.ENABLE_HYBRID_SEARCH:
    print("   ⚠️  Enable ENABLE_HYBRID_SEARCH=true for better retrieval")
if not config.ENABLE_QUERY_CACHE:
    print("   ⚠️  Enable ENABLE_QUERY_CACHE=true for 50-100x speedup on repeated queries")
if not config.ENABLE_CONFIDENCE_SCORING:
    print("   ⚠️  Enable ENABLE_CONFIDENCE_SCORING=true to show reliability indicators")
if not config.ENABLE_METRICS:
    print("   ⚠️  Enable ENABLE_METRICS=true for performance monitoring")

all_enabled = all([
    config.ENABLE_HYBRID_SEARCH,
    config.ENABLE_QUERY_CACHE,
    config.ENABLE_CONFIDENCE_SCORING,
    config.ENABLE_METRICS
])

if all_enabled:
    print("   ✅ All enhancements enabled! System is fully optimized.")
else:
    print("   📝 Edit .env file to enable features, then restart the system")

print()

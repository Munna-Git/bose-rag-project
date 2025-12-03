"""
Global configuration settings
"""
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    """Configuration class"""
    
    # Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    DOCS_DIR = DATA_DIR / "documents"
    VECTOR_DB_DIR = DATA_DIR / "vector_db"
    
    # Ensure directories exist
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
    
    # Model Configuration
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
    OLLAMA_NUM_THREADS = int(os.getenv("OLLAMA_NUM_THREADS", "4"))
    OLLAMA_NUM_GPU = int(os.getenv("OLLAMA_NUM_GPU", "0"))  # 0 = CPU only
    
    # Processing Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))
    
    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Generation Configuration
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "512"))
    RESPONSE_TIMEOUT = int(os.getenv("RESPONSE_TIMEOUT", "60"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = BASE_DIR / "rag_system.log"
    
    # Enhancement Features (Phase 1 - Optional, backward compatible)
    # Hybrid Search: Combines vector search (semantic) with BM25 (keyword)
    ENABLE_HYBRID_SEARCH = os.getenv("ENABLE_HYBRID_SEARCH", "false").lower() == "true"
    HYBRID_SEARCH_ALPHA = float(os.getenv("HYBRID_SEARCH_ALPHA", "0.5"))  # 0.5 = equal weight
    
    # Query Caching: Cache results for repeated queries
    ENABLE_QUERY_CACHE = os.getenv("ENABLE_QUERY_CACHE", "false").lower() == "true"
    CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "100"))
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour
    
    # Confidence Scoring: Reliability indicators for answers
    ENABLE_CONFIDENCE_SCORING = os.getenv("ENABLE_CONFIDENCE_SCORING", "false").lower() == "true"
    
    # Metrics Dashboard: Performance tracking and monitoring
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "false").lower() == "true"
    METRICS_WINDOW_SIZE = int(os.getenv("METRICS_WINDOW_SIZE", "100"))

config = Config()

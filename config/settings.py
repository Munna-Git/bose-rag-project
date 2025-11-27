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

config = Config()

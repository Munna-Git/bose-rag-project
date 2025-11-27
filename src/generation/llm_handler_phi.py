"""
LLM Handler for Phi-2 via Ollama
Optimized for speed and memory efficiency
"""
import requests
import time
from typing import Optional
from langchain.llms import Ollama
from config.settings import config
from config.constants import ErrorType
from src.error_handling.handlers import error_handler
from src.error_handling.logger import logger


class Phi2Handler:
    """
    Handle Phi-2 LLM operations via Ollama
    
    Features:
    - Fast inference on CPU (2-3 seconds)
    - Low memory (1.6GB)
    - Graceful error handling
    - Retry mechanism
    """
    
    def __init__(self):
        """Initialize Phi-2 handler"""
        
        self.model_name = config.OLLAMA_MODEL
        self.base_url = config.OLLAMA_BASE_URL
        self.temperature = config.OLLAMA_TEMPERATURE
        self.max_tokens = config.MAX_TOKENS
        self.timeout = config.RESPONSE_TIMEOUT
        self.model = None
        self.retry_count = 0
        self.max_retries = 3
        
        logger.info(f"Initializing {self.model_name} handler...")
        self._initialize()
    
    def _initialize(self):
        """Initialize Phi-2 with error handling"""
        
        try:
            # Check Ollama running
            if not self._check_ollama_running():
                error_handler.handle_error(
                    ErrorType.LLM_ERROR,
                    Exception("Ollama not running"),
                    context={"url": self.base_url},
                    fallback_fn=lambda: self._suggest_start_ollama()
                )
                raise RuntimeError(
                    "❌ Ollama not running!\n"
                    "Start it with: ollama serve"
                )
            
            # Check model exists
            if not self._check_model_exists():
                error_handler.handle_error(
                    ErrorType.LLM_ERROR,
                    Exception(f"Model {self.model_name} not found"),
                    context={"model": self.model_name},
                    fallback_fn=lambda: self._suggest_pull_model()
                )
                raise RuntimeError(
                    f"❌ Model '{self.model_name}' not found!\n"
                    f"Pull it with: ollama pull {self.model_name}"
                )
            
            # Initialize LLM
            self.model = Ollama(
                base_url=self.base_url,
                model=self.model_name,
                temperature=self.temperature,
                num_ctx=2048,
                num_threads=config.OLLAMA_NUM_THREADS,
                num_gpu=config.OLLAMA_NUM_GPU
            )
            
            logger.info(f"✅ {self.model_name} initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize {self.model_name}: {str(e)}")
            raise
    
    def _check_ollama_running(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=2
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama check failed: {str(e)}")
            return False
    
    def _check_model_exists(self) -> bool:
        """Check if Phi-2 model is downloaded"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            data = response.json()
            models = [m['name'].split(':') for m in data.get('models', [])]
            exists = self.model_name in models
            
            if not exists:
                logger.warning(f"Model {self.model_name} not found. Available: {models}")
            
            return exists
        except Exception as e:
            logger.error(f"Failed to check models: {str(e)}")
            return False
    
    def _suggest_start_ollama(self):
        """Suggest how to start Ollama"""
        logger.info("💡 To start Ollama, run: ollama serve")
        return False
    
    def _suggest_pull_model(self):
        """Suggest how to pull model"""
        logger.info(f"💡 To pull {self.model_name}, run: ollama pull {self.model_name}")
        return False
    
    def generate(self, prompt: str, retries: int = 0) -> str:
        """
        Generate response using Phi-2
        
        Args:
            prompt: Input prompt
            retries: Retry count (internal)
        
        Returns:
            Generated response
        """
        
        if retries > self.max_retries:
            error_msg = f"Failed after {self.max_retries} retries"
            logger.error(error_msg)
            return error_msg
        
        try:
            logger.debug(f"Generating response (attempt {retries + 1})...")
            
            start_time = time.time()
            response = self.model.predict(
                prompt,
                num_predict=self.max_tokens
            )
            elapsed = time.time() - start_time
            
            logger.info(f"Response generated in {elapsed:.2f}s")
            return response.strip()
        
        except requests.Timeout:
            logger.warning(f"Timeout on attempt {retries + 1}, retrying...")
            time.sleep(2)  # Wait before retry
            return self.generate(prompt, retries + 1)
        
        except Exception as e:
            logger.error(f"Generation error: {str(e)}")
            
            error_handler.handle_error(
                ErrorType.LLM_ERROR,
                e,
                context={"attempt": retries + 1}
            )
            
            if retries < self.max_retries:
                logger.info(f"Retrying... (attempt {retries + 2})")
                time.sleep(2)
                return self.generate(prompt, retries + 1)
            
            return (
                "I encountered an error generating a response. "
                "Please check if Ollama is running and try again."
            )
    
    def get_model_info(self) -> dict:
        """Get model information"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            data = response.json()
            
            for model in data.get('models', []):
                if self.model_name in model['name']:
                    return {
                        'name': model['name'],
                        'size': model.get('size', 'Unknown'),
                        'modified_at': model.get('modified_at', 'Unknown'),
                        'status': 'ready'
                    }
            
            return {'status': 'not_found', 'model': self.model_name}
        
        except Exception as e:
            logger.error(f"Failed to get model info: {str(e)}")
            return {'status': 'error', 'error': str(e)}

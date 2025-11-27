"""
Embedding generation
"""
from langchain.embeddings import HuggingFaceEmbeddings
from config.settings import config
from src.error_handling.logger import logger


class EmbeddingGenerator:
    """Generate embeddings"""
    
    def __init__(self):
        try:
            logger.info(f"Initializing embeddings with {config.EMBEDDING_MODEL}...")
            
            self.embeddings = HuggingFaceEmbeddings(
                model_name=config.EMBEDDING_MODEL
            )
            
            logger.info("✅ Embeddings initialized")
        
        except Exception as e:
            logger.error(f"Embedding initialization failed: {str(e)}")
            raise
    
    def embed_text(self, text: str):
        """Embed single text"""
        return self.embeddings.embed_query(text)
    
    def embed_texts(self, texts: list):
        """Embed multiple texts"""
        return self.embeddings.embed_documents(texts)

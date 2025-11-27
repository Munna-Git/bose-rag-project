"""
ChromaDB manager with metadata support
"""
from typing import List, Dict
import chromadb
from langchain.schema import Document
from langchain.embeddings import HuggingFaceEmbeddings
from config.settings import config
from src.error_handling.logger import logger


class EnhancedChromaDB:
    """Enhanced ChromaDB with metadata support"""
    
    def __init__(self):
        """Initialize ChromaDB"""
        
        try:
            logger.info("Initializing ChromaDB...")
            
            # Initialize embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name=config.EMBEDDING_MODEL
            )
            
            # Initialize ChromaDB
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection(
                name="bose_documents",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("✅ ChromaDB initialized")
        
        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Document]):
        """Add documents to vector store"""
        
        try:
            logger.info(f"Adding {len(documents)} documents...")
            
            for i, doc in enumerate(documents):
                # Generate embedding
                embedding = self.embeddings.embed_query(doc.page_content)
                
                # Add to collection
                self.collection.add(
                    ids=[f"doc_{i}"],
                    embeddings=[embedding],
                    documents=[doc.page_content],
                    metadatas=[doc.metadata]
                )
            
            logger.info(f"✅ {len(documents)} documents added")
        
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            raise
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search documents"""
        
        try:
            query_embedding = self.embeddings.embed_query(query)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k
            )
            
            return results
        
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise
    
    def load_existing(self):
        """Load existing collection"""
        
        try:
            self.collection = self.client.get_collection(
                name="bose_documents"
            )
            logger.info("✅ Loaded existing collection")
        
        except Exception as e:
            logger.warning(f"No existing collection: {str(e)}")

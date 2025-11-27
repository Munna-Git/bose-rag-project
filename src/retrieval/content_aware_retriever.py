"""
Content-aware retriever with intent detection
"""
from typing import List
from langchain.schema import Document
from src.vector_store.chromadb_manager import EnhancedChromaDB
from src.error_handling.logger import logger


class ContentAwareRetriever:
    """Retrieve documents with content type awareness"""
    
    def __init__(self, vector_store: EnhancedChromaDB):
        self.vector_store = vector_store
    
    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """Retrieve relevant documents"""
        
        try:
            # Detect intent
            intent = self._detect_intent(query)
            logger.debug(f"Query intent: {intent}")
            
            # Search
            results = self.vector_store.search(query, k=k)
            
            # Convert to Document objects
            documents = []
            for i, (doc_text, metadata) in enumerate(
                zip(results['documents'], results['metadatas'])
            ):
                doc = Document(
                    page_content=doc_text,
                    metadata=metadata
                )
                documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} documents")
            return documents
        
        except Exception as e:
            logger.error(f"Retrieval failed: {str(e)}")
            return []
    
    def _detect_intent(self, query: str) -> str:
        """Detect query intent"""
        
        spec_words = ["specification", "spec", "value", "rating", "snr", "response"]
        proc_words = ["how", "configure", "setup", "install"]
        
        query_lower = query.lower()
        
        if any(w in query_lower for w in spec_words):
            return "specification"
        elif any(w in query_lower for w in proc_words):
            return "procedure"
        else:
            return "general"

"""
Content-aware retriever with intent detection
"""
from typing import List
from langchain_core.documents import Document
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

            # Convert to Document objects (no reranking; preserve vector order)
            documents: List[Document] = []
            if results.get('documents') and len(results['documents']) > 0:
                docs_list = results['documents'][0]
                metas_list = results.get('metadatas', [[]])[0] if results.get('metadatas') else [{}] * len(docs_list)

                for doc_text, metadata in zip(docs_list, metas_list):
                    doc = Document(
                        page_content=doc_text,
                        metadata=metadata or {}
                    )
                    documents.append(doc)

            logger.info(f"Retrieved {len(documents)} documents for query")
            if len(documents) == 0:
                logger.warning(f"No documents retrieved for query: '{query[:50]}...'")
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

    

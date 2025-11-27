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

            # Prepare lists
            documents: List[Document] = []
            if results.get('documents') and len(results['documents']) > 0:
                docs_list = results['documents'][0]
                metas_list = results.get('metadatas', [[]])[0] if results.get('metadatas') else [{}] * len(docs_list)
                dists_list = results.get('distances', [[]])[0] if results.get('distances') else [1.0] * len(docs_list)

                # Keyword overlap for reranking
                q_low = query.lower()
                keywords = self._keywords_for_rerank(q_low, intent)

                scored = []
                for doc_text, metadata, dist in zip(docs_list, metas_list, dists_list):
                    text_low = (doc_text or '').lower()
                    meta_low = ' '.join(str(v).lower() for v in (metadata or {}).values())
                    overlap = sum(1 for kw in keywords if kw in text_low or kw in meta_low)
                    score = (overlap * 2.0) - float(dist if dist is not None else 1.0)
                    scored.append((score, doc_text, metadata or {}, float(dist if dist is not None else 1.0), overlap))

                # Sort by score desc and trim to k
                scored.sort(key=lambda x: x[0], reverse=True)
                scored = scored[:k]

                for _, doc_text, metadata, dist, overlap in scored:
                    # Attach distance and overlap for downstream confidence and display
                    metadata = dict(metadata)
                    metadata['distance'] = dist
                    metadata['overlap'] = overlap
                    documents.append(Document(page_content=doc_text, metadata=metadata))

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

    def _keywords_for_rerank(self, q_low: str, intent: str) -> List[str]:
        base = []
        for token in ['ex-1280c', 'ex1280c', 'analog', 'inputs', 'input channels', 'mic/line', 'euroblock', 'dante', 'usb', 'voip', 'aec']:
            if token in q_low:
                base.append(token)
        if intent == 'spec':
            base += ['max', 'maximum', 'count', 'qty', 'number', 'analog inputs', 'mic inputs', 'line inputs']
        elif intent == 'procedure':
            base += ['configure', 'setup', 'install', 'connect']
        return list(set(base))

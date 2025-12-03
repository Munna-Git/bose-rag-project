"""
Hybrid retriever combining vector search (semantic) with BM25 (keyword)
Improves retrieval for exact matches (model numbers, specs) while preserving semantic understanding
"""
from typing import List, Dict, Optional
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
import numpy as np

from src.vector_store.chromadb_manager import EnhancedChromaDB
from src.error_handling.logger import logger


class HybridRetriever:
    """
    Hybrid retrieval combining:
    - Vector search (semantic similarity)
    - BM25 (keyword/lexical matching)
    
    Benefits:
    - Captures both meaning and exact terms
    - Better for model numbers, specs, precise terminology
    - Configurable weighting between methods
    """
    
    def __init__(
        self, 
        vector_store: EnhancedChromaDB,
        alpha: float = 0.5,
        enable_hybrid: bool = True
    ):
        """
        Initialize hybrid retriever
        
        Args:
            vector_store: Vector database for semantic search
            alpha: Weight for vector search (1-alpha for BM25)
                  0.5 = equal weight (default)
                  0.7 = prefer semantic
                  0.3 = prefer keyword
            enable_hybrid: If False, falls back to pure vector search (backward compatible)
        """
        self.vector_store = vector_store
        self.alpha = alpha
        self.enable_hybrid = enable_hybrid
        
        # BM25 index (lazy initialization)
        self.bm25_index: Optional[BM25Okapi] = None
        self.indexed_docs: List[Document] = []
        
        if enable_hybrid:
            self._build_bm25_index()
            logger.info(f"Hybrid retriever initialized (alpha={alpha}, hybrid={enable_hybrid})")
        else:
            logger.info("Hybrid retriever initialized in vector-only mode (backward compatible)")
    
    def _build_bm25_index(self):
        """Build BM25 index from all documents in vector store"""
        try:
            # Get all documents from ChromaDB
            results = self.vector_store.collection.get()
            
            if not results['documents']:
                logger.warning("No documents found in vector store for BM25 indexing")
                return
            
            # Create Document objects
            self.indexed_docs = []
            for i, doc_text in enumerate(results['documents']):
                metadata = results['metadatas'][i] if results['metadatas'] else {}
                self.indexed_docs.append(Document(
                    page_content=doc_text,
                    metadata=metadata
                ))
            
            # Tokenize for BM25
            tokenized_docs = [doc.page_content.lower().split() for doc in self.indexed_docs]
            self.bm25_index = BM25Okapi(tokenized_docs)
            
            logger.info(f"BM25 index built with {len(self.indexed_docs)} documents")
        
        except Exception as e:
            logger.error(f"Failed to build BM25 index: {str(e)}")
            self.bm25_index = None
    
    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieve documents using hybrid search
        
        Args:
            query: User query
            k: Number of documents to retrieve
        
        Returns:
            List of documents ranked by hybrid score
        """
        # If hybrid disabled or BM25 not available, use pure vector search
        if not self.enable_hybrid or self.bm25_index is None:
            return self._vector_search(query, k)
        
        try:
            # Get candidates from both methods (retrieve more for fusion)
            k_candidates = min(k * 3, len(self.indexed_docs))
            
            vector_docs = self._vector_search(query, k_candidates)
            bm25_docs = self._bm25_search(query, k_candidates)
            
            # Hybrid scoring and fusion
            hybrid_docs = self._reciprocal_rank_fusion(vector_docs, bm25_docs, k)
            
            logger.info(f"Hybrid retrieval: {len(hybrid_docs)} documents (alpha={self.alpha})")
            return hybrid_docs
        
        except Exception as e:
            logger.error(f"Hybrid search failed, falling back to vector search: {str(e)}")
            return self._vector_search(query, k)
    
    def _vector_search(self, query: str, k: int) -> List[Document]:
        """Vector similarity search"""
        try:
            results = self.vector_store.search(query, k=k)
            
            documents: List[Document] = []
            if results.get('documents') and len(results['documents']) > 0:
                docs_list = results['documents'][0]
                metas_list = results.get('metadatas', [[]])[0] if results.get('metadatas') else [{}] * len(docs_list)
                distances = results.get('distances', [[]])[0] if results.get('distances') else [1.0] * len(docs_list)
                
                for doc_text, metadata, distance in zip(docs_list, metas_list, distances):
                    doc = Document(
                        page_content=doc_text,
                        metadata={**(metadata or {}), 'vector_score': 1.0 - distance}
                    )
                    documents.append(doc)
            
            return documents
        
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            return []
    
    def _bm25_search(self, query: str, k: int) -> List[Document]:
        """BM25 keyword search"""
        try:
            if not self.bm25_index:
                return []
            
            # Tokenize query
            tokenized_query = query.lower().split()
            
            # Get BM25 scores
            scores = self.bm25_index.get_scores(tokenized_query)
            
            # Get top-k indices
            top_k_indices = np.argsort(scores)[-k:][::-1]
            
            # Create documents with BM25 scores
            documents = []
            for idx in top_k_indices:
                if scores[idx] > 0:  # Only include non-zero scores
                    doc = self.indexed_docs[idx]
                    # Add BM25 score to metadata
                    doc_copy = Document(
                        page_content=doc.page_content,
                        metadata={**doc.metadata, 'bm25_score': float(scores[idx])}
                    )
                    documents.append(doc_copy)
            
            return documents
        
        except Exception as e:
            logger.error(f"BM25 search failed: {str(e)}")
            return []
    
    def _reciprocal_rank_fusion(
        self, 
        vector_docs: List[Document], 
        bm25_docs: List[Document],
        k: int
    ) -> List[Document]:
        """
        Reciprocal Rank Fusion (RRF) for combining rankings
        
        RRF formula: score(d) = sum(1 / (rank_i + 60))
        - Reduces impact of outlier ranks
        - Fair fusion of different scoring scales
        """
        # Create document ID mapping (use content hash)
        doc_scores: Dict[str, Dict] = {}
        
        # Add vector search ranks
        for rank, doc in enumerate(vector_docs, 1):
            doc_id = hash(doc.page_content)
            if doc_id not in doc_scores:
                doc_scores[doc_id] = {
                    'doc': doc,
                    'vector_rank': rank,
                    'bm25_rank': None,
                    'rrf_score': 0.0
                }
            doc_scores[doc_id]['vector_rank'] = rank
        
        # Add BM25 ranks
        for rank, doc in enumerate(bm25_docs, 1):
            doc_id = hash(doc.page_content)
            if doc_id not in doc_scores:
                doc_scores[doc_id] = {
                    'doc': doc,
                    'vector_rank': None,
                    'bm25_rank': rank,
                    'rrf_score': 0.0
                }
            else:
                doc_scores[doc_id]['bm25_rank'] = rank
        
        # Calculate RRF scores
        for doc_id, info in doc_scores.items():
            rrf_score = 0.0
            
            # Vector contribution (weighted by alpha)
            if info['vector_rank'] is not None:
                rrf_score += self.alpha * (1.0 / (info['vector_rank'] + 60))
            
            # BM25 contribution (weighted by 1-alpha)
            if info['bm25_rank'] is not None:
                rrf_score += (1.0 - self.alpha) * (1.0 / (info['bm25_rank'] + 60))
            
            info['rrf_score'] = rrf_score
        
        # Sort by RRF score and take top-k
        sorted_docs = sorted(
            doc_scores.values(), 
            key=lambda x: x['rrf_score'], 
            reverse=True
        )[:k]
        
        # Return documents with hybrid scores in metadata
        result_docs = []
        for item in sorted_docs:
            doc = item['doc']
            doc_with_score = Document(
                page_content=doc.page_content,
                metadata={
                    **doc.metadata,
                    'hybrid_score': item['rrf_score'],
                    'vector_rank': item['vector_rank'],
                    'bm25_rank': item['bm25_rank']
                }
            )
            result_docs.append(doc_with_score)
        
        return result_docs
    
    def _detect_intent(self, query: str) -> str:
        """Detect query intent (for backward compatibility with ContentAwareRetriever)"""
        spec_words = ["specification", "spec", "value", "rating", "snr", "response"]
        proc_words = ["how", "configure", "setup", "install"]
        
        query_lower = query.lower()
        
        if any(w in query_lower for w in spec_words):
            return "specification"
        elif any(w in query_lower for w in proc_words):
            return "procedure"
        else:
            return "general"

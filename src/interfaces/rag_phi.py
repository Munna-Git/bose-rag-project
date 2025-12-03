"""
Complete RAG system using Phi-2
Main orchestrator class with optional enhancements (Phase 1)
"""
from typing import List, Optional, Dict
import time
from src.document_processing.router import ProcessingRouter
from src.vector_store.chromadb_manager import EnhancedChromaDB
from src.retrieval.content_aware_retriever import ContentAwareRetriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.query_cache import cache_manager
from src.generation.prompt_builder import PromptBuilder
from src.generation.llm_handler_phi import Phi2Handler
from src.generation.confidence_scorer import confidence_manager
from src.monitoring.metrics_collector import metrics_manager
from src.error_handling.logger import logger
from src.error_handling.handlers import error_handler
from config.constants import ErrorType
from config.settings import config


class BoseRAGPhi:
    """
    Complete RAG system using Phi-2
    Memory-efficient (1.6GB), fast (2-3s per query)
    
    Phase 1 Enhancements (optional, backward compatible):
    - Hybrid Search (BM25 + Vector)
    - Query Caching (LRU)
    - Confidence Scoring
    - Metrics Dashboard
    """
    
    def __init__(self):
        """Initialize RAG system with optional enhancements"""
        
        logger.info("=" * 70)
        logger.info("Initializing Bose RAG with Phi-2...")
        logger.info("=" * 70)
        
        try:
            # Initialize core components
            self.vector_store = EnhancedChromaDB()
            logger.info("SUCCESS: Vector store initialized")
            
            self.prompt_builder = PromptBuilder()
            logger.info("SUCCESS: Prompt builder initialized")
            
            self.llm = Phi2Handler()
            logger.info("SUCCESS: Phi-2 LLM initialized")
            
            self.router = ProcessingRouter()
            
            # Initialize enhancements (optional, backward compatible)
            self._init_enhancements()
            
            # Check if database has documents and initialize retriever
            doc_count = self.vector_store.collection.count()
            if doc_count > 0:
                # Use hybrid retriever if enabled, else standard
                if config.ENABLE_HYBRID_SEARCH:
                    self.retriever = HybridRetriever(
                        self.vector_store,
                        alpha=config.HYBRID_SEARCH_ALPHA,
                        enable_hybrid=True
                    )
                    logger.info(f"SUCCESS: Hybrid retriever initialized (alpha={config.HYBRID_SEARCH_ALPHA})")
                else:
                    self.retriever = ContentAwareRetriever(self.vector_store)
                    logger.info("SUCCESS: Standard retriever initialized")
                
                logger.info(f"SUCCESS: Loaded existing collection with {doc_count} documents")
            else:
                self.retriever = None
                logger.warning("WARNING: No documents in database. Process documents first.")
            
            logger.info("SUCCESS: RAG system fully initialized")
            self._log_enhancement_status()
            logger.info("=" * 70)
        
        except Exception as e:
            logger.error(f"ERROR: Initialization failed: {str(e)}")
            error_handler.handle_error(
                ErrorType.PROCESSING_ERROR,
                e,
                context={"stage": "initialization"}
            )
            raise
    
    def _init_enhancements(self):
        """Initialize optional enhancement features"""
        # Query caching
        cache_manager.initialize(
            max_size=config.CACHE_MAX_SIZE,
            ttl_seconds=config.CACHE_TTL_SECONDS,
            enable_cache=config.ENABLE_QUERY_CACHE
        )
        self.cache = cache_manager.get_query_cache()
        
        # Confidence scoring
        confidence_manager.initialize(
            enable_scoring=config.ENABLE_CONFIDENCE_SCORING
        )
        self.confidence_scorer = confidence_manager.get_scorer()
        
        # Metrics collection
        metrics_manager.initialize(
            window_size=config.METRICS_WINDOW_SIZE,
            enable_metrics=config.ENABLE_METRICS
        )
        self.metrics = metrics_manager.get_collector()
    
    def _log_enhancement_status(self):
        """Log status of optional enhancements"""
        enhancements = []
        if config.ENABLE_HYBRID_SEARCH:
            enhancements.append(f"Hybrid Search (α={config.HYBRID_SEARCH_ALPHA})")
        if config.ENABLE_QUERY_CACHE:
            enhancements.append(f"Query Cache (size={config.CACHE_MAX_SIZE})")
        if config.ENABLE_CONFIDENCE_SCORING:
            enhancements.append("Confidence Scoring")
        if config.ENABLE_METRICS:
            enhancements.append("Metrics Dashboard")
        
        if enhancements:
            logger.info(f"Enhancements enabled: {', '.join(enhancements)}")
        else:
            logger.info("Enhancements disabled (standard mode)")
    
    def process_documents(self, pdf_paths: List[str]) -> Dict:
        """
        Process PDF documents with error handling
        
        Args:
            pdf_paths: List of PDF file paths
        
        Returns:
            Processing result dictionary
        """
        
        logger.info(f"Processing {len(pdf_paths)} document(s)...")
        
        all_chunks = []
        processed_count = 0
        failed_count = 0
        
        for pdf_path in pdf_paths:
            try:
                logger.info(f"Processing: {pdf_path}")
                
                chunks = self.router.process_pdf(pdf_path)
                all_chunks.extend(chunks)
                processed_count += 1
                
                logger.info(f"SUCCESS: {pdf_path}: {len(chunks)} chunks extracted")
            
            except Exception as e:
                logger.error(f"ERROR: Failed to process {pdf_path}: {str(e)}")
                failed_count += 1
                
                error_handler.handle_error(
                    ErrorType.PROCESSING_ERROR,
                    e,
                    context={"file": pdf_path}
                )
        
        if not all_chunks:
            logger.warning("WARNING: No chunks extracted from any document")
            return {
                'status': 'failed',
                'total_chunks': 0,
                'documents_processed': processed_count,
                'documents_failed': failed_count,
                'error': 'No content extracted from documents'
            }
        
        try:
            # Store in vector DB
            logger.info(f"Storing {len(all_chunks)} chunks...")
            self.vector_store.add_documents(all_chunks)
            
            # Initialize/rebuild retriever (hybrid if enabled)
            if config.ENABLE_HYBRID_SEARCH:
                self.retriever = HybridRetriever(
                    self.vector_store,
                    alpha=config.HYBRID_SEARCH_ALPHA,
                    enable_hybrid=True
                )
                logger.info("SUCCESS: Hybrid retriever rebuilt with new documents")
            else:
                self.retriever = ContentAwareRetriever(self.vector_store)
                logger.info("SUCCESS: Standard retriever initialized with new documents")
            
            logger.info(f"SUCCESS: Processing complete: {len(all_chunks)} chunks stored")
            
            return {
                'status': 'success',
                'total_chunks': len(all_chunks),
                'documents_processed': processed_count,
                'documents_failed': failed_count
            }
        
        except Exception as e:
            logger.error(f"ERROR: Storage failed: {str(e)}")
            error_handler.handle_error(
                ErrorType.PROCESSING_ERROR,
                e,
                context={"stage": "storage", "chunks": len(all_chunks)}
            )
            
            return {
                'status': 'partial_failure',
                'total_chunks': len(all_chunks),
                'documents_processed': processed_count,
                'documents_failed': failed_count,
                'storage_error': str(e)
            }
    
    def answer_query(self, query: str, verbose: bool = False) -> Dict:
        """
        Answer user query with comprehensive error handling and optional enhancements
        
        Args:
            query: User question
            verbose: Show intermediate steps
        
        Returns:
            Result dictionary with answer, sources, metadata, and optional confidence
        """
        
        start_time = time.time()
        cache_hit = False
        component_times = {}
        
        try:
            logger.debug(f"Query: {query}")
            
            # Check initialization
            if not self.retriever:
                logger.warning("WARNING: No documents processed yet")
                result = {
                    'status': 'error',
                    'query': query,
                    'answer': 'Please process documents first using process_documents()',
                    'sources': [],
                    'time': f"{time.time() - start_time:.2f}s",
                    'error': 'No documents loaded'
                }
                self.metrics.record_query(query, False, time.time() - start_time, error='No documents loaded')
                return result
            
            # Detect off-topic queries (before retrieval to save time)
            if self._is_off_topic(query):
                logger.info(f"Off-topic query detected: {query}")
                result = {
                    'status': 'success',
                    'query': query,
                    'answer': 'I am a technical assistant for Bose Professional Audio equipment. I can only answer questions about Bose audio products, specifications, installation, and troubleshooting. Please ask me about Bose audio systems.',
                    'sources': [],
                    'model': 'phi-2',
                    'time': f"{time.time() - start_time:.2f}s"
                }
                if config.ENABLE_CONFIDENCE_SCORING:
                    result['confidence'] = {
                        'overall': 0.0,
                        'label': 'very_low',
                        'breakdown': {'retrieval': 0.0, 'grounding': 0.0, 'specificity': 0.0, 'uncertainty': 0.0},
                        'explanation': 'Off-topic query - not related to Bose audio equipment.',
                        'enabled': True
                    }
                self.metrics.record_query(query, True, time.time() - start_time)
                return result
            
            # Check cache first (if enabled)
            cached_result = self.cache.get(query)
            if cached_result:
                cache_hit = True
                cache_hit_time = time.time() - start_time
                # Update cache indicators and timing
                cached_result['cache_hit'] = True
                cached_result['time'] = f"{cache_hit_time:.2f}s"
                self.metrics.record_query(query, True, cache_hit_time, cache_hit=True)
                logger.info(f"Cache HIT: Query answered in {cache_hit_time:.2f}s")
                return cached_result
            
            if verbose:
                logger.info(f"Step 1: Retrieving documents...")
            
            # Retrieve documents
            retrieval_start = time.time()
            docs = self.retriever.retrieve(query, k=5)
            retrieval_time = time.time() - retrieval_start
            component_times['retrieval'] = retrieval_time
            logger.info(f"Retrieval completed in {retrieval_time:.2f}s")
            
            if not docs:
                logger.warning(f"WARNING: No relevant documents found for query: {query}")
                result = {
                    'status': 'no_context',
                    'query': query,
                    'answer': (
                        "No relevant information found in the documents. "
                        "Try rephrasing your question or ask about: "
                        "specifications, installation, configuration, or features."
                    ),
                    'sources': [],
                    'time': f"{time.time() - start_time:.2f}s",
                    'cache_hit': False
                }
                self.metrics.record_query(query, False, time.time() - start_time, 
                                         component_times=component_times)
                return result
            
            # Extract retrieval scores for confidence calculation
            retrieval_scores = [doc.metadata.get('vector_score', 0.5) for doc in docs]
            
            if verbose:
                logger.info(f"SUCCESS: Retrieved {len(docs)} relevant documents in {retrieval_time:.2f}s")
                logger.info(f"Step 2: Building prompt...")
            
            # Build prompt
            prompt_start = time.time()
            prompt = self.prompt_builder.build_prompt(query, docs)
            prompt_time = time.time() - prompt_start
            component_times['prompt'] = prompt_time
            logger.info(f"Prompt built in {prompt_time:.2f}s")
            
            if verbose:
                logger.info(f"Step 3: Generating answer with Phi-2...")
            
            # Generate answer
            generation_start = time.time()
            answer = self.llm.generate(prompt)
            generation_time = time.time() - generation_start
            component_times['llm_generation'] = generation_time
            logger.info(f"LLM generation completed in {generation_time:.2f}s")
            
            if verbose:
                logger.info(f"SUCCESS: Answer generated")
            
            # Format response
            elapsed_time = time.time() - start_time
            
            # Build sources
            sources = []
            for doc in docs:
                sources.append({
                    'page': doc.metadata.get('page'),
                    'content_type': doc.metadata.get('content_type'),
                    'source': doc.metadata.get('source')
                })
            
            # Calculate confidence score (if enabled)
            confidence = None
            if config.ENABLE_CONFIDENCE_SCORING:
                logger.info("Calculating confidence score...")
                confidence = self.confidence_scorer.calculate_confidence(
                    query, answer, docs, retrieval_scores
                )
                logger.info(f"Confidence calculated: {confidence}")
            else:
                logger.debug("Confidence scoring disabled in config")
            
            result = {
                'status': 'success',
                'query': query,
                'answer': answer,
                'sources': sources,
                'model': 'phi-2',
                'time': f"{elapsed_time:.2f}s",
                'cache_hit': False
            }
            
            # Add confidence if calculated
            if confidence:
                logger.info(f"Adding confidence to result: {confidence}")
                result['confidence'] = confidence
                result['confidence_recommendation'] = self.confidence_scorer.get_recommendation(confidence)
            else:
                logger.warning("No confidence score to add to result")
            
            # Cache result (if enabled)
            if config.ENABLE_QUERY_CACHE:
                self.cache.set(query, result)
            
            # Record metrics (if enabled)
            self.metrics.record_query(
                query, 
                True, 
                elapsed_time,
                cache_hit=False,
                retrieval_scores=retrieval_scores,
                confidence=confidence.get('overall') if confidence else None,
                component_times=component_times
            )
            
            logger.info(f"SUCCESS: Query answered in {elapsed_time:.2f}s")
            
            return result
        
        except Exception as e:
            logger.error(f"ERROR: Query processing failed: {str(e)}")
            
            error_handler.handle_error(
                ErrorType.RETRIEVAL_ERROR,
                e,
                context={'query': query}
            )
            
            self.metrics.record_query(query, False, time.time() - start_time, 
                                     error=str(e), component_times=component_times)
            
            return {
                'status': 'error',
                'query': query,
                'answer': f"Error processing query: {str(e)}",
                'sources': [],
                'time': f"{time.time() - start_time:.2f}s",
                'error': str(e),
                'cache_hit': False
            }
    
    def interactive_session(self):
        """Interactive Q&A session with error handling"""
        
        if not self.retriever:
            logger.error("ERROR: No documents loaded. Run process_documents() first.")
            print("ERROR: Please load documents first!")
            return
        
        print("\n" + "=" * 70)
        print("BOSE TECHNICAL SPECS Q&A (Phi-2)")
        print("=" * 70)
        print(f"Model: Phi-2 | Privacy: 100% Local | Speed: Fast")
        print("Type 'quit', 'exit', or 'q' to exit\n")
        
        query_count = 0
        
        while True:
            try:
                query = input("Your question: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break
                
                if not query:
                    print("Please enter a question.\n")
                    continue
                
                query_count += 1
                logger.info(f"Query #{query_count}: {query}")
                
                # Get answer
                result = self.answer_query(query, verbose=False)
                
                # Display result
                print(f"\nAnswer:")
                print(f"{result['answer']}\n")
                
                if result['sources']:
                    print(f"Sources ({len(result['sources'])} documents):")
                    for i, src in enumerate(result['sources'], 1):
                        print(f"   {i}. Page {src['page']} ({src['content_type']}) - {src['source']}")
                
                print(f"Time: {result['time']}")
                print("-" * 70 + "\n")
            
            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            
            except Exception as e:
                logger.error(f"Unexpected error in interactive session: {str(e)}")
                print(f"Error: {str(e)}")
                print("Continuing...\n")
    
    def _is_off_topic(self, query: str) -> bool:
        """Detect if query is completely off-topic (not audio-related)"""
        query_lower = query.lower()
        
        # Audio/equipment related keywords - if ANY present, consider on-topic
        audio_keywords = [
            'bose', 'speaker', 'audio', 'sound', 'amplifier', 'microphone',
            'loudspeaker', 'processor', 'dsp', 'channel', 'frequency', 'db',
            'watt', 'ohm', 'installation', 'setup', 'configure', 'connect',
            'designmax', 'controlspace', 'professional', 'system', 'equipment',
            'volume', 'bass', 'treble', 'equalizer', 'mixer', 'input', 'output',
            'signal', 'cable', 'wire', 'mount', 'ceiling', 'pendant', 'acoustic'
        ]
        
        # If any audio keyword found, it's on-topic
        if any(keyword in query_lower for keyword in audio_keywords):
            return False
        
        # Off-topic indicators - common unrelated topics
        off_topic_keywords = [
            'pizza', 'food', 'recipe', 'cook', 'restaurant', 'eat',
            'airplane', 'aeroplane', 'wings', 'fly', 'flight', 'aviation',
            'car', 'vehicle', 'drive', 'road', 'traffic',
            'weather', 'temperature', 'rain', 'snow',
            'movie', 'film', 'actor', 'cinema',
            'sport', 'game', 'football', 'basketball',
            'political', 'president', 'election', 'government',
            'medical', 'doctor', 'medicine', 'hospital',
            'programming', 'code', 'software', 'python', 'java'
        ]
        
        # If clear off-topic keyword found, reject
        if any(keyword in query_lower for keyword in off_topic_keywords):
            return True
        
        # Default: assume on-topic (let retrieval handle it)
        return False
    
    def get_system_info(self) -> Dict:
        """Get system information and health status"""
        
        doc_count = self.vector_store.collection.count()
        
        info = {
            'model': self.llm.get_model_info(),
            'documents_loaded': self.retriever is not None,
            'document_count': doc_count,
            'retriever_type': 'hybrid' if config.ENABLE_HYBRID_SEARCH else 'standard',
            'enhancements': {
                'hybrid_search': config.ENABLE_HYBRID_SEARCH,
                'query_cache': config.ENABLE_QUERY_CACHE,
                'confidence_scoring': config.ENABLE_CONFIDENCE_SCORING,
                'metrics': config.ENABLE_METRICS
            },
            'cache_stats': self.cache.get_stats() if config.ENABLE_QUERY_CACHE else None,
            'metrics_summary': self.metrics.get_summary() if config.ENABLE_METRICS else None,
            'errors': error_handler.get_error_summary()
        }
        
        logger.info(f"System info requested")
        return info
    
    def get_metrics(self) -> Dict:
        """Get detailed metrics (if enabled)"""
        if not config.ENABLE_METRICS:
            return {'enabled': False}
        
        return {
            'enabled': True,
            'summary': self.metrics.get_summary(),
            'recent_queries': self.metrics.get_recent_queries(limit=10),
            'time_series': self.metrics.get_time_series(interval_minutes=5)
        }
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics (if enabled)"""
        if not config.ENABLE_QUERY_CACHE:
            return {'enabled': False}
        
        stats = self.cache.get_stats()
        stats['recent_queries'] = self.cache.get_recent_queries(limit=10)
        return stats
    
    def clear_cache(self):
        """Clear query cache"""
        if config.ENABLE_QUERY_CACHE:
            self.cache.clear()
            logger.info("Cache cleared by user request")

"""
Complete RAG system using Phi-2
Main orchestrator class
"""
from typing import List, Optional, Dict
import time
from src.document_processing.router import ProcessingRouter
from src.vector_store.chromadb_manager import EnhancedChromaDB
from src.retrieval.content_aware_retriever import ContentAwareRetriever
from src.generation.prompt_builder import PromptBuilder
from src.generation.llm_handler_phi import Phi2Handler
from src.error_handling.logger import logger
from src.error_handling.handlers import error_handler
from config.constants import ErrorType


class BoseRAGPhi:
    """
    Complete RAG system using Phi-2
    Memory-efficient (1.6GB), fast (2-3s per query)
    """
    
    def __init__(self):
        """Initialize RAG system"""
        
        logger.info("=" * 70)
        logger.info("Initializing Bose RAG with Phi-2...")
        logger.info("=" * 70)
        
        try:
            # Initialize components
            self.vector_store = EnhancedChromaDB()
            logger.info("SUCCESS: Vector store initialized")
            
            self.prompt_builder = PromptBuilder()
            logger.info("SUCCESS: Prompt builder initialized")
            
            self.llm = Phi2Handler()
            logger.info("SUCCESS: Phi-2 LLM initialized")
            
            self.router = ProcessingRouter()
            
            # Check if database has documents and initialize retriever
            doc_count = self.vector_store.collection.count()
            if doc_count > 0:
                self.retriever = ContentAwareRetriever(self.vector_store)
                logger.info(f"SUCCESS: Loaded existing collection with {doc_count} documents")
            else:
                self.retriever = None
                logger.warning("WARNING: No documents in database. Process documents first.")
            
            logger.info("SUCCESS: RAG system fully initialized")
            logger.info("=" * 70)
        
        except Exception as e:
            logger.error(f"ERROR: Initialization failed: {str(e)}")
            error_handler.handle_error(
                ErrorType.PROCESSING_ERROR,
                e,
                context={"stage": "initialization"}
            )
            raise
    
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
            
            # Initialize retriever
            self.retriever = ContentAwareRetriever(self.vector_store)
            
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
        Answer user query with comprehensive error handling
        
        Args:
            query: User question
            verbose: Show intermediate steps
        
        Returns:
            Result dictionary with answer, sources, metadata
        """
        
        start_time = time.time()
        
        try:
            logger.debug(f"Query: {query}")
            
            # Check initialization
            if not self.retriever:
                logger.warning("WARNING: No documents processed yet")
                return {
                    'status': 'error',
                    'query': query,
                    'answer': 'Please process documents first using process_documents()',
                    'sources': [],
                    'time': f"{time.time() - start_time:.2f}s",
                    'error': 'No documents loaded'
                }
            
            if verbose:
                logger.info(f"Step 1: Retrieving documents...")
            
            # Retrieve documents
            docs = self.retriever.retrieve(query, k=5)
            
            if not docs:
                logger.warning(f"WARNING: No relevant documents found for query: {query}")
                return {
                    'status': 'no_context',
                    'query': query,
                    'answer': (
                        "No relevant information found in the documents. "
                        "Try rephrasing your question or ask about: "
                        "specifications, installation, configuration, or features."
                    ),
                    'sources': [],
                    'time': f"{time.time() - start_time:.2f}s"
                }
            
            if verbose:
                logger.info(f"SUCCESS: Retrieved {len(docs)} relevant documents")
                logger.info(f"Step 2: Building prompt...")
            
            # Build prompt
            prompt = self.prompt_builder.build_prompt(query, docs)
            
            if verbose:
                logger.info(f"Step 3: Generating answer with Phi-2...")
            
            # Generate answer
            answer = self.llm.generate(prompt)
            
            if verbose:
                logger.info(f"SUCCESS: Answer generated")
            
            # Format response
            elapsed_time = time.time() - start_time
            
            # Build sources with distance for confidence
            sources = []
            distances = []
            for doc in docs:
                dist = doc.metadata.get('distance')
                if isinstance(dist, (int, float)):
                    distances.append(float(dist))
                sources.append({
                    'page': doc.metadata.get('page'),
                    'content_type': doc.metadata.get('content_type'),
                    'source': doc.metadata.get('source'),
                    'distance': dist
                })

            # Simple confidence heuristic based on top distance
            confidence = 'unknown'
            if distances:
                d0 = distances[0]
                if d0 is not None:
                    # Lower distance => higher similarity in Chroma
                    confidence = 'high' if d0 <= 0.15 else 'medium' if d0 <= 0.35 else 'low'
            
            logger.info(f"SUCCESS: Query answered in {elapsed_time:.2f}s")
            
            return {
                'status': 'success',
                'query': query,
                'answer': answer,
                'sources': sources,
                'confidence': confidence,
                'model': 'phi-2',
                'time': f"{elapsed_time:.2f}s"
            }
        
        except Exception as e:
            logger.error(f"ERROR: Query processing failed: {str(e)}")
            
            error_handler.handle_error(
                ErrorType.RETRIEVAL_ERROR,
                e,
                context={'query': query}
            )
            
            return {
                'status': 'error',
                'query': query,
                'answer': f"Error processing query: {str(e)}",
                'sources': [],
                'time': f"{time.time() - start_time:.2f}s",
                'error': str(e)
            }
    
    def interactive_session(self):
        """Interactive Q&A session with error handling"""
        
        if not self.retriever:
            logger.error("ERROR: No documents loaded. Run process_documents() first.")
            print("ERROR: Please load documents first!")
            return
        
        print("\n" + "=" * 70)
        print("🎙️  BOSE TECHNICAL SPECS Q&A (Phi-2)")
        print("=" * 70)
        print(f"Model: Phi-2 | Privacy: 100% Local | Speed: Fast ⚡")
        print("Type 'quit', 'exit', or 'q' to exit\n")
        
        query_count = 0
        
        while True:
            try:
                query = input("❓ Your question: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if not query:
                    print("Please enter a question.\n")
                    continue
                
                query_count += 1
                logger.info(f"Query #{query_count}: {query}")
                
                # Get answer
                result = self.answer_query(query, verbose=False)
                
                # Display result
                print(f"\n{'✅' if result['status'] == 'success' else '⚠️'} Answer:")
                print(f"{result['answer']}\n")
                
                if result['sources']:
                    print(f"📚 Sources ({len(result['sources'])} documents):")
                    for i, src in enumerate(result['sources'], 1):
                        print(f"   {i}. Page {src['page']} ({src['content_type']}) - {src['source']}")
                
                print(f"⏱️  Time: {result['time']}")
                print("-" * 70 + "\n")
            
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            
            except Exception as e:
                logger.error(f"Unexpected error in interactive session: {str(e)}")
                print(f"❌ Error: {str(e)}")
                print("Continuing...\n")
    
    def get_system_info(self) -> Dict:
        """Get system information and health status"""
        
        doc_count = self.vector_store.collection.count()
        
        info = {
            'model': self.llm.get_model_info(),
            'documents_loaded': self.retriever is not None,
            'document_count': doc_count,
            'errors': error_handler.get_error_summary()
        }
        
        logger.info(f"System info: {info}")
        return info

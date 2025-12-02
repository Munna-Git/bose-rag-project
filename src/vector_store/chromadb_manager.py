"""
ChromaDB manager with metadata support
"""
from typing import List, Dict
import chromadb
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from config.settings import config
from src.error_handling.logger import logger


class EnhancedChromaDB:
    """Enhanced ChromaDB with metadata support"""
    
    def __init__(self):
        """Initialize ChromaDB"""
        
        try:
            logger.info("Initializing ChromaDB...")
            
            # Initialize embeddings with caching and optimization
            model_kwargs = {'device': 'cpu'}
            encode_kwargs = {'normalize_embeddings': True, 'batch_size': 32}
            
            self.embeddings = HuggingFaceEmbeddings(
                model_name=config.EMBEDDING_MODEL,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs,
                cache_folder=str(config.BASE_DIR / "models")
            )
            
            logger.info("Embedding model loaded and cached")
            
            # Initialize ChromaDB with persistence
            self.client = chromadb.PersistentClient(path=str(config.VECTOR_DB_DIR))
            self.collection = self.client.get_or_create_collection(
                name="bose_documents",
                metadata={"hnsw:space": "cosine"}
            )
            
            # Track document count
            self.doc_count = self.collection.count()
            logger.info(f"Existing documents in collection: {self.doc_count}")
            
            logger.info("SUCCESS: ChromaDB initialized")
        
        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Document]):
        """Add documents to vector store"""
        
        try:
            logger.info(f"Adding {len(documents)} documents...")
            
            # Prepare batch data
            ids = []
            embeddings = []
            docs_content = []
            metadatas = []
            
            for i, doc in enumerate(documents):
                # Generate unique ID using current count + index
                doc_id = f"doc_{self.doc_count + i}"
                ids.append(doc_id)
                
                # Generate embedding
                embedding = self.embeddings.embed_query(doc.page_content)
                embeddings.append(embedding)
                
                docs_content.append(doc.page_content)
                metadatas.append(doc.metadata)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(documents)} documents...")
            
            # Add all documents in batch
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=docs_content,
                metadatas=metadatas
            )
            
            # Update document count
            self.doc_count += len(documents)
            new_total = self.collection.count()
            logger.info(f"SUCCESS: {len(documents)} documents added. Total in DB: {new_total}")
        
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            raise
    
    def search(self, query: str, k: int = 5) -> Dict:
        """Search documents"""
        
        try:
            import time
            total_docs = self.collection.count()
            logger.info(f"Searching in {total_docs} documents for: '{query[:50]}...'")
            
            if total_docs == 0:
                logger.warning("Collection is empty! No documents to search.")
                return {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
            
            embedding_start = time.time()
            query_embedding = self.embeddings.embed_query(query)
            embedding_time = time.time() - embedding_start
            logger.info(f"Query embedding generated in {embedding_time:.2f}s")
            
            search_start = time.time()
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(k, total_docs)
            )
            search_time = time.time() - search_start
            logger.info(f"ChromaDB search completed in {search_time:.2f}s")
            
            # Log search results
            num_results = len(results['documents'][0]) if results.get('documents') else 0
            logger.info(f"Found {num_results} matching documents")
            
            if num_results > 0:
                logger.debug(f"Top result distance: {results['distances'][0][0]:.4f}")
            
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
            logger.info("SUCCESS: Loaded existing collection")
        
        except Exception as e:
            logger.warning(f"No existing collection: {str(e)}")

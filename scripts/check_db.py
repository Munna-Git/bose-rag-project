#!/usr/bin/env python3
"""
Utility script to check ChromaDB contents and debug retrieval
"""
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_store.chromadb_manager import EnhancedChromaDB
from src.error_handling.logger import logger
from config.settings import config


def main():
    """Check database contents"""
    
    print("=" * 70)
    print("ChromaDB Database Checker")
    print("=" * 70)
    
    try:
        # Initialize vector store
        print("\nInitializing ChromaDB...")
        vector_store = EnhancedChromaDB()
        
        # Get collection info
        collection = vector_store.collection
        count = collection.count()
        
        print(f"\nCollection: {collection.name}")
        print(f"Total documents: {count}")
        print(f"Database path: {config.VECTOR_DB_DIR}")
        
        if count == 0:
            print("\nWARNING: Database is empty!")
            print("Run demo.py to process documents first.")
            return
        
        # Get sample documents
        print("\n" + "-" * 70)
        print("Sample Documents (first 5):")
        print("-" * 70)
        
        results = collection.get(limit=5)
        
        for i, (doc_id, doc_text, metadata) in enumerate(
            zip(results['ids'], results['documents'], results['metadatas']), 1
        ):
            print(f"\n{i}. ID: {doc_id}")
            print(f"   Source: {metadata.get('source', 'Unknown')}")
            print(f"   Page: {metadata.get('page', 'Unknown')}")
            print(f"   Type: {metadata.get('content_type', 'Unknown')}")
            print(f"   Content: {doc_text[:150]}...")
        
        # Test search
        print("\n" + "-" * 70)
        print("Testing Search:")
        print("-" * 70)
        
        test_queries = [
            "What is the maximum number of analog inputs?",
            "EX-1280C specifications",
            "software version configuration"
        ]
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            
            results = vector_store.search(query, k=3)
            
            if results.get('documents') and len(results['documents'][0]) > 0:
                docs = results['documents'][0]
                distances = results['distances'][0]
                metas = results['metadatas'][0]
                
                print(f"  Found {len(docs)} results:")
                for j, (doc, dist, meta) in enumerate(zip(docs, distances, metas), 1):
                    print(f"    {j}. Distance: {dist:.4f} | Page: {meta.get('page')} | {doc[:80]}...")
            else:
                print("  No results found!")
        
        print("\n" + "=" * 70)
        print("Check complete!")
        print("=" * 70)
    
    except Exception as e:
        logger.error(f"Check failed: {str(e)}", exc_info=True)
        print(f"\nERROR: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

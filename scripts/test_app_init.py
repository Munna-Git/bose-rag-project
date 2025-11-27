#!/usr/bin/env python3
"""
Quick test to verify the Gradio app loads existing documents correctly
"""
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.interfaces.rag_phi import BoseRAGPhi
from src.error_handling.logger import logger


def main():
    """Test RAG initialization with existing database"""
    
    print("=" * 70)
    print("Testing RAG Initialization with Existing Database")
    print("=" * 70)
    print()
    
    try:
        # Initialize RAG (same as Gradio app does)
        print("Initializing RAG system...")
        rag = BoseRAGPhi()
        
        # Check status
        print("\nSystem Status:")
        print("-" * 70)
        
        info = rag.get_system_info()
        
        print(f"Model: {info['model'].get('name', 'Unknown')}")
        print(f"Documents in DB: {info['document_count']}")
        print(f"Retriever initialized: {info['documents_loaded']}")
        
        if not info['documents_loaded']:
            print("\nWARNING: Retriever not initialized!")
            print("This means the Gradio app won't be able to answer questions.")
            print("\nTroubleshooting:")
            print("1. Run: python scripts\\check_db.py")
            print("2. If empty, run: python scripts\\demo.py")
            return 1
        
        # Test a query
        print("\n" + "-" * 70)
        print("Testing Query...")
        print("-" * 70)
        
        test_query = "What is the maximum number of analog inputs?"
        print(f"\nQuery: {test_query}")
        
        result = rag.answer_query(test_query, verbose=True)
        
        print(f"\nStatus: {result['status']}")
        print(f"Answer: {result['answer'][:200]}...")
        print(f"Sources found: {len(result.get('sources', []))}")
        print(f"Time: {result['time']}")
        
        if result['status'] == 'success':
            print("\n" + "=" * 70)
            print("SUCCESS: RAG system working correctly!")
            print("=" * 70)
            return 0
        else:
            print("\n" + "=" * 70)
            print("WARNING: Query did not succeed")
            print("=" * 70)
            return 1
    
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        print(f"\nERROR: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

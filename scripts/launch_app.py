#!/usr/bin/env python3
"""
Launch Bose RAG Web Application
Simple launcher with startup checks
"""
import sys
import os
from pathlib import Path
import requests
import time

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_ollama():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def check_model():
    """Check if phi model is available"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        data = response.json()
        models = [m['name'] for m in data.get('models', [])]
        return any('phi' in m for m in models)
    except:
        return False


def check_database():
    """Check if database has documents"""
    from src.vector_store.chromadb_manager import EnhancedChromaDB
    try:
        vector_store = EnhancedChromaDB()
        count = vector_store.collection.count()
        return count > 0, count
    except:
        return False, 0


def main():
    """Launch application with checks"""
    
    print("=" * 70)
    print("Bose RAG Application Launcher")
    print("=" * 70)
    print()
    
    # Pre-flight checks
    print("Running pre-flight checks...")
    print()
    
    # Check 1: Ollama
    print("1. Checking Ollama service...", end=" ")
    if check_ollama():
        print("OK")
    else:
        print("FAILED")
        print("\n   ERROR: Ollama is not running!")
        print("   Start it with: ollama serve")
        return 1
    
    # Check 2: Model
    print("2. Checking Phi model...", end=" ")
    if check_model():
        print("OK")
    else:
        print("FAILED")
        print("\n   ERROR: Phi model not found!")
        print("   Pull it with: ollama pull phi")
        return 1
    
    # Check 3: Database
    print("3. Checking vector database...", end=" ")
    has_docs, count = check_database()
    if has_docs:
        print(f"OK ({count} documents)")
    else:
        print("WARNING")
        print(f"\n   WARNING: Database is empty ({count} documents)")
        print("   Run: python scripts\\demo.py to process documents")
        print("\n   Continue anyway? (y/n): ", end="")
        
        response = input().strip().lower()
        if response != 'y':
            print("   Cancelled.")
            return 0
    
    print()
    print("All checks passed!")
    print()
    print("=" * 70)
    print("Starting Gradio Web Interface...")
    print("=" * 70)
    print()
    
    # Import and launch
    try:
        from src.interfaces.gradio_app import RAGGradioApp
        
        app = RAGGradioApp()
        
        print("\nApplication starting...")
        print()
        print("Access the interface at:")
        print("  Local:   http://localhost:7860")
        print("  Network: http://0.0.0.0:7860")
        print()
        print("Press Ctrl+C to stop the server")
        print()
        
        app.launch(share=False)
        
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        return 0
    
    except Exception as e:
        print(f"\nERROR: Application failed to start!")
        print(f"Details: {str(e)}")
        print("\nCheck logs: rag_system.log")
        return 1


if __name__ == "__main__":
    sys.exit(main())

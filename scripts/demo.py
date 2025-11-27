#!/usr/bin/env python3
"""
Complete demo of Bose RAG with Phi-2
Shows all features and error handling
"""
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.interfaces.rag_phi import BoseRAGPhi
from src.error_handling.logger import logger
from config.settings import config


def main():
    """Run complete demo"""
    
    logger.info("Starting Bose RAG Demo with Phi-2")
    
    try:
        # Initialize RAG
        rag = BoseRAGPhi()
        
        # Prepare documents
        pdf_files = [
            config.DOCS_DIR / "AIML.pdf",
            config.DOCS_DIR / "tds_DesignMax_DM8SE_a4_EN.pdf",
            config.DOCS_DIR / "TDS_ControlSpace_EX-1280C_LTR_enUS.pdf"
        ]
        
        # Verify files exist
        existing_files = [f for f in pdf_files if f.exists()]
        
        if not existing_files:
            logger.error(f"❌ No PDF files found in {config.DOCS_DIR}")
            logger.info(f"📌 Place PDFs in: {config.DOCS_DIR}")
            return
        
        logger.info(f"Found {len(existing_files)} PDF files")
        
        # Process documents
        logger.info("\n📥 Processing documents...")
        result = rag.process_documents([str(f) for f in existing_files])
        logger.info(f"Processing result: {result}")
        
        if result['status'] in ['success', 'partial_failure']:
            # Test queries
            test_queries = [
                "What is the SNR of DesignMax DM8SE?",
                "How do I configure ControlSpace?",
                "What is the frequency response?"
            ]
            
            logger.info("\n❓ Testing queries...")
            
            for query in test_queries:
                print(f"\n{'=' * 70}")
                print(f"Q: {query}")
                
                result = rag.answer_query(query, verbose=True)
                
                print(f"\nA: {result['answer']}")
                
                if result['sources']:
                    print(f"\n📚 Sources:")
                    for src in result['sources']:
                        print(f"   - Page {src['page']} ({src['content_type']})")
                
                print(f"⏱️  {result['time']}")
            
            # Interactive session
            logger.info("\n🎙️ Starting interactive session...")
            rag.interactive_session()
        
        else:
            logger.error(f"❌ Processing failed: {result}")
    
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    
    except Exception as e:
        logger.error(f"❌ Demo failed: {str(e)}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

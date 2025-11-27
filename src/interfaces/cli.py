"""
Command-line interface for Bose RAG
"""
import sys
import argparse
from pathlib import Path
from src.interfaces.rag_phi import BoseRAGPhi
from src.error_handling.logger import logger
from config.settings import config


class CLIInterface:
    """Command-line interface"""
    
    def __init__(self):
        """Initialize CLI"""
        self.rag = None
    
    def init_rag(self):
        """Initialize RAG system"""
        try:
            logger.info("Initializing RAG system...")
            self.rag = BoseRAGPhi()
            logger.info("✅ RAG system ready")
        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG: {str(e)}")
            print(f"❌ Error: {str(e)}")
            sys.exit(1)
    
    def process_command(self, args):
        """Process command-line arguments"""
        
        try:
            if args.command == 'process':
                return self.cmd_process(args.files)
            
            elif args.command == 'query':
                return self.cmd_query(args.question)
            
            elif args.command == 'interactive':
                return self.cmd_interactive()
            
            elif args.command == 'info':
                return self.cmd_info()
            
            else:
                print("❌ Unknown command")
                return 1
        
        except Exception as e:
            logger.error(f"Command processing failed: {str(e)}")
            print(f"❌ Error: {str(e)}")
            return 1
    
    def cmd_process(self, files: List[str]) -> int:
        """Process documents"""
        
        try:
            if not files:
                print("❌ No files specified")
                return 1
            
            # Verify files exist
            file_paths = []
            for f in files:
                path = Path(f)
                if not path.exists():
                    print(f"❌ File not found: {f}")
                    continue
                file_paths.append(str(path))
            
            if not file_paths:
                print("❌ No valid files to process")
                return 1
            
            print(f"\n📥 Processing {len(file_paths)} file(s)...")
            result = self.rag.process_documents(file_paths)
            
            print(f"\n✅ Processing complete:")
            print(f"   Total chunks: {result['total_chunks']}")
            print(f"   Documents processed: {result['documents_processed']}")
            if result.get('documents_failed', 0) > 0:
                print(f"   Documents failed: {result['documents_failed']}")
            
            return 0
        
        except Exception as e:
            logger.error(f"Processing command failed: {str(e)}")
            print(f"❌ Error: {str(e)}")
            return 1
    
    def cmd_query(self, question: str) -> int:
        """Answer single query"""
        
        try:
            if not question:
                print("❌ No question provided")
                return 1
            
            print(f"\n❓ Question: {question}")
            print("-" * 70)
            
            result = self.rag.answer_query(question, verbose=False)
            
            if result['status'] == 'error':
                print(f"❌ Error: {result['answer']}")
                return 1
            
            print(f"✅ Answer:")
            print(f"{result['answer']}\n")
            
            if result['sources']:
                print("📚 Sources:")
                for i, src in enumerate(result['sources'], 1):
                    print(f"   {i}. Page {src['page']} ({src['content_type']}) - {src['source']}")
            
            print(f"⏱️  Time: {result['time']}")
            print("-" * 70)
            
            return 0
        
        except Exception as e:
            logger.error(f"Query command failed: {str(e)}")
            print(f"❌ Error: {str(e)}")
            return 1
    
    def cmd_interactive(self) -> int:
        """Start interactive session"""
        
        try:
            print("\n" + "=" * 70)
            print("🎙️ BOSE TECHNICAL SPECS Q&A (CLI)")
            print("=" * 70)
            print("Type 'quit', 'exit', or 'q' to exit")
            print("Type 'help' for commands\n")
            
            self.rag.interactive_session()
            return 0
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted")
            return 0
        
        except Exception as e:
            logger.error(f"Interactive session failed: {str(e)}")
            print(f"❌ Error: {str(e)}")
            return 1
    
    def cmd_info(self) -> int:
        """Show system information"""
        
        try:
            print("\n" + "=" * 70)
            print("📊 SYSTEM INFORMATION")
            print("=" * 70)
            
            info = self.rag.get_system_info()
            
            print("\n🤖 Model Information:")
            model_info = info['model']
            print(f"   Model: {model_info.get('name', 'Unknown')}")
            print(f"   Size: {model_info.get('size', 'Unknown')}")
            print(f"   Status: {model_info.get('status', 'Unknown')}")
            
            print("\n📚 Documents:")
            print(f"   Loaded: {'Yes' if info['documents_loaded'] else 'No'}")
            
            print("\n⚠️  Errors:")
            errors = info['errors']
            if errors['total_errors'] > 0:
                print(f"   Total: {errors['total_errors']}")
                for err in errors['errors'][-5:]:  # Show last 5 errors
                    print(f"   - {err['type']}: {err['message']}")
            else:
                print("   None")
            
            print("\n" + "=" * 70 + "\n")
            
            return 0
        
        except Exception as e:
            logger.error(f"Info command failed: {str(e)}")
            print(f"❌ Error: {str(e)}")
            return 1


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    
    parser = argparse.ArgumentParser(
        description="Bose Technical Specs RAG - CLI Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s process file1.pdf file2.pdf
  %(prog)s query "What is the SNR?"
  %(prog)s interactive
  %(prog)s info
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Process command
    process_parser = subparsers.add_parser(
        'process',
        help='Process PDF documents'
    )
    process_parser.add_argument(
        'files',
        nargs='+',
        help='PDF files to process'
    )
    
    # Query command
    query_parser = subparsers.add_parser(
        'query',
        help='Answer a single question'
    )
    query_parser.add_argument(
        'question',
        help='Question to answer'
    )
    
    # Interactive command
    subparsers.add_parser(
        'interactive',
        help='Start interactive Q&A session'
    )
    
    # Info command
    subparsers.add_parser(
        'info',
        help='Show system information'
    )
    
    return parser


def main():
    """Main entry point"""
    
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize CLI
    cli = CLIInterface()
    cli.init_rag()
    
    # Process command
    return cli.process_command(args)


if __name__ == '__main__':
    sys.exit(main())

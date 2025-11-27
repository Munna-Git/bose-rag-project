"""
Gradio web interface for Bose RAG
Complete version with error handling
"""
import gradio as gr
from typing import Tuple
from src.interfaces.rag_phi import BoseRAGPhi
from src.generation.response_formatter import ResponseFormatter
from src.error_handling.logger import logger
from config.settings import config


class RAGGradioApp:
    """Gradio interface for RAG system with complete error handling"""
    
    def __init__(self):
        """Initialize Gradio app"""
        
        try:
            logger.info("Initializing Gradio app...")
            self.rag = BoseRAGPhi()
            self.formatter = ResponseFormatter()
            self.interface = None
            logger.info("SUCCESS: Gradio app initialized")
        
        except Exception as e:
            logger.error(f"Gradio app initialization failed: {str(e)}")
            raise
    
    def process_files(self, files) -> str:
        """
        Process uploaded files
        
        Args:
            files: Uploaded files
        
        Returns:
            Status message
        """
        
        try:
            if not files:
                return "ERROR: No files uploaded"
            
            # Extract file paths
            file_paths = []
            for f in files:
                try:
                    file_paths.append(f.name)
                except Exception as e:
                    logger.warning(f"Failed to process file: {str(e)}")
            
            if not file_paths:
                return "ERROR: No valid files to process"
            
            logger.info(f"Processing {len(file_paths)} files via Gradio")
            
            # Process documents
            result = self.rag.process_documents(file_paths)
            
            # Format response
            if result['status'] == 'success':
                return (
                    f"✅ **Processing Complete!**\n\n"
                    f"• Chunks extracted: {result['total_chunks']}\n"
                    f"• Documents processed: {result['documents_processed']}\n"
                    f"• Status: Ready for queries"
                )
            
            elif result['status'] == 'partial_failure':
                return (
                    f"⚠️ **Partial Success**\n\n"
                    f"• Chunks extracted: {result['total_chunks']}\n"
                    f"• Documents processed: {result['documents_processed']}\n"
                    f"• Documents failed: {result['documents_failed']}\n"
                    f"• Error: {result.get('storage_error', 'Unknown')}"
                )
            
            else:
                return (
                    f"❌ **Processing Failed**\n\n"
                    f"Error: {result.get('error', 'Unknown error')}"
                )
        
        except Exception as e:
            logger.error(f"File processing failed: {str(e)}")
            return f"❌ Error processing files: {str(e)}"
    
    def answer_question(self, question: str) -> Tuple[str, str]:
        """
        Answer question
        
        Args:
            question: User question
        
        Returns:
            Tuple of (answer, sources_text)
        """
        
        try:
            if not question or not question.strip():
                return "ERROR: Please enter a question", ""
            
            logger.info(f"Processing question via Gradio: {question}")
            
            # Get answer
            result = self.rag.answer_query(question, verbose=False)
            
            # Check status
            if result['status'] == 'error':
                return f"ERROR: {result['answer']}", ""
            
            # Format answer
            answer_text = result['answer']
            
            # Format sources
            sources_text = self._format_sources_for_display(result.get('sources', []))
            
            logger.info(f"Question answered in {result['time']}")
            
            return answer_text, sources_text
        
        except Exception as e:
            logger.error(f"Question answering failed: {str(e)}")
            return f"ERROR: {str(e)}", ""
    
    def _format_sources_for_display(self, sources: list) -> str:
        """Format sources for Gradio display"""
        
        try:
            if not sources:
                return "No sources found"
            
            markdown_text = "### 📚 Sources\n\n"
            
            for i, src in enumerate(sources, 1):
                markdown_text += (
                    f"{i}. **Page {src['page']}** "
                    f"({src['content_type']}) - {src['source']}\n"
                )
            
            return markdown_text
        
        except Exception as e:
            logger.error(f"Source formatting failed: {str(e)}")
            return "Error formatting sources"
    
    def get_status(self) -> str:
        """Get system status"""
        
        try:
            info = self.rag.get_system_info()
            
            status = "## System Status\n\n"
            status += f"**Model:** {info['model'].get('name', 'Unknown')}\n\n"
            status += f"**Documents in Database:** {info.get('document_count', 0)}\n\n"
            status += f"**Ready for Queries:** {'Yes' if info['documents_loaded'] else 'No - Process documents first'}\n\n"
            
            errors = info['errors']
            if errors['total_errors'] > 0:
                status += f"**Errors:** {errors['total_errors']}\n"
            else:
                status += "**No errors**\n"
            
            return status
        
        except Exception as e:
            logger.error(f"Status check failed: {str(e)}")
            return f"Error getting status: {str(e)}"
    
    def launch(self, share: bool = False):
        """
        Launch Gradio interface
        
        Args:
            share: Whether to create public share link
        """
        
        try:
            logger.info("Launching Gradio interface...")
            
            with gr.Blocks(
                title="Bose RAG - Phi-2",
                theme=gr.themes.Soft()
            ) as demo:
                
                # Header with status
                doc_count = self.rag.vector_store.collection.count()
                status_emoji = "✓" if doc_count > 0 else "⚠"
                status_text = f"{doc_count} documents loaded" if doc_count > 0 else "No documents - Upload PDFs below"
                
                gr.Markdown(f"""
                # Bose Technical Specs Q&A
                
                **Powered by Phi-2 | 100% Local | Privacy First**
                
                **Status:** {status_emoji} {status_text}
                
                Ask questions about Bose technical documentation.
                """)
                
                # Tabs
                with gr.Tabs():
                    
                    # Ask Questions Tab
                    with gr.Tab("❓ Ask Questions"):
                        with gr.Column():
                            question_input = gr.Textbox(
                                label="Your Question",
                                placeholder="e.g., What is the SNR of DesignMax DM8SE?",
                                lines=3
                            )
                            
                            ask_btn = gr.Button(
                                "🔍 Get Answer",
                                variant="primary"
                            )
                        
                        with gr.Column():
                            answer_output = gr.Textbox(
                                label="Answer",
                                lines=10,
                                interactive=False
                            )
                            
                            sources_output = gr.Markdown(
                                label="Sources",
                                value="Sources will appear here"
                            )
                        
                        # Connect button
                        ask_btn.click(
                            self.answer_question,
                            inputs=question_input,
                            outputs=[answer_output, sources_output]
                        )
                    
                    # Upload Documents Tab
                    with gr.Tab("📄 Upload Documents"):
                        with gr.Column():
                            gr.Markdown("### Upload PDF Documents")
                            
                            file_input = gr.File(
                                label="Select PDF Files",
                                file_count="multiple",
                                file_types=["pdf"]
                            )
                            
                            process_btn = gr.Button(
                                "⚙️ Process Documents",
                                variant="primary"
                            )
                        
                        with gr.Column():
                            status_output = gr.Markdown(
                                value="Upload documents and click 'Process' to begin"
                            )
                        
                        # Connect button
                        process_btn.click(
                            self.process_files,
                            inputs=file_input,
                            outputs=status_output
                        )
                    
                    # System Status Tab
                    with gr.Tab("📊 System Status"):
                        status_btn = gr.Button("🔄 Refresh Status")
                        status_display = gr.Markdown(
                            value=self.get_status()
                        )
                        
                        status_btn.click(
                            self.get_status,
                            outputs=status_display
                        )
                
                # Footer
                gr.Markdown("""
                ---
                
                **Tips:**
                - Ask specific questions for better answers
                - Use keywords like "specification", "how to", "installation"
                - All processing happens locally - your data is private
                
                For issues, check the logs in `rag_system.log`
                """)
            
            # Launch interface
            logger.info("Launching interface...")
            demo.launch(
                share=share,
                server_name="0.0.0.0",
                server_port=7860
            )
        
        except Exception as e:
            logger.error(f"Gradio launch failed: {str(e)}")
            print(f"ERROR: Error launching interface: {str(e)}")
            raise


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Bose RAG Web Interface")
    parser.add_argument(
        '--share',
        action='store_true',
        help='Create public share link'
    )
    
    args = parser.parse_args()
    
    try:
        app = RAGGradioApp()
        app.launch(share=args.share)
    
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        print(f"ERROR: Application failed: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

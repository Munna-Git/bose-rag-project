"""
Gradio web interface for Bose RAG
"""
import gradio as gr
from src.interfaces.rag_phi import BoseRAGPhi
from src.error_handling.logger import logger
from config.settings import config


class RAGGradioApp:
    """Gradio interface for RAG system"""
    
    def __init__(self):
        self.rag = BoseRAGPhi()
        self.interface = None
    
    def process_files(self, files):
        """Process uploaded files"""
        if not files:
            return "❌ No files uploaded"
        
        file_paths = [f.name for f in files]
        logger.info(f"Processing {len(file_paths)} files")
        
        result = self.rag.process_documents(file_paths)
        
        if result['status'] == 'success':
            return f"✅ Processed {result['total_chunks']} chunks from {result['documents_processed']} documents"
        else:
            return f"⚠️ {result['status']}: {result.get('error', 'Unknown error')}"
    
    def answer_question(self, question):
        """Answer question"""
        if not question:
            return "❌ Please enter a question", ""
        
        result = self.rag.answer_query(question, verbose=False)
        
        sources_text = ""
        if result['sources']:
            sources_text = "**Sources:**\n"
            for src in result['sources']:
                sources_text += f"- Page {src['page']} ({src['content_type']})\n"
        
        return result['answer'], sources_text
    
    def launch(self):
        """Launch Gradio interface"""
        
        with gr.Blocks(title="Bose RAG - Phi-2") as demo:
            gr.Markdown("# 🎙️ Bose Technical Specs Q&A")
            gr.Markdown("*Powered by Phi-2 | 100% Local | Privacy First*")
            
            with gr.Tab("Ask Questions"):
                question_input = gr.Textbox(label="Your Question", lines=3)
                ask_btn = gr.Button("Get Answer", variant="primary")
                answer_output = gr.Textbox(label="Answer", lines=10)
                sources_output = gr.Markdown(label="Sources")
                
                ask_btn.click(
                    self.answer_question,
                    inputs=question_input,
                    outputs=[answer_output, sources_output]
                )
            
            with gr.Tab("Upload Documents"):
                file_input = gr.File(label="Upload PDFs", file_count="multiple")
                process_btn = gr.Button("Process Documents", variant="primary")
                status_output = gr.Textbox(label="Status")
                
                process_btn.click(
                    self.process_files,
                    inputs=file_input,
                    outputs=status_output
                )
        
        demo.launch()


if __name__ == "__main__":
    app = RAGGradioApp()
    app.launch()

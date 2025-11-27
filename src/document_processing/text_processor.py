"""
Text processor - standard chunking
"""
from typing import List
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from .base_processor import BaseProcessor
from src.error_handling.logger import logger


class TextProcessor(BaseProcessor):
    """Process text content"""
    
    def process(self, pdf_path: str) -> List[Document]:
        """Process entire PDF as text"""
        
        try:
            logger.info(f"Processing text: {pdf_path}")
            
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            chunks = splitter.split_documents(documents)
            
            # Add metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata['content_type'] = 'TEXT'
                chunk.metadata['chunk_id'] = i
                chunk.metadata['processor'] = 'TextProcessor'
            
            logger.info(f"Extracted {len(chunks)} text chunks")
            return chunks
        
        except Exception as e:
            logger.error(f"Text processing failed: {str(e)}")
            raise

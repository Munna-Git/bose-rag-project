"""
Route documents to appropriate processors
"""
from typing import List
from langchain.schema import Document
from src.content_detection.detector import ContentDetector
from .text_processor import TextProcessor
from .table_processor import TableProcessor
from .image_processor import ImageProcessor
from src.error_handling.logger import logger
from config.constants import ContentType


class ProcessingRouter:
    """Route PDF to appropriate processor"""
    
    def __init__(self):
        self.detector = ContentDetector()
        self.text_processor = TextProcessor()
        self.table_processor = TableProcessor()
        self.image_processor = ImageProcessor()
    
    def process_pdf(self, pdf_path: str) -> List[Document]:
        """Process PDF based on content type"""
        
        try:
            # Detect content type
            detection = self.detector.detect_pdf_content(pdf_path)
            content_type = detection['overall_type']
            
            logger.info(f"Routing {pdf_path} as {content_type.value}")
            
            # Route to processor
            if content_type == ContentType.TABLE:
                return self.table_processor.process(pdf_path)
            elif content_type == ContentType.IMAGE:
                return self.image_processor.process(pdf_path)
            elif content_type == ContentType.MIXED:
                # Process with all processors
                text_chunks = self.text_processor.process(pdf_path)
                table_chunks = self.table_processor.process(pdf_path)
                image_chunks = self.image_processor.process(pdf_path)
                return text_chunks + table_chunks + image_chunks
            else:
                return self.text_processor.process(pdf_path)
        
        except Exception as e:
            logger.error(f"Routing failed for {pdf_path}: {str(e)}")
            # Fallback to text processing
            return self.text_processor.process(pdf_path)

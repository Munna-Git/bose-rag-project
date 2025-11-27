"""
Detect content types in PDFs
"""
import PyPDF2
from typing import Dict, List
from enum import Enum
from config.constants import ContentType, ProcessingStrategy
from src.error_handling.logger import logger


class ContentDetector:
    """Detect and analyze PDF content types"""
    
    def detect_pdf_content(self, pdf_path: str) -> Dict:
        """Detect content types in PDF"""
        
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                total_pages = len(reader.pages)
            
            text_pages = 0
            table_pages = 0
            image_pages = 0
            
            for i, page in enumerate(reader.pages[:5]):  # Sample first 5 pages
                text = page.extract_text()
                
                if not text:
                    image_pages += 1
                elif '|' in text or '\t' in text:
                    table_pages += 1
                else:
                    text_pages += 1
            
            # Determine overall type
            if table_pages > text_pages and table_pages > image_pages:
                overall_type = ContentType.TABLE
                strategy = ProcessingStrategy.TABLE_EXTRACTION
            elif image_pages > 0:
                overall_type = ContentType.MIXED
                strategy = ProcessingStrategy.MULTI_PROCESSOR
            else:
                overall_type = ContentType.TEXT
                strategy = ProcessingStrategy.STANDARD_CHUNKING
            
            logger.info(f"Detected {pdf_path}: {overall_type.value}")
            
            return {
                'overall_type': overall_type,
                'text_pages': text_pages,
                'table_pages': table_pages,
                'image_pages': image_pages,
                'total_pages': total_pages,
                'processing_strategy': strategy.value
            }
        
        except Exception as e:
            logger.error(f"Detection failed: {str(e)}")
            return {
                'overall_type': ContentType.TEXT,
                'processing_strategy': ProcessingStrategy.FALLBACK_TO_TEXT.value,
                'error': str(e)
            }

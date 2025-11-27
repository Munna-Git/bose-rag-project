"""
Image processor - OCR
"""
from typing import List
import pytesseract
from pdf2image import convert_from_path
from langchain.schema import Document
from .base_processor import BaseProcessor
from src.error_handling.logger import logger


class ImageProcessor(BaseProcessor):
    """Process image content with OCR"""
    
    def process(self, pdf_path: str) -> List[Document]:
        """Extract text from images in PDF"""
        
        try:
            logger.info(f"Processing images (OCR): {pdf_path}")
            
            images = convert_from_path(pdf_path)
            chunks = []
            
            for page_idx, image in enumerate(images):
                try:
                    text = pytesseract.image_to_string(image)
                    
                    if text.strip():
                        doc = Document(
                            page_content=text,
                            metadata={
                                'source': pdf_path,
                                'page': page_idx + 1,
                                'content_type': 'IMAGE',
                                'chunk_id': page_idx,
                                'processor': 'ImageProcessor'
                            }
                        )
                        chunks.append(doc)
                
                except Exception as e:
                    logger.warning(f"OCR failed on page {page_idx + 1}: {str(e)}")
            
            logger.info(f"Extracted {len(chunks)} image chunks")
            return chunks
        
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            return []

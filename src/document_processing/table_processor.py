"""
Table processor - structured extraction
"""
from typing import List
import camelot
from langchain.schema import Document
from .base_processor import BaseProcessor
from src.error_handling.logger import logger


class TableProcessor(BaseProcessor):
    """Process table content"""
    
    def process(self, pdf_path: str) -> List[Document]:
        """Extract tables from PDF"""
        
        try:
            logger.info(f"Extracting tables: {pdf_path}")
            
            tables = camelot.read_pdf(pdf_path, pages='all')
            chunks = []
            
            for table_idx, table in enumerate(tables):
                content = table.df.to_string()
                
                doc = Document(
                    page_content=content,
                    metadata={
                        'source': pdf_path,
                        'page': table_idx + 1,
                        'content_type': 'TABLE',
                        'chunk_id': table_idx,
                        'processor': 'TableProcessor'
                    }
                )
                chunks.append(doc)
            
            logger.info(f"Extracted {len(chunks)} tables")
            return chunks
        
        except Exception as e:
            logger.error(f"Table processing failed: {str(e)}")
            return []

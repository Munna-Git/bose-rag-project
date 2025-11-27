"""
Base processor class
"""
from abc import ABC, abstractmethod
from typing import List
from langchain.schema import Document
from config.settings import config


class BaseProcessor(ABC):
    """Base class for all processors"""
    
    def __init__(self):
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
    
    @abstractmethod
    def process(self, pdf_path: str) -> List[Document]:
        """Process PDF document"""
        pass

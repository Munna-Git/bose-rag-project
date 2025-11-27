"""
Constants for the RAG system
"""
from enum import Enum

class ContentType(Enum):
    """Content types"""
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    MIXED = "mixed"
    UNSUPPORTED = "unsupported"

class ErrorType(Enum):
    """Error types"""
    PDF_CORRUPTION = "pdf_corruption"
    TABLE_EXTRACTION_FAILED = "table_extraction_failed"
    OCR_FAILURE = "ocr_failure"
    EMBEDDING_ERROR = "embedding_error"
    LLM_ERROR = "llm_error"
    RETRIEVAL_ERROR = "retrieval_error"
    PROCESSING_ERROR = "processing_error"

class ProcessingStrategy(Enum):
    """Processing strategies"""
    STANDARD_CHUNKING = "standard_chunking"
    TABLE_EXTRACTION = "table_extraction"
    OCR_THEN_CHUNKING = "ocr_then_chunking"
    MULTI_PROCESSOR = "multi_processor_routing"
    FALLBACK_TO_TEXT = "fallback_to_raw_text"

# Error messages
ERROR_MESSAGES = {
    ErrorType.PDF_CORRUPTION: "PDF appears to be corrupted. Attempting recovery...",
    ErrorType.TABLE_EXTRACTION_FAILED: "Table extraction failed. Using text extraction fallback.",
    ErrorType.OCR_FAILURE: "Image OCR failed. Skipping image content.",
    ErrorType.EMBEDDING_ERROR: "Failed to generate embeddings. Retrying...",
    ErrorType.LLM_ERROR: "LLM error occurred. Using cached response if available.",
    ErrorType.RETRIEVAL_ERROR: "Retrieval failed. Using default search.",
    ErrorType.PROCESSING_ERROR: "Processing error. Attempting recovery...",
}

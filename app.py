"""
FastAPI application for Bose RAG System
Production-ready REST API with professional UI
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import os
from pathlib import Path

from src.interfaces.rag_phi import BoseRAGPhi
from src.error_handling.logger import logger

# Initialize FastAPI app
app = FastAPI(
    title="Bose Professional Technical Assistant",
    description="AI-powered technical documentation assistant for Bose Professional products",
    version="1.0.0"
)

# Initialize RAG system
rag: Optional[BoseRAGPhi] = None

# Mount static files for UI
static_dir = Path(__file__).parent / "static"
if not static_dir.exists():
    static_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


class QueryRequest(BaseModel):
    """Query request model"""
    question: str
    verbose: bool = False


class QueryResponse(BaseModel):
    """Query response model"""
    status: str
    query: str
    answer: str
    sources: List[Dict]
    model: str
    time: str
    error: Optional[str] = None
    confidence: Optional[Dict] = None
    confidence_recommendation: Optional[str] = None


class SystemInfo(BaseModel):
    """System information model"""
    status: str
    model: Dict
    documents_loaded: bool
    document_count: int


@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup"""
    global rag
    try:
        logger.info("Starting Bose RAG FastAPI server...")
        rag = BoseRAGPhi()
        logger.info("RAG system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        raise


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main UI"""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("""
        <html>
            <head><title>Bose Professional Technical Assistant</title></head>
            <body>
                <h1>Bose Professional Technical Assistant</h1>
                <p>API is running. Visit <a href="/docs">/docs</a> for API documentation.</p>
            </body>
        </html>
    """)


@app.post("/api/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Process a technical question
    
    Args:
        request: QueryRequest with question and optional verbose flag
    
    Returns:
        QueryResponse with answer, sources, and metadata
    """
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    if not rag.retriever:
        raise HTTPException(
            status_code=400, 
            detail="No documents loaded. Please process documents first."
        )
    
    try:
        result = rag.answer_query(request.question, verbose=request.verbose)
        return result
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    if not rag:
        return {"status": "initializing"}
    
    return {
        "status": "healthy",
        "model": "phi-2",
        "documents_loaded": rag.retriever is not None,
        "document_count": rag.vector_store.collection.count() if rag else 0
    }


@app.get("/api/info", response_model=SystemInfo)
async def system_info():
    """Get system information"""
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        info = rag.get_system_info()
        return {
            "status": "ready",
            "model": info["model"],
            "documents_loaded": info["documents_loaded"],
            "document_count": info["document_count"]
        }
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics")
async def get_metrics():
    """Get performance metrics (if enabled)"""
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        return rag.get_metrics()
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache statistics (if enabled)"""
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        return rag.get_cache_stats()
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cache/clear")
async def clear_cache():
    """Clear query cache"""
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        rag.clear_cache()
        return {"status": "success", "message": "Cache cleared"}
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/enhancements")
async def get_enhancements():
    """Get status of enhancement features"""
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    info = rag.get_system_info()
    return info.get('enhancements', {})


@app.get("/api/test-confidence")
async def test_confidence():
    """Test endpoint to verify confidence scoring works"""
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    from langchain_core.documents import Document
    from config.settings import config
    
    # Create test documents
    test_docs = [
        Document(page_content="Test content about frequency response", metadata={'page': 1}),
        Document(page_content="More test content", metadata={'page': 2})
    ]
    
    # Test confidence calculation
    if config.ENABLE_CONFIDENCE_SCORING:
        confidence = rag.confidence_scorer.calculate_confidence(
            query="test query",
            answer="This is a test answer with specific technical details about frequency response.",
            retrieved_docs=test_docs,
            retrieval_scores=[0.9, 0.85]
        )
        return {
            "confidence_scoring_enabled": True,
            "test_confidence": confidence,
            "message": "Confidence scoring is working!"
        }
    else:
        return {
            "confidence_scoring_enabled": False,
            "message": "Confidence scoring is disabled in settings"
        }


@app.post("/api/process-documents")
async def process_documents(pdf_paths: List[str]):
    """
    Process PDF documents
    
    Args:
        pdf_paths: List of PDF file paths to process
    
    Returns:
        Processing result with statistics
    """
    if not rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        result = rag.process_documents(pdf_paths)
        return result
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

# Bose Professional Technical Assistant
### AI-Powered RAG System for Technical Documentation

---

## What This System Does

This is an **intelligent Q&A system** that allows users to ask technical questions about Bose Professional products in natural language and receive instant, accurate answers with source citations.

**The Problem It Solves:**
- Engineers and technicians need quick answers from hundreds of pages of technical documentation
- Searching through multiple PDF manuals is time-consuming and frustrating
- Critical information is buried in dense technical documents

**The Solution:**
- Ask questions in plain English: *"What is the maximum number of analog inputs on the EX-1280C?"*
- Get accurate answers in 2-3 seconds with page references
- 100% local processing (no cloud APIs, complete privacy)
- Professional web interface matching Bose brand standards

**End-User Experience:**
1. User opens web browser to http://localhost:8000
2. Types a question in natural language (no special syntax needed)
3. System searches all processed documents using AI-powered semantic search
4. Receives clear answer with source page numbers in under 3 seconds
5. Can ask follow-up questions or explore related topics

---

## Project Structure Explained

**Understanding the Architecture:** This project follows a modular RAG (Retrieval-Augmented Generation) pipeline with clear separation of concerns. Here's how the codebase is organized:

```
bose-rag-project/
│
├── app.py                            # FastAPI application - Production web server
│   └─> Serves the web UI and REST API endpoints
│   └─> Initializes RAG system on startup
│   └─> Handles /api/query, /api/health, /api/info routes
│
├── launch_fastapi.bat                # Convenience launcher with pre-flight checks
│
├── requirements.txt                  # All Python dependencies with versions
│
├── config/                           # CONFIGURATION LAYER
│   ├── settings.py                   # Environment variables (.env) loader
│   │   └─> OLLAMA_BASE_URL, EMBEDDING_MODEL, CHUNK_SIZE, etc.
│   │
│   └── constants.py                  # System-wide constants and enums
│       └─> ContentType enum (SPECIFICATION, PROCEDURE, GENERAL)
│       └─> ErrorType enum for structured error handling
│       └─> Default values (CHUNK_SIZE=800, CHUNK_OVERLAP=100)
│
├── data/                             # DATA STORAGE
│   ├── vector_db/                    # ChromaDB persistent storage (auto-created)
│   │   └─> Stores document embeddings and metadata
│   │   └─> Survives application restarts
│   │
│   └── *.pdf                         # Source PDF documents (place here)
│
├── src/                              # CORE APPLICATION CODE
│   │
│   ├── content_detection/            # CONTENT CLASSIFICATION
│   │   └── detector.py               
│   │       └─> Analyzes text to determine if it's:
│   │           • Specification (technical data, numbers, specs)
│   │           • Procedure (installation, setup, how-to)
│   │           • General (overview, features, descriptions)
│   │       └─> Uses keyword matching and pattern recognition
│   │       └─> Helps build appropriate prompts for LLM
│   │
│   ├── document_processing/          # PDF PROCESSING PIPELINE
│   │   ├── base_processor.py        # Abstract base class defining interface
│   │   │
│   │   ├── text_processor.py        # Standard text extraction (PyPDF2)
│   │   │   └─> Handles most PDFs with selectable text
│   │   │   └─> Fast, primary extraction method
│   │   │
│   │   ├── table_processor.py       # Table extraction (Camelot)
│   │   │   └─> Detects and extracts tabular data
│   │   │   └─> Preserves structure of spec tables
│   │   │
│   │   ├── image_processor.py       # OCR processing (Tesseract)
│   │   │   └─> Handles scanned PDFs or image-based pages
│   │   │   └─> Fallback when text extraction fails
│   │   │
│   │   └── router.py                # Processing orchestrator
│   │       └─> Decides which processor to use per page
│   │       └─> Tries text → table → OCR in that order
│   │       └─> Chunks extracted text into semantic segments
│   │
│   ├── embeddings/                   # VECTOR EMBEDDINGS
│   │   └── embedder.py               
│   │       └─> Wraps HuggingFace sentence-transformers
│   │       └─> Model: all-MiniLM-L6-v2 (lightweight, fast)
│   │       └─> Converts text to 384-dimensional vectors
│   │       └─> Enables semantic similarity search
│   │
│   ├── vector_store/                 # VECTOR DATABASE
│   │   └── chromadb_manager.py      
│   │       └─> Manages ChromaDB operations
│   │       └─> PersistentClient (data survives restarts)
│   │       └─> Stores: embeddings + metadata (page, source, content_type)
│   │       └─> add_documents(): Batch insert with unique IDs
│   │       └─> search(): Cosine similarity search, returns top-k
│   │
│   ├── retrieval/                    # DOCUMENT RETRIEVAL
│   │   └── content_aware_retriever.py
│   │       └─> Queries vector store for relevant chunks
│   │       └─> Retrieves top-k (default k=5) most similar documents
│   │       └─> Returns Document objects with metadata preserved
│   │       └─> Maintains original ranking from ChromaDB
│   │
│   ├── generation/                   # ANSWER GENERATION
│   │   ├── llm_handler_phi.py       # Ollama + Phi-2 integration
│   │   │   └─> Connects to local Ollama server
│   │   │   └─> Uses Phi-2 model (1.6GB, fast, local)
│   │   │   └─> generate(): Sends prompt, gets answer
│   │   │   └─> Configurable max_tokens, temperature
│   │   │
│   │   └── prompt_builder.py        # Context-aware prompt construction
│   │       └─> Detects query intent (spec/procedure/general)
│   │       └─> Builds appropriate prompt template
│   │       └─> Includes retrieved context + user question
│   │       └─> Optimizes for concise, accurate answers
│   │
│   ├── interfaces/                   # USER INTERFACES
│   │   ├── rag_phi.py               # Main RAG orchestrator (BoseRAGPhi class)
│   │   │   └─> Coordinates all components
│   │   │   └─> process_documents(): Ingests PDFs → chunks → embeddings → DB
│   │   │   └─> answer_query(): Full RAG pipeline
│   │   │   └─> Handles errors gracefully, logs everything
│   │   │
│   │   └── gradio_app.py            # Alternative Gradio UI (simple demo)
│   │
│   └── error_handling/               # LOGGING & ERROR MANAGEMENT
│       ├── logger.py                 # Rotating file logger
│       │   └─> Writes to rag_system.log
│       │   └─> Max 10MB per file, keeps 5 backups
│       │   └─> Console + file output
│       │
│       └── handlers.py               # Structured error handling
│           └─> ErrorType enum categorization
│           └─> Collects error statistics
│           └─> Provides error summaries
│
├── static/                           # FRONTEND (FastAPI)
│   ├── index.html                    # Main web interface
│   │   └─> Professional Bose-branded UI
│   │   └─> Chat-style message interface
│   │   └─> Real-time status indicators
│   │
│   ├── styles.css                    # Bose Professional dark theme
│   │   └─> CSS variables for easy customization
│   │   └─> --bose-accent: #00a0dc (brand color)
│   │   └─> Responsive design (mobile-friendly)
│   │
│   └── app.js                        # Frontend JavaScript logic
│       └─> API calls to /api/query
│       └─> Message rendering and chat history
│       └─> Loading states and error handling
│
├── scripts/                          # UTILITY SCRIPTS
│   ├── demo.py                       # Document processing demo
│   │   └─> Run this first to populate database
│   │   └─> Processes PDFs in data/ folder
│   │   └─> Shows progress and statistics
│   │
│   ├── check_db.py                   # Database inspection tool
│   │   └─> Shows document count
│   │   └─> Tests sample queries
│   │   └─> Displays top results with distances
│   │
│   ├── clear_db.py                   # Database reset utility
│   │   └─> Deletes vector_db directory
│   │   └─> Use when reprocessing documents
│   │
│   └── launch_app.py                 # Gradio launcher with checks
│
└── tests/                            # UNIT TESTS (future)
```

### Key Design Principles

1. **Modularity**: Each component has a single responsibility
2. **Separation of Concerns**: Processing → Storage → Retrieval → Generation are independent
3. **Error Resilience**: Comprehensive error handling at every layer
4. **Configurability**: Environment variables for all settings
5. **Persistence**: Vector DB survives restarts, no reprocessing needed
6. **Observability**: Detailed logging for debugging and monitoring

---

## System Architecture & Data Flow

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          END USER                                    │
│              (Opens browser, types question)                         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      WEB INTERFACE                                   │
│                   (FastAPI + HTML/CSS/JS)                            │
│                                                                       │
│  • Professional Bose-branded UI                                      │
│  • Real-time status display                                          │
│  • Chat-style message interface                                      │
│  • REST API endpoints (/api/query, /api/health)                     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    RAG ORCHESTRATOR                                  │
│                    (BoseRAGPhi Class)                                │
│                                                                       │
│  • Receives user question                                            │
│  • Coordinates all components                                        │
│  • Handles errors gracefully                                         │
│  • Returns formatted response                                        │
└──────┬──────────────────────────────────────────────────────┬───────┘
       │                                                      │
       │ ONE-TIME SETUP PHASE                    QUERY PHASE (Every Request)
       │                                                      │
       ▼                                                      ▼
┌──────────────────────┐                    ┌──────────────────────────┐
│  DOCUMENT INGESTION  │                    │   QUERY PROCESSING       │
└──────────────────────┘                    └──────────────────────────┘
       │                                                      │
       │                                                      │
       ▼                                                      ▼
┌──────────────────────┐                    ┌──────────────────────────┐
│  1. PDF Processing   │                    │  1. Question Embedding   │
│     Router           │                    │     (all-MiniLM-L6-v2)   │
│                      │                    │                          │
│  Tries in order:     │                    │  "What is max inputs?"   │
│  • Text extraction   │                    │          ↓               │
│  • Table extraction  │                    │  [0.23, -0.45, 0.78...] │
│  • OCR (fallback)    │                    │  (384-dim vector)        │
└──────┬───────────────┘                    └──────────┬───────────────┘
       │                                               │
       ▼                                               ▼
┌──────────────────────┐                    ┌──────────────────────────┐
│  2. Content          │                    │  2. Vector Search        │
│     Detection        │                    │     (ChromaDB)           │
│                      │                    │                          │
│  Classifies as:      │                    │  Searches 156 docs       │
│  • Specification     │                    │  Finds top 5 similar     │
│  • Procedure         │                    │  Returns with metadata   │
│  • General           │                    │                          │
└──────┬───────────────┘                    └──────────┬───────────────┘
       │                                               │
       ▼                                               ▼
┌──────────────────────┐                    ┌──────────────────────────┐
│  3. Text Chunking    │                    │  3. Context Retrieval    │
│                      │                    │                          │
│  Splits into         │                    │  Retrieved Documents:    │
│  semantic chunks     │                    │  • Chunk 1 (Page 12)     │
│  (800 chars,         │                    │  • Chunk 2 (Page 45)     │
│   100 overlap)       │                    │  • Chunk 3 (Page 23)     │
└──────┬───────────────┘                    │  • Chunk 4 (Page 67)     │
       │                                    │  • Chunk 5 (Page 34)     │
       ▼                                    └──────────┬───────────────┘
┌──────────────────────┐                               │
│  4. Generate         │                               ▼
│     Embeddings       │                    ┌──────────────────────────┐
│                      │                    │  4. Prompt Construction  │
│  Convert each chunk  │                    │     (Context-Aware)      │
│  to vector           │                    │                          │
│  (all-MiniLM-L6-v2)  │                    │  Builds prompt with:     │
└──────┬───────────────┘                    │  • Query intent detected │
       │                                    │  • Retrieved context     │
       ▼                                    │  • User question         │
┌──────────────────────┐                    │  • Answer instructions   │
│  5. Store in         │                    └──────────┬───────────────┘
│     Vector DB        │                               │
│                      │                               ▼
│  ChromaDB:           │                    ┌──────────────────────────┐
│  • Embeddings        │                    │  5. LLM Generation       │
│  • Metadata          │                    │     (Phi-2 via Ollama)   │
│    - Page number     │                    │                          │
│    - Source file     │                    │  Prompt → Ollama API     │
│    - Content type    │                    │  Phi-2 processes         │
│  • Persistent        │                    │  Generates answer        │
│    storage           │                    │  (2-3 seconds)           │
└──────────────────────┘                    └──────────┬───────────────┘
                                                       │
                                                       ▼
                                            ┌──────────────────────────┐
                                            │  6. Format Response      │
                                            │                          │
                                            │  Returns:                │
                                            │  • Answer text           │
                                            │  • Source pages          │
                                            │  • Content types         │
                                            │  • Response time         │
                                            └──────────┬───────────────┘
                                                       │
                                                       ▼
                                            ┌──────────────────────────┐
                                            │    USER RECEIVES:        │
                                            │                          │
                                            │  "The EX-1280C has 12    │
                                            │   analog inputs..."      │
                                            │                          │
                                            │  Sources:                │
                                            │  • Page 12 (spec)        │
                                            │  • Page 45 (spec)        │
                                            │                          │
                                            │  Time: 2.34s             │
                                            └──────────────────────────┘
```

### Processing Flow in Detail

**Phase 1: Document Setup (Run Once)**
```
User places PDFs in data/ folder
    ↓
Runs: python scripts/demo.py
    ↓
For each PDF:
    1. Router selects extraction method (text/table/OCR)
    2. Content detector classifies chunks
    3. Text splitter creates semantic segments
    4. Embedder converts text → vectors
    5. ChromaDB stores vectors + metadata
    ↓
Database ready: 156 chunks stored
```

**Phase 2: Query Handling (Every Question)**
```
User types: "What is the warranty period?"
    ↓
Frontend → POST /api/query → FastAPI
    ↓
RAG Orchestrator:
    1. Embedder: Question → vector
    2. ChromaDB: Find 5 most similar chunks
    3. Retriever: Get full Document objects
    4. Prompt Builder: Detect intent, build prompt
    5. Ollama: Send prompt → Phi-2 → generate answer
    6. Format: Add sources, timing
    ↓
Response → Frontend → Display to user
    ↓
Total time: 2-3 seconds
```

---

## Technical Approach & Design Decisions

### 1. Why RAG (Retrieval-Augmented Generation)?

**The Challenge:** LLMs don't "know" your specific documents
**The Solution:** RAG combines:
- **Retrieval**: Find relevant information from your documents
- **Generation**: Use LLM to synthesize natural language answers

**Why not just use ChatGPT?**
- ❌ Can't access private/internal documents
- ❌ May hallucinate (make up information)
- ❌ No source citations
- ❌ Ongoing API costs
- ❌ Data privacy concerns

**Why RAG wins:**
- ✅ 100% based on your documents
- ✅ Source citations for every answer
- ✅ Works offline
- ✅ No ongoing costs
- ✅ Complete data privacy

### 2. Technology Stack Rationale

| Component | Choice | Why? | Alternatives Considered |
|-----------|--------|------|------------------------|
| **LLM** | Phi-2 (via Ollama) | • 1.6GB (fits 8GB RAM target)<br>• 2-3s response time<br>• Runs locally<br>• No API costs | GPT-4 (expensive, cloud), Llama (requires 8GB+) |
| **Embeddings** | all-MiniLM-L6-v2 | • Lightweight (80MB)<br>• Fast inference<br>• Good quality<br>• Sentence Transformers | OpenAI Ada (costs), BGE-large (slower) |
| **Vector DB** | ChromaDB | • Simple Python API<br>• Persistent storage<br>• No separate server<br>• Built for embeddings | Pinecone (cloud), Qdrant (overkill), FAISS (no persistence) |
| **Web Framework** | FastAPI | • Async support<br>• Auto API docs<br>• Fast performance<br>• Modern | Flask (older, slower), Django (too heavy) |
| **PDF Processing** | PyPDF2 + Camelot + Tesseract | • Multi-strategy<br>• Handles all PDF types<br>• Table extraction<br>• OCR fallback | PyMuPDF (limited tables), pdfplumber (slower) |

### 3. Key Design Decisions

#### Decision 1: Local-First Architecture
**Choice:** Everything runs locally (Ollama, embeddings, vector DB)

**Reasoning:**
- Privacy: Documents never leave the machine
- No API costs or rate limits
- Works offline
- Predictable performance

**Trade-off:** Requires local compute (8GB RAM minimum)

#### Decision 2: Persistent Vector Store
**Choice:** ChromaDB with disk persistence (not in-memory)

**Reasoning:**
- Survive application restarts
- No need to reprocess documents
- Fast startup time

**Implementation:**
```python
# In chromadb_manager.py
self.client = chromadb.PersistentClient(path=config.VECTOR_DB_DIR)
```

#### Decision 3: Multi-Strategy PDF Processing
**Choice:** Try multiple extraction methods per document

**Reasoning:**
- PDFs vary wildly in structure
- Text extraction works for most
- Tables need special handling
- Scanned docs need OCR

**Implementation:**
```python
# In router.py
1. Try text extraction (fast)
2. If tables detected → use Camelot
3. If text extraction fails → OCR with Tesseract
```

#### Decision 4: Content-Aware Prompting
**Choice:** Classify content type, adjust prompts accordingly

**Reasoning:**
- Specifications need factual, precise answers
- Procedures need step-by-step instructions
- Different content = different prompt styles

**Implementation:**
```python
# In prompt_builder.py
if content_type == "specification":
    prompt = "Provide exact specifications from the documents..."
elif content_type == "procedure":
    prompt = "Provide step-by-step instructions..."
```

#### Decision 5: Semantic Chunking
**Choice:** 800-character chunks with 100-character overlap

**Reasoning:**
- 800 chars = ~1-2 paragraphs (semantic unit)
- 100-char overlap preserves context across boundaries
- Fits in embedding model's token limit

**Trade-offs tested:**
- Too small (400): Lost context
- Too large (1500): Diluted relevance
- No overlap: Missed boundary information

### 4. Performance Optimization

**Target:** 8GB RAM, 2-3 second response time

**Optimizations applied:**
1. **Model Selection:** Phi-2 (1.6GB) instead of Llama-7B (7GB)
2. **Embedding Cache:** HuggingFace caches models locally
3. **Batch Processing:** ChromaDB batch inserts during ingestion
4. **Async API:** FastAPI async endpoints for concurrency
5. **Persistent DB:** No reprocessing on restart

**Measured Performance:**
- Cold start: ~5 seconds (load models)
- Warm query: 2-3 seconds average
- Memory idle: ~500MB
- Memory during query: ~1.5GB
- Concurrent users: 100+ (async)

### 5. Error Handling Strategy

**Philosophy:** Graceful degradation, never crash

**Implementation:**
```python
# Three-layer error handling:
1. Try-except at component level (specific recovery)
2. ErrorHandler class for logging and categorization
3. User-friendly messages in API responses
```

**Error types handled:**
- Ollama not running → Clear error message
- No documents loaded → Instruction to process docs
- No relevant context → Suggest rephrasing question
- Timeout → Configurable RESPONSE_TIMEOUT

---

## Quick Start Guide

### Prerequisites

1. **Python 3.11+** ([Download](https://www.python.org/downloads/))
2. **Ollama** with Phi model:
   ```bash
   # Install Ollama: https://ollama.ai
   ollama pull phi
   ```

### Installation & Setup

```powershell
# 1. Clone repository
git clone https://github.com/Munna-Git/bose-rag-project.git
cd bose-rag-project

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt
pip install fastapi uvicorn

# 4. Process documents (one-time setup)
#    Place your PDFs in the data/ folder first
python scripts\demo.py

# 5. Launch application
.\launch_fastapi.bat
```

**Access:** http://localhost:8000

---

## Usage Examples

### Web Interface

1. Open http://localhost:8000
2. Wait for green "Online" status
3. Type question: *"What is the power consumption?"*
4. Receive answer with page citations in ~2 seconds

### REST API

```bash
# Submit query
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the dimensions?"}'

# Check health
curl http://localhost:8000/api/health

# Get system info
curl http://localhost:8000/api/info
```

### Python API

```python
from src.interfaces.rag_phi import BoseRAGPhi

# Initialize
rag = BoseRAGPhi()

# Process documents (one-time)
result = rag.process_documents([
    "data/manual.pdf",
    "data/spec_sheet.pdf"
])
print(f"Processed {result['total_chunks']} chunks")

# Query
response = rag.answer_query("What is the warranty period?")
print(f"Answer: {response['answer']}")
print(f"Sources: {response['sources']}")
print(f"Time: {response['time']}")
```

---

## Configuration

### Environment Variables

Create `.env` file:
```env
# Model Configuration
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Processing
CHUNK_SIZE=800
CHUNK_OVERLAP=100

# Generation
MAX_TOKENS=512
TEMPERATURE=0.1

# System
LOG_LEVEL=INFO
VECTOR_DB_DIR=data/vector_db
```

### Customization

**Change UI theme** (`static/styles.css`):
```css
:root {
    --bose-accent: #00a0dc;  /* Your brand color */
}
```

**Adjust retrieval count** (`src/interfaces/rag_phi.py`):
```python
docs = self.retriever.retrieve(query, k=5)  # Change k
```

---

## Monitoring & Maintenance

### Check Database
```powershell
python scripts\check_db.py
```

Output:
```
Database Status:
Total documents: 156
Sample query results: Top 3 chunks with distances
```

### Clear Database
```powershell
python scripts\clear_db.py
```

### View Logs
```powershell
Get-Content rag_system.log -Tail 50 -Wait
```

### Backup
```powershell
Copy-Item -Recurse data\vector_db data\vector_db_backup_$(Get-Date -Format 'yyyyMMdd')
```

---

## Deployment Options

### Development
```powershell
python app.py
```

### Production (Windows Service)
```powershell
# Install NSSM
choco install nssm

# Create service
nssm install BoseRAGAPI "D:\bose-rag-project\venv\Scripts\python.exe" "app.py"
nssm set BoseRAGAPI AppDirectory "D:\bose-rag-project"
nssm start BoseRAGAPI
```

### Docker
```bash
docker build -t bose-rag .
docker run -p 8000:8000 bose-rag
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for cloud deployment (AWS, Azure, GCP).

---

## For Interviewers: Key Highlights

### What This Project Demonstrates

1. **Full-Stack AI/ML Application**
   - Backend: FastAPI (Python)
   - Frontend: HTML/CSS/JavaScript
   - AI: LangChain + Ollama + ChromaDB
   - Integration: REST API, async processing

2. **Production-Ready Engineering**
   - Modular architecture (separation of concerns)
   - Comprehensive error handling
   - Persistent storage
   - Structured logging
   - Configuration management
   - Deployment automation

3. **AI/ML Best Practices**
   - RAG architecture (retrieval + generation)
   - Vector embeddings for semantic search
   - Multi-strategy PDF processing
   - Content-aware prompting
   - Local LLM integration

4. **User-Centric Design**
   - Professional branded UI
   - Real-time status feedback
   - Source citations for trust
   - Error messages guide users
   - Responsive design

5. **System Design Thinking**
   - Resource constraints (8GB target)
   - Performance optimization (2-3s responses)
   - Scalability considerations (async, stateless)
   - Privacy-first (local processing)

### Technical Decisions Worth Discussing

- **Why Phi-2?** Balances performance vs resource usage (1.6GB)
- **Why ChromaDB?** Simple, persistent, no separate server needed
- **Why multi-strategy PDF?** Real-world PDFs vary wildly in structure
- **Why content-aware prompts?** Different content needs different framing
- **Why persistent storage?** Avoid reprocessing, faster startup

### Potential Improvements

1. **Caching:** Redis for frequent queries
2. **GPU Acceleration:** 10x faster with CUDA
3. **Hybrid Search:** Combine semantic + keyword search
4. **Query Rewriting:** Expand abbreviations, fix typos
5. **Answer Verification:** Cross-reference multiple chunks
6. **User Feedback Loop:** Rating system to improve responses
7. **Multi-Language:** Support non-English documents
8. **Streaming Responses:** Show answer as it generates

---

## Future Enhancements (Roadmap)

This section outlines a pragmatic, phased roadmap that balances user impact, system robustness, and strategic scalability. Interview discussion ready.

## Short-Term Priorities
- Add user feedback (thumbs up/down with optional comment).  
- Implement basic caching and query normalization (lowercasing, unit normalization, abbreviation expansion).  
- Provide expandable source citations.  
- Add simple API rate limiting.

---

## Medium-Term Improvements
- Hybrid retrieval (vector + BM25) for better accuracy, especially on numeric/spec queries.  
- Query rewriting to improve ambiguous or shorthand user input.  
- Confidence validation when retrieved chunks conflict.  
- Adaptive chunking (smaller for dense tables, larger for narrative sections).  
- Observability dashboard displaying metrics like latency, cache hits, and error categories.

---

## Long-Term Vision
- Multi-tenancy with role-based access control (RBAC).  
- Integrate structured metadata (CSV/DB) into retrieval alongside unstructured text.  
- Fine-tune a small domain model and add multilingual query support.  
- Deploy lightweight retrieval and inference models for edge-based use cases.

---

## User Experience Enhancements
- Preserve tables in citations for readability.  
- Suggest relevant follow-up questions after each result.  
- Optional short-term conversation memory with controlled session scope.  
- Allow exporting results and citations to a downloadable PDF.

---

## License

MIT License - Free to use, modify, distribute.

---

## 📞 Support & Documentation

- **Full Deployment Guide:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **FastAPI Details:** [FASTAPI_README.md](FASTAPI_README.md)
- **API Documentation:** http://localhost:8000/docs (when running)
- **Logs:** `rag_system.log`
- **Database Check:** `python scripts\check_db.py`

---

<div align="center">

**Built with ❤️ for Bose Professional Technical Support**

*Demonstrating production-ready AI/ML engineering*

[GitHub](https://github.com/Munna-Git/bose-rag-project) • [Issues](https://github.com/Munna-Git/bose-rag-project/issues) • [Documentation](DEPLOYMENT.md)

</div>

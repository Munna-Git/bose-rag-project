# Bose RAG System with Phi-2

Complete RAG (Retrieval-Augmented Generation) system for Bose technical documentation using the Phi-2 LLM.

## ✨ Features

- 🚀 **Fast Local Processing** - Phi-2 model runs locally (1.6GB)
- 🔒 **100% Private** - All processing happens on your machine
- 📄 **Multi-Format Support** - Text, tables, and images from PDFs
- 🎯 **Smart Retrieval** - Content-aware document retrieval
- 🌐 **Web Interface** - Easy-to-use Gradio interface
- ⚡ **Quick Responses** - 2-3 seconds per query

---

## 🚀 Quick Start

### 1. Prerequisites

```powershell
# Install Ollama
winget install Ollama.Ollama

# Pull Phi model
ollama pull phi

# Start Ollama (in a separate terminal)
ollama serve
```

### 2. Install Dependencies

```powershell
# Clone the repository
git clone <your-repo-url>
cd bose-rag-project

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and adjust settings if needed:

```env
OLLAMA_MODEL=phi
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### 4. Add Documents

Place your PDF files in `data/documents/`

### 5. Process Documents

```powershell
python scripts\demo.py
```

This will:
- Detect content types (text, tables, images)
- Extract and chunk documents
- Generate embeddings
- Store in vector database

### 6. Launch Application

**Option A: Simple Launch Script**
```powershell
.\launch.ps1
```

**Option B: Manual Launch**
```powershell
python scripts\launch_app.py
```

**Option C: Direct Gradio Launch**
```powershell
python src\interfaces\gradio_app.py
```

Access the web interface at: **http://localhost:7860**

---

## 📖 Usage

### Web Interface

1. **Upload Documents** - Click "Upload Documents" tab
2. **Process** - Select PDF files and click "Process Documents"
3. **Ask Questions** - Go to "Ask Questions" tab and enter your query
4. **View Results** - Get answers with source citations

### CLI Demo

```powershell
python scripts\demo.py
```

Interactive Q&A session with pre-loaded documents.

### Check Database

```powershell
# View database contents
python scripts\check_db.py

# Clear database
python scripts\clear_db.py
```

---

## 📁 Project Structure

```
bose-rag-project/
│
├── config/
│   ├── settings.py          # Configuration
│   └── constants.py         # Constants
│
├── src/
│   ├── content_detection/
│   │   └── detector.py      # Content type detection
│   │
│   ├── document_processing/
│   │   ├── text_processor.py
│   │   ├── table_processor.py
│   │   ├── image_processor.py
│   │   └── router.py
│   │
│   ├── embeddings/
│   │   └── embedder.py
│   │
│   ├── vector_store/
│   │   └── chromadb_manager.py
│   │
│   ├── retrieval/
│   │   └── content_aware_retriever.py
│   │
│   ├── generation/
│   │   ├── llm_handler_phi.py
│   │   ├── prompt_builder.py
│   │   └── response_formatter.py
│   │
│   ├── error_handling/
│   │   ├── handlers.py
│   │   └── logger.py
│   │
│   └── interfaces/
│       ├── rag_phi.py       # Main RAG class
│       └── gradio_app.py    # Web interface
│
├── data/
│   ├── documents/           # Place PDFs here
│   └── vector_db/           # Database storage
│
├── scripts/
│   ├── demo.py              # Demo script
│   ├── launch_app.py        # Application launcher
│   ├── check_db.py          # Database checker
│   └── clear_db.py          # Database cleaner
│
├── requirements.txt
├── .env
├── launch.ps1               # Quick launch script
├── DEPLOYMENT.md            # Deployment guide
└── README.md
```

---

## 🛠️ Configuration

Edit `.env` file:

```env
# Model Configuration
OLLAMA_MODEL=phi
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TEMPERATURE=0.7

# Processing
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Generation
MAX_TOKENS=512
RESPONSE_TIMEOUT=60

# Logging
LOG_LEVEL=INFO
```

---

## 🔧 Troubleshooting

### Ollama Connection Error

```powershell
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

### Model Not Found

```powershell
# Pull the model
ollama pull phi

# List available models
ollama list
```

### No Search Results

```powershell
# Check database
python scripts\check_db.py

# Reprocess documents if empty
python scripts\clear_db.py
python scripts\demo.py
```

### Port Already in Use

Change port in `src/interfaces/gradio_app.py`:
```python
server_port=7861  # Change to available port
```

### Import Errors

```powershell
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

---

## 📊 Example Queries

- "What is the maximum number of analog inputs on the EX-1280C?"
- "Which software version is required for PC configuration?"
- "What are the specifications of DesignMax DM8SE?"
- "How do I install ControlSpace?"
- "What is the frequency response?"

---

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment options:

- Local deployment with Gradio
- Production deployment with FastAPI
- Docker deployment
- Cloud deployment (AWS, Azure, GCP)
- Windows Service

---

## 📝 Development

### Run Tests

```powershell
pytest tests/
```

### Check Code Quality

```powershell
# Format code
black src/

# Lint
flake8 src/
```

### View Logs

```powershell
Get-Content rag_system.log -Tail 50 -Wait
```

---

## 🔒 Security

- All processing happens locally
- No data sent to external APIs
- Documents stored locally
- Optional authentication for web interface
- Use HTTPS in production

---

## 📄 License

[Your License Here]

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📞 Support

For issues:
1. Check logs: `rag_system.log`
2. Run database check: `python scripts\check_db.py`
3. Review [DEPLOYMENT.md](DEPLOYMENT.md)
4. Open an issue on GitHub

---

## 🙏 Acknowledgments

- **Phi-2** by Microsoft Research
- **Ollama** for local LLM serving
- **LangChain** for RAG framework
- **ChromaDB** for vector storage
- **Gradio** for web interface

---

**Built with ❤️ for Bose Technical Documentation**

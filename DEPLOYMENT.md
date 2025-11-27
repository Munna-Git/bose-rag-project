# Deployment Guide - Bose RAG System

## Prerequisites

1. **Ollama must be running** on the deployment machine
2. **Phi model must be pulled**: `ollama pull phi`
3. **Python 3.11+** installed
4. **Documents processed** (run demo.py first to populate database)

---

## Option 1: Local Deployment (Gradio Web Interface)

### Quick Start

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Launch Gradio app
python src\interfaces\gradio_app.py
```

Access at: **http://localhost:7860**

### With Public URL (Share Link)

```powershell
python src\interfaces\gradio_app.py --share
```

This creates a temporary public URL (valid for 72 hours) that you can share with others.

---

## Option 2: Production Deployment (FastAPI with Professional UI)

### Quick Start

The project includes a production-ready FastAPI application with a professional Bose-style web interface.

```powershell
# Install FastAPI dependencies
pip install fastapi uvicorn

# Launch using the convenience script
.\launch_fastapi.ps1
```

Or manually:
```powershell
python app.py
```

**Access the application:**
- **Web Interface:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

### Features

✅ **Professional Bose-branded UI** with dark theme and brand colors  
✅ **Real-time status monitoring** (system health, document count)  
✅ **Chat interface** for technical questions  
✅ **Source citations** with page numbers and content types  
✅ **REST API** with OpenAPI documentation  
✅ **Responsive design** for desktop and mobile  

### API Endpoints

**POST /api/query** - Submit a technical question
```json
{
  "question": "What is the maximum number of analog inputs?",
  "verbose": false
}
```

**GET /api/health** - Check system health
```json
{
  "status": "healthy",
  "model": "phi-2",
  "documents_loaded": true,
  "document_count": 156
}
```

**GET /api/info** - Get detailed system information

### Customization

Edit `static/styles.css` to customize the UI theme:
```css
:root {
    --bose-accent: #00a0dc;  /* Primary brand color */
    --bose-dark: #1a1a1a;     /* Background color */
}
```

---

## Option 3: Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ghostscript \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose ports
EXPOSE 7860

# Run Gradio app
CMD ["python", "src/interfaces/gradio_app.py"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    command: serve

  rag-app:
    build: .
    ports:
      - "7860:7860"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama
    volumes:
      - ./data:/app/data

volumes:
  ollama_data:
```

Build and run:
```powershell
docker-compose up -d
```

---

## Option 4: Windows Service Deployment

### Create Windows Service Script

Install `nssm` (Non-Sucking Service Manager):
```powershell
choco install nssm
```

Create service:
```powershell
nssm install BoseRAG "D:\bose-rag-project\venv\Scripts\python.exe" "D:\bose-rag-project\src\interfaces\gradio_app.py"
nssm set BoseRAG AppDirectory "D:\bose-rag-project"
nssm start BoseRAG
```

---

## Configuration for Production

### 1. Update .env for Production

```env
# Production settings
OLLAMA_BASE_URL=http://localhost:11434
LOG_LEVEL=WARNING
MAX_TOKENS=512
RESPONSE_TIMEOUT=120
```

### 2. Enable Authentication (Gradio)

Modify `gradio_app.py` launch:

```python
demo.launch(
    share=False,
    server_name="0.0.0.0",
    server_port=7860,
    auth=("admin", "your_password_here")  # Add authentication
)
```

### 3. Setup HTTPS with Nginx

Install Nginx and configure:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support for Gradio
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## Cloud Deployment Options

### AWS EC2
1. Launch EC2 instance (t3.medium or larger)
2. Install Ollama and Python
3. Clone repository
4. Follow Local Deployment steps
5. Use Elastic IP for permanent address

### Azure VM
1. Create Ubuntu VM
2. Install dependencies
3. Configure Network Security Group (port 7860)
4. Deploy application

### Google Cloud VM
1. Create Compute Engine instance
2. Configure firewall rules
3. Deploy application

---

## Monitoring & Maintenance

### View Logs
```powershell
Get-Content rag_system.log -Tail 50 -Wait
```

### Check Database Status
```powershell
python scripts\check_db.py
```

### Clear and Reprocess Documents
```powershell
python scripts\clear_db.py
python scripts\demo.py
```

### Backup Database
```powershell
# Backup vector database
Copy-Item -Recurse data\vector_db data\vector_db_backup_$(Get-Date -Format 'yyyyMMdd')
```

---

## Performance Optimization

### 1. Use GPU (if available)
Update `.env`:
```env
OLLAMA_NUM_GPU=1
```

### 2. Adjust Chunk Settings
```env
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
```

### 3. Increase Context Window
```env
MAX_TOKENS=1024
```

### 4. Enable Caching
Add Redis for response caching (optional)

---

## Troubleshooting

### Ollama Not Found
```powershell
# Check if Ollama is running
curl http://localhost:11434/api/tags
```

### Port Already in Use
```powershell
# Change port in gradio_app.py
server_port=7861
```

### Out of Memory
- Reduce `CHUNK_SIZE`
- Reduce `MAX_TOKENS`
- Process documents in smaller batches

---

## Security Checklist

- [ ] Enable authentication on Gradio
- [ ] Use HTTPS in production
- [ ] Restrict IP access with firewall
- [ ] Regular security updates
- [ ] Backup database regularly
- [ ] Monitor logs for suspicious activity
- [ ] Use environment variables for secrets
- [ ] Don't expose Ollama API publicly

---

## Quick Commands Reference

```powershell
# Start FastAPI application (Professional UI)
.\launch_fastapi.ps1
# or
python app.py

# Start Gradio application (Alternative)
python src\interfaces\gradio_app.py

# Start with public URL (Gradio only)
python src\interfaces\gradio_app.py --share

# Check database
python scripts\check_db.py

# Clear database
python scripts\clear_db.py

# Run demo/test
python scripts\demo.py

# View logs
Get-Content rag_system.log -Tail 50

# Check Ollama
ollama list
ollama ps
```

---

## Support

For issues:
1. Check logs: `rag_system.log`
2. Verify Ollama is running
3. Check database: `python scripts\check_db.py`
4. Review configuration in `.env`

# Bose Professional Technical Assistant - FastAPI Deployment

## What's New

This deployment uses **FastAPI with a professional Bose-branded UI** that mimics the look and feel of Bose Professional's support interface.

## Quick Start

```powershell
# 1. Ensure Ollama is running with the phi model
ollama pull phi

# 2. Process your documents (if not already done)
python scripts\demo.py

# 3. Launch the FastAPI application
.\launch_fastapi.ps1
```

Visit: **http://localhost:8000**

## What This Gives You

### Professional UI Features
- 🎨 **Bose Professional Branding** - Dark theme with official brand colors
- 💬 **Chat Interface** - Clean, modern conversation UI
- 📊 **System Status** - Real-time monitoring dashboard
- 📚 **Source Citations** - Automatic source references with page numbers
- 📱 **Responsive Design** - Works on desktop and mobile

### Technical Features
- ⚡ **FastAPI Backend** - High-performance async API
- 🔒 **Type Safety** - Pydantic models for validation
- 📖 **Auto Documentation** - OpenAPI/Swagger UI at `/docs`
- 🔍 **REST API** - Easy integration with other systems
- 🌐 **Production Ready** - Deploy anywhere that supports Python

## File Structure

```
bose-rag-project/
├── app.py                 # FastAPI application (main server)
├── launch_fastapi.ps1     # Convenience launcher script
└── static/                # Frontend assets
    ├── index.html         # Main UI page
    ├── styles.css         # Bose Professional styling
    └── app.js             # Frontend logic
```

## API Endpoints

### POST /api/query
Submit a technical question
```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the specifications of the EX-1280C?"}'
```

### GET /api/health
Check system status
```bash
curl http://localhost:8000/api/health
```

### GET /api/info
Get detailed system information
```bash
curl http://localhost:8000/api/info
```

## Customization

### Change Brand Colors
Edit `static/styles.css`:
```css
:root {
    --bose-accent: #00a0dc;  /* Change to your brand color */
}
```

### Change Port
Edit `app.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8080)  # Change port here
```

### Add Authentication
Edit `app.py` to add auth middleware or use FastAPI's security features.

## Why This Impresses

1. **Professional Appearance** - Looks like a real Bose product
2. **Production Ready** - Not just a demo, it's deployment-ready
3. **Modern Stack** - FastAPI is industry standard for AI APIs
4. **Full Featured** - Status monitoring, error handling, source citations
5. **API First** - Easy to integrate, extend, or embed
6. **Interview Ready** - Shows full-stack capabilities

## Troubleshooting

### Port 8000 in use?
Change the port in `app.py` or kill the existing process:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

### Ollama not connecting?
Check Ollama is running:
```powershell
curl http://localhost:11434/api/tags
```

### No documents loaded?
Process documents first:
```powershell
python scripts\demo.py
```

## Next Steps

- Add user authentication
- Deploy to cloud (AWS, Azure, GCP)
- Add more API endpoints
- Integrate with existing systems
- Add analytics/logging
- Scale with load balancer

---

**Tip for Interview**: Mention that this architecture allows easy scaling - you can add Redis caching, deploy multiple instances behind a load balancer, and the API design makes it simple to integrate with existing enterprise systems.

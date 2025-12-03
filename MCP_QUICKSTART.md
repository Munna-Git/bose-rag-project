# 🚀 MCP Quick Start Guide

## What is MCP?

**Model Context Protocol (MCP)** is a standard protocol for exposing AI/ML capabilities as discoverable, callable tools. Think of it as an API standard for AI services.

## What We Built

✅ **MCP Server** - Exposes Bose RAG system as 3 MCP tools  
✅ **MCP Client** - Demonstrates tool discovery and invocation  
✅ **Standard Protocol** - Follows MCP specification  

## Quick Test (5 minutes)

### Step 1: Start MCP Server

Terminal 1:
```powershell
python mcp_server.py
```

You should see:
```
Starting Bose RAG MCP Server
Server will run on: http://localhost:8001
```

### Step 2: Run Client Test

Terminal 2:
```powershell
python mcp_client.py
```

This will automatically:
1. ✅ Connect to server
2. ✅ List 3 available tools
3. ✅ Query documentation ("What is power of DM8SE?")
4. ✅ Get system metrics
5. ✅ Test caching (repeat same query)
6. ✅ Clear cache

**Expected Output:**
```
✅ SUCCESS
======================================================================
**Answer:** The DesignMax DM8SE has a power rating of 125 watts...

**Confidence:** 87% (high)

**Sources:**
1. tds_DesignMax_DM8SE_a4_EN.pdf (Page 1)
...
**Query Time:** 0.85s 🔥 (cached)
```

### Step 3 (Optional): Manual Testing

Test with curl:
```powershell
# Get server info
curl http://localhost:8001/

# List tools
curl http://localhost:8001/mcp/tools

# Call query tool
curl -X POST http://localhost:8001/mcp/tools/call `
  -H "Content-Type: application/json" `
  -d '{"name":"query_bose_documentation","arguments":{"question":"What is EX-1280?"}}'
```

## Architecture Diagram

```
┌──────────────┐
│  mcp_client  │  ← You run this to test
└──────┬───────┘
       │ HTTP/JSON (MCP Protocol)
       ↓
┌──────────────┐
│  mcp_server  │  ← Runs on port 8001
│  (FastAPI)   │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│  BoseRAGPhi  │  ← Your existing RAG system
│  (Phi-2 LLM) │
└──────────────┘
```

## Available MCP Tools

### 1. query_bose_documentation
**Purpose:** Answer technical questions  
**Input:**
```json
{
  "question": "What is the frequency response of DM8SE?",
  "verbose": false
}
```
**Output:** Answer + confidence + sources + timing

### 2. get_system_metrics
**Purpose:** Performance monitoring  
**Input:** None  
**Output:** Query stats, latency, cache performance

### 3. clear_cache
**Purpose:** Cache management  
**Input:** None  
**Output:** Confirmation message

## MCP Protocol Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Server info |
| `/mcp/tools` | GET | List available tools (discovery) |
| `/mcp/tools/call` | POST | Execute a tool |

## Integration with Main App

Both can run simultaneously:
- **Main App:** `python app.py` → Port 8000 (Web UI)
- **MCP Server:** `python mcp_server.py` → Port 8001 (MCP API)

They share the same:
- RAG system instance
- ChromaDB database
- Query cache
- Metrics collector

## Troubleshooting

**Problem:** "Connection refused"  
**Solution:** Make sure MCP server is running: `python mcp_server.py`

**Problem:** "RAG system not initialized"  
**Solution:** Wait 10 seconds after starting server (loading models)

**Problem:** Port 8001 already in use  
**Solution:** Stop other services or edit `mcp_server.py` to use different port

## Demo for Interview

1. **Show MCP server starting** - highlight port 8001, FastAPI
2. **Run client script** - full automated test
3. **Show tool discovery** - `/mcp/tools` lists 3 tools
4. **Execute query tool** - structured response with answer, confidence, sources
5. **Show metrics tool** - performance data
6. **Demonstrate caching** - second query instant (<1s vs 25s)

**Key Points to Mention:**
- ✅ Standard MCP protocol compliance
- ✅ Tool discovery via REST API
- ✅ Structured JSON responses
- ✅ Non-invasive wrapper (doesn't modify RAG code)
- ✅ Client-server communication demonstrated
- ✅ Extensible (easy to add more tools)

## Files Overview

```
mcp_server.py         ← MCP server implementation (FastAPI)
mcp_client.py         ← Test client (demonstrates protocol)
MCP_README.md         ← Detailed documentation
test_mcp.bat          ← Automated test script
```

## Success Criteria

✅ Server starts without errors  
✅ Client connects successfully  
✅ Tool discovery returns 3 tools  
✅ Query tool executes and returns structured answer  
✅ Metrics tool shows performance data  
✅ Cache tool works  
✅ Repeated query shows cache benefit  

## Time Required

- **Setup:** 0 minutes (already implemented)
- **Server startup:** ~5 seconds
- **Client test:** ~30 seconds
- **Total demo:** 2-3 minutes

---

**Stretch goal complete!** 🎯 Simple, functional, interview-ready MCP integration.

# Model Context Protocol (MCP) Integration

## Overview

This project includes a **Model Context Protocol (MCP)** implementation that wraps the Bose RAG system as MCP-compliant tools.

## Architecture

```
┌─────────────────┐
│   MCP Client    │  (mcp_client.py)
│  Test Script    │
└────────┬────────┘
         │ HTTP/JSON
         ↓
┌─────────────────┐
│   MCP Server    │  (mcp_server.py - Port 8001)
│   FastAPI App   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   RAG System    │  (BoseRAGPhi)
│   Phi-2 + DB    │
└─────────────────┘
```

## Components

### 1. MCP Server (`mcp_server.py`)
- **Framework:** FastAPI (lightweight, MCP-compliant REST API)
- **Port:** 8001 (separate from main app on 8000)
- **Protocol:** Standard Model Context Protocol

**Endpoints:**
- `GET /` - Server information and status
- `GET /mcp/tools` - List available MCP tools
- `POST /mcp/tools/call` - Execute an MCP tool

**MCP Tools Exposed:**
1. **query_bose_documentation** - Main RAG query tool
   - Input: `question` (string), `verbose` (bool, optional)
   - Output: Answer, confidence, sources, timing
   
2. **get_system_metrics** - Performance monitoring
   - Input: None
   - Output: Query stats, latency, cache performance
   
3. **clear_cache** - Cache management
   - Input: None
   - Output: Success confirmation

### 2. MCP Client (`mcp_client.py`)
- Simple Python client demonstrating MCP communication
- Methods:
  - `get_server_info()` - Check server status
  - `list_tools()` - Discover available tools
  - `call_tool(name, args)` - Generic tool invocation
  - Convenience methods for each tool

## MCP Protocol Compliance

### Tool Discovery (Standard MCP)
```json
GET /mcp/tools
{
  "tools": [
    {
      "name": "query_bose_documentation",
      "description": "...",
      "inputSchema": {
        "type": "object",
        "properties": {...},
        "required": [...]
      }
    }
  ]
}
```

### Tool Invocation (Standard MCP)
```json
POST /mcp/tools/call
{
  "name": "query_bose_documentation",
  "arguments": {
    "question": "What is the power of DM8SE?",
    "verbose": false
  }
}
```

### Tool Response (Standard MCP)
```json
{
  "content": [
    {
      "type": "text",
      "text": "**Answer:** The DesignMax DM8SE..."
    },
    {
      "type": "text",
      "text": "**Confidence:** 87% (high)"
    }
  ],
  "isError": false
}
```

## Usage

### Start MCP Server
```powershell
python mcp_server.py
```
Server starts on `http://localhost:8001`

### Run MCP Client Test
```powershell
python mcp_client.py
```

This will:
1. ✅ Connect to MCP server
2. ✅ List available tools
3. ✅ Query documentation
4. ✅ Get system metrics
5. ✅ Test caching
6. ✅ Clear cache

### Manual Testing with curl
```powershell
# Get server info
curl http://localhost:8001/

# List tools
curl http://localhost:8001/mcp/tools

# Call a tool
curl -X POST http://localhost:8001/mcp/tools/call `
  -H "Content-Type: application/json" `
  -d '{
    "name": "query_bose_documentation",
    "arguments": {
      "question": "What is the frequency response of DM8SE?"
    }
  }'
```

## Integration with Existing System

The MCP server **wraps** the existing RAG system without modifying it:
- Uses same `BoseRAGPhi` class
- Accesses same ChromaDB database
- Shares query cache and metrics
- No duplicate resources

**Running Both Servers:**
- Main FastAPI App: `python app.py` → Port 8000 (Web UI)
- MCP Server: `python mcp_server.py` → Port 8001 (MCP API)
- Both can run simultaneously

## Why This Implementation?

✅ **Simple:** Minimal code, easy to understand  
✅ **Standard:** Follows MCP protocol specification  
✅ **Non-invasive:** Doesn't modify existing RAG code  
✅ **Functional:** Demonstrates server-client communication  
✅ **Extensible:** Easy to add more tools  
✅ **Interview-ready:** Clear demonstration of protocol understanding  

## Testing Checklist

- [ ] Start MCP server successfully
- [ ] Client connects and gets server info
- [ ] Client lists 3 tools
- [ ] Tool execution returns structured response
- [ ] Query tool provides answer + confidence + sources
- [ ] Metrics tool shows performance data
- [ ] Cache tool clears successfully
- [ ] Repeated query shows cache hit
- [ ] Error handling works (invalid tool, missing args)

## MCP Compliance Features

✅ Standard REST endpoints  
✅ Tool discovery via `/mcp/tools`  
✅ Tool execution via `/mcp/tools/call`  
✅ JSON Schema for input validation  
✅ Structured content responses  
✅ Error handling with `isError` flag  
✅ Tool metadata (name, description, schema)  

## Performance

- **Server startup:** ~5s (loads RAG system)
- **Tool discovery:** <10ms
- **Query tool:** ~25s first query, <1s cached
- **Metrics/cache tools:** <100ms
- **Memory overhead:** Minimal (shares RAG resources)

## Future Enhancements (Optional)

- WebSocket support for streaming responses
- Authentication/authorization
- Rate limiting
- Tool result caching
- Multiple RAG system instances
- Async tool execution

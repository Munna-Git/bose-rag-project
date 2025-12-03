"""
MCP (Model Context Protocol) Server for Bose RAG System
A simple FastAPI-based MCP server that exposes RAG functionality as MCP tools
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.interfaces.rag_phi import BoseRAGPhi
from src.error_handling.logger import logger

# Initialize MCP FastAPI app (separate from main app)
mcp_app = FastAPI(
    title="Bose RAG MCP Server",
    description="Model Context Protocol server for Bose Professional Audio RAG system",
    version="1.0.0"
)

# Initialize RAG system
rag_system: Optional[BoseRAGPhi] = None


class MCPToolRequest(BaseModel):
    """MCP Tool Request - standard MCP format"""
    name: str
    arguments: Dict[str, Any]


class MCPToolResponse(BaseModel):
    """MCP Tool Response - standard MCP format"""
    content: List[Dict[str, Any]]
    isError: bool = False


class MCPListToolsResponse(BaseModel):
    """MCP List Tools Response"""
    tools: List[Dict[str, Any]]


@mcp_app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup"""
    global rag_system
    try:
        logger.info("Initializing MCP Server...")
        rag_system = BoseRAGPhi()
        logger.info("MCP Server initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MCP Server: {e}")
        raise


@mcp_app.get("/")
async def root():
    """MCP Server info"""
    return {
        "name": "Bose RAG MCP Server",
        "version": "1.0.0",
        "protocol": "MCP",
        "description": "Model Context Protocol server for Bose Professional Audio technical documentation",
        "capabilities": ["tools"],
        "status": "ready" if rag_system else "initializing"
    }


@mcp_app.get("/mcp/tools", response_model=MCPListToolsResponse)
async def list_tools():
    """
    List available MCP tools
    Standard MCP endpoint for tool discovery
    """
    tools = [
        {
            "name": "query_bose_documentation",
            "description": "Search and answer questions about Bose Professional Audio equipment using RAG system. Retrieves relevant documentation and generates accurate technical answers.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Technical question about Bose audio equipment (specifications, installation, troubleshooting, etc.)"
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Include intermediate steps and source documents in response",
                        "default": False
                    }
                },
                "required": ["question"]
            }
        },
        {
            "name": "get_system_metrics",
            "description": "Get performance metrics and statistics from the RAG system including query latency, cache hit rate, and confidence scores.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "clear_cache",
            "description": "Clear the query cache to force fresh retrieval and generation for all queries.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    ]
    
    return MCPListToolsResponse(tools=tools)


@mcp_app.post("/mcp/tools/call", response_model=MCPToolResponse)
async def call_tool(request: MCPToolRequest):
    """
    Call an MCP tool
    Standard MCP endpoint for tool execution
    """
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    tool_name = request.name
    arguments = request.arguments
    
    logger.info(f"MCP Tool call: {tool_name} with args: {arguments}")
    
    try:
        # Route to appropriate tool handler
        if tool_name == "query_bose_documentation":
            return await handle_query_tool(arguments)
        elif tool_name == "get_system_metrics":
            return await handle_metrics_tool(arguments)
        elif tool_name == "clear_cache":
            return await handle_clear_cache_tool(arguments)
        else:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return MCPToolResponse(
            content=[{
                "type": "text",
                "text": f"Error executing tool: {str(e)}"
            }],
            isError=True
        )


async def handle_query_tool(arguments: Dict[str, Any]) -> MCPToolResponse:
    """Handle query_bose_documentation tool"""
    question = arguments.get("question")
    verbose = arguments.get("verbose", False)
    
    if not question:
        raise HTTPException(status_code=400, detail="Missing required argument: question")
    
    # Execute RAG query
    result = rag_system.answer_query(question, verbose=verbose)
    
    # Format as MCP response
    content = []
    
    # Main answer
    content.append({
        "type": "text",
        "text": f"**Answer:** {result['answer']}\n\n"
    })
    
    # Add confidence if available
    if result.get('confidence'):
        confidence = result['confidence']
        content.append({
            "type": "text",
            "text": f"**Confidence:** {confidence['overall']*100:.0f}% ({confidence['label']})\n"
        })
    
    # Add sources
    if result.get('sources'):
        sources_text = "**Sources:**\n"
        for i, source in enumerate(result['sources'][:3], 1):
            source_name = source.get('source', 'Unknown')
            page = source.get('page', '?')
            sources_text += f"{i}. {source_name} (Page {page})\n"
        content.append({
            "type": "text",
            "text": sources_text
        })
    
    # Add timing
    content.append({
        "type": "text",
        "text": f"\n**Query Time:** {result.get('time', 'N/A')}"
    })
    
    # Add cache indicator
    if result.get('cache_hit'):
        content.append({
            "type": "text",
            "text": " 🔥 (cached)"
        })
    
    return MCPToolResponse(content=content, isError=False)


async def handle_metrics_tool(arguments: Dict[str, Any]) -> MCPToolResponse:
    """Handle get_system_metrics tool"""
    metrics = rag_system.get_metrics()
    
    if not metrics.get('enabled'):
        return MCPToolResponse(
            content=[{
                "type": "text",
                "text": "Metrics collection is disabled. Enable ENABLE_METRICS in settings."
            }],
            isError=False
        )
    
    summary = metrics.get('summary', {})
    overview = summary.get('overview', {})
    cache = summary.get('cache', {})
    latency = summary.get('latency', {})
    
    metrics_text = f"""**System Metrics**

**Overview:**
- Total Queries: {overview.get('total_queries', 0)}
- Success Rate: {overview.get('success_rate', 0)}%
- Failed: {overview.get('failed', 0)}

**Latency:**
- Average: {latency.get('average', 0):.2f}s
- Median: {latency.get('median', 0):.2f}s
- Max: {latency.get('max', 0):.2f}s

**Cache Performance:**
- Hit Rate: {cache.get('hit_rate', 0):.1f}%
- Hits: {cache.get('hits', 0)}
- Misses: {cache.get('misses', 0)}
"""
    
    return MCPToolResponse(
        content=[{"type": "text", "text": metrics_text}],
        isError=False
    )


async def handle_clear_cache_tool(arguments: Dict[str, Any]) -> MCPToolResponse:
    """Handle clear_cache tool"""
    rag_system.clear_cache()
    
    return MCPToolResponse(
        content=[{
            "type": "text",
            "text": "✓ Query cache cleared successfully"
        }],
        isError=False
    )


if __name__ == "__main__":
    import uvicorn
    print("=" * 70)
    print("Starting Bose RAG MCP Server")
    print("=" * 70)
    print("Server will run on: http://localhost:8001")
    print("\nAvailable endpoints:")
    print("  GET  /              - Server info")
    print("  GET  /mcp/tools     - List available tools")
    print("  POST /mcp/tools/call - Call a tool")
    print("=" * 70)
    
    uvicorn.run(mcp_app, host="0.0.0.0", port=8001, log_level="info")

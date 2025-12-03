"""
TUTORIAL 2: MCP with Your Bose RAG System
Step-by-step building a real MCP server for your project
"""

import sys
import os

# ============================================================
# STEP 1: Import Your Existing RAG System
# ============================================================
print("=" * 60)
print("STEP 1: Loading Your RAG System")
print("=" * 60)

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.interfaces.rag_phi import BoseRAGPhi

# Initialize your existing RAG (no changes needed!)
rag = BoseRAGPhi()
print("✓ RAG system loaded successfully")
print(f"✓ Using database: {rag.db_path}")
print()

# ============================================================
# STEP 2: Wrap Your RAG as an MCP Tool
# ============================================================
print("=" * 60)
print("STEP 2: Creating MCP Tool from RAG")
print("=" * 60)

# This is the tool description
query_tool = {
    "name": "query_bose_documentation",
    "description": "Query Bose Professional Audio documentation using RAG",
    "inputSchema": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "Your question about Bose products"
            }
        },
        "required": ["question"]
    }
}

print("Tool created:")
print(f"  Name: {query_tool['name']}")
print(f"  Description: {query_tool['description']}")
print(f"  Required input: question (string)")
print()

# ============================================================
# STEP 3: Execute Tool (Call Your RAG)
# ============================================================
print("=" * 60)
print("STEP 3: Executing Tool")
print("=" * 60)

def execute_query_tool(question: str):
    """This function calls your RAG system"""
    print(f"\n📝 Question: {question}")
    
    # Call your existing RAG system (no changes!)
    result = rag.answer_query(question)
    
    # Format response in MCP format
    mcp_response = {
        "content": [
            {
                "type": "text",
                "text": f"Answer: {result['answer']}\n\n"
                       f"Confidence: {result.get('confidence', {}).get('overall', 0)*100:.0f}%\n"
                       f"Time: {result.get('time', 'N/A')}\n"
                       f"Sources: {len(result.get('sources', []))} documents"
            }
        ],
        "isError": False
    }
    
    return mcp_response

# Test it!
print("\nTesting MCP tool with a real query...")
response = execute_query_tool("What is the power of DM8SE?")

print("\n✓ MCP Response:")
print(response['content'][0]['text'])
print()

# ============================================================
# STEP 4: Complete MCP Server (Conceptual)
# ============================================================
print("=" * 60)
print("STEP 4: How MCP Server Works")
print("=" * 60)

print("""
In mcp_server.py, we create a FastAPI server that:

1. ENDPOINT: GET /mcp/tools
   Returns list of available tools:
   → [{"name": "query_bose_documentation", ...}]

2. ENDPOINT: POST /mcp/tools/call
   Accepts: {"name": "query_bose_documentation", "arguments": {"question": "..."}}
   Calls: execute_query_tool(question)
   Returns: {"content": [...], "isError": false}

3. Runs on separate port (8001) so it doesn't interfere with main app (8000)

4. Other programs can now:
   - Discover your tools (GET /mcp/tools)
   - Use your RAG system (POST /mcp/tools/call)
   - Get structured responses
""")

print()
print("=" * 60)
print("NEXT: Run the actual MCP server and client!")
print("=" * 60)
print("\nTerminal 1: python mcp_server.py")
print("Terminal 2: python mcp_client.py")
print("\nOr use the batch file: test_mcp.bat")

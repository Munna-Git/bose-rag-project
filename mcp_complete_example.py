"""
🎯 COMPLETE MCP EXAMPLE - Everything in One File
This shows the ENTIRE flow from question to answer
"""

import sys
import os

print("="*70)
print(" MCP COMPLETE FLOW DEMONSTRATION ".center(70))
print("="*70)

# ================================================================
# PART 1: What You Already Have (Your RAG System)
# ================================================================
print("\n📦 PART 1: Your Existing RAG System")
print("─"*70)

# This is what you built BEFORE MCP
class SimpleRAG:
    def answer_query(self, question):
        """Your RAG system that queries ChromaDB + Phi-2"""
        # In reality, this:
        # 1. Queries ChromaDB for relevant docs
        # 2. Sends to Phi-2 LLM
        # 3. Calculates confidence
        # 4. Returns result
        return {
            'answer': f"[RAG processed: {question}] The DM8SE has 125W power rating.",
            'confidence': {'overall': 0.92, 'label': 'high'},
            'sources': ['doc1.pdf', 'doc2.pdf'],
            'time': '23.5s'
        }

rag = SimpleRAG()
print("✓ RAG system created")

# ================================================================
# PART 2: MCP Wrapper (What You Added)
# ================================================================
print("\n🎁 PART 2: MCP Wrapper Around Your RAG")
print("─"*70)

class MCPServer:
    def __init__(self, rag_system):
        self.rag = rag_system  # Use existing RAG!
        
    def list_tools(self):
        """Show what tools are available (MCP Discovery)"""
        return {
            "tools": [
                {
                    "name": "query_bose_documentation",
                    "description": "Query Bose Professional Audio docs",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"}
                        },
                        "required": ["question"]
                    }
                }
            ]
        }
    
    def call_tool(self, tool_name, arguments):
        """Execute a tool (MCP Execution)"""
        if tool_name == "query_bose_documentation":
            question = arguments.get("question")
            
            # Call your existing RAG (no changes!)
            result = self.rag.answer_query(question)
            
            # Format as MCP response
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Answer: {result['answer']}\n"
                               f"Confidence: {result['confidence']['overall']*100:.0f}%\n"
                               f"Sources: {', '.join(result['sources'])}\n"
                               f"Time: {result['time']}"
                    }
                ],
                "isError": False
            }
        else:
            return {
                "content": [{"type": "text", "text": "Tool not found"}],
                "isError": True
            }

mcp_server = MCPServer(rag)
print("✓ MCP server created (wrapping RAG)")

# ================================================================
# PART 3: Client (Where You Type Questions)
# ================================================================
print("\n✏️  PART 3: Client (Where YOU Type Questions)")
print("─"*70)

class MCPClient:
    def __init__(self, server):
        self.server = server
    
    def query_documentation(self, question):
        """Easy way to ask questions"""
        return self.server.call_tool(
            "query_bose_documentation",
            {"question": question}
        )

client = MCPClient(mcp_server)
print("✓ Client created")

# ================================================================
# PART 4: Complete Flow
# ================================================================
print("\n🔄 PART 4: Complete Flow")
print("="*70)

# Step 1: Discovery
print("\nStep 1️⃣: Discover Available Tools")
print("─"*70)
tools = mcp_server.list_tools()
print(f"Found {len(tools['tools'])} tool(s):")
for tool in tools['tools']:
    print(f"  • {tool['name']}: {tool['description']}")

# Step 2: Ask a Question (THIS IS WHERE YOU TYPE!)
print("\nStep 2️⃣: Ask a Question")
print("─"*70)
YOUR_QUESTION = "What is the power rating of DM8SE?"  # ← EDIT THIS!
print(f"Question: {YOUR_QUESTION}")

# Step 3: Execute Query
print("\nStep 3️⃣: Execute Query via MCP")
print("─"*70)
print("Client → MCP Server → RAG System → ChromaDB + Phi-2")

response = client.query_documentation(YOUR_QUESTION)

# Step 4: Display Result
print("\nStep 4️⃣: Get Formatted Response")
print("─"*70)
if not response['isError']:
    print("\n✅ SUCCESS!\n")
    print(response['content'][0]['text'])
else:
    print("\n❌ ERROR!")
    print(response['content'][0]['text'])

# ================================================================
# PART 5: What Just Happened?
# ================================================================
print("\n" + "="*70)
print(" WHAT JUST HAPPENED? ".center(70))
print("="*70)

print("""
1. You typed a question (line 98)
   YOUR_QUESTION = "What is the power rating of DM8SE?"

2. Client wrapped it in MCP format:
   {"name": "query_bose_documentation", "arguments": {"question": "..."}}

3. MCP Server received the request

4. MCP Server called your RAG system:
   result = rag.answer_query(question)

5. Your RAG did its magic:
   - Queried ChromaDB for relevant docs
   - Sent to Phi-2 LLM
   - Calculated confidence
   - Returned result

6. MCP Server formatted response:
   {"content": [...], "isError": false}

7. Client extracted and displayed answer

YOUR RAG SYSTEM DIDN'T CHANGE AT ALL!
MCP just wrapped it in a standard protocol.
""")

# ================================================================
# PART 6: In Your Real Project
# ================================================================
print("="*70)
print(" IN YOUR REAL PROJECT ".center(70))
print("="*70)

print("""
This demo showed everything in ONE file for learning.

In your REAL project:

┌────────────────────────────────────────────────────────────┐
│ File: mcp_server.py                                        │
│ - FastAPI app (HTTP server)                                │
│ - GET /mcp/tools → list_tools()                            │
│ - POST /mcp/tools/call → call_tool()                       │
│ - Uses your REAL BoseRAGPhi                                │
│ - Runs on port 8001                                        │
└────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────┐
│ File: my_questions.py (WHERE YOU TYPE!)                    │
│                                                            │
│ MY_QUESTIONS = [                                           │
│     "What is the power of DM8SE?",  ← Edit this!          │
│     "Your question here",                                  │
│ ]                                                          │
│                                                            │
│ for q in MY_QUESTIONS:                                     │
│     response = client.query_documentation(q)               │
│     print(response)                                        │
└────────────────────────────────────────────────────────────┘

TO RUN:
1. Terminal 1: python mcp_server.py
2. Edit: my_questions.py (add questions)
3. Terminal 2: python my_questions.py
4. See answers!
""")

print("="*70)
print(" 🎉 You now understand MCP! ".center(70))
print("="*70)
print("\nNext steps:")
print("  1. Run: python tutorial_mcp_basics.py (5 min)")
print("  2. Run: python learn_mcp_interactive.py (15 min)")
print("  3. Edit: my_questions.py and use it!")
print("\nRead: MCP_LEARNING_GUIDE.md for complete overview")
print("="*70)

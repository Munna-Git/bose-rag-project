"""
🎓 Interactive MCP Learning Script
This script helps you understand MCP by letting you type questions!
"""

import sys
import os
import requests
import json
from typing import Optional

# Colors for Windows terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}\n")

def print_step(number, text):
    print(f"{Colors.BLUE}{Colors.BOLD}Step {number}: {text}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")

class MCPLearningClient:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
    
    def check_server(self):
        """Check if MCP server is running"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def list_tools(self):
        """Get available tools"""
        try:
            response = requests.get(f"{self.base_url}/mcp/tools")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def call_tool(self, tool_name, arguments):
        """Call a tool"""
        try:
            response = requests.post(
                f"{self.base_url}/mcp/tools/call",
                json={
                    "name": tool_name,
                    "arguments": arguments
                }
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def lesson_1_what_is_mcp():
    """Lesson 1: Understanding MCP"""
    print_header("LESSON 1: What is MCP?")
    
    print("""
MCP (Model Context Protocol) is like a MENU SYSTEM for AI tools.

🏪 Imagine a Restaurant:
   - Menu shows what dishes are available
   - You order a dish
   - Kitchen makes it
   - Waiter brings it to you

🤖 MCP for Your RAG:
   - MCP Server shows what tools are available
   - You request a tool (with parameters)
   - RAG system processes it
   - MCP returns structured response

Why is this useful?
✓ Other programs can discover what you offer
✓ Standard way to call your AI
✓ Works from any programming language
✓ No need to know your internal code
    """)
    
    input("Press Enter to continue...")

def lesson_2_discover_tools():
    """Lesson 2: Tool Discovery"""
    print_header("LESSON 2: Discovering Tools")
    
    client = MCPLearningClient()
    
    print_step(1, "Check if MCP server is running")
    if not client.check_server():
        print_error("MCP Server is not running!")
        print_info("Please start it in another terminal:")
        print("   python mcp_server.py")
        return False
    
    print_success("MCP Server is running on port 8001")
    
    print_step(2, "Ask server: What tools are available?")
    print_info("Calling: GET http://localhost:8001/mcp/tools")
    
    tools_response = client.list_tools()
    
    if "error" in tools_response:
        print_error(f"Error: {tools_response['error']}")
        return False
    
    print_success("Received tool list!")
    print("\n📋 Available Tools:")
    
    for tool in tools_response.get('tools', []):
        print(f"\n  🔧 {tool['name']}")
        print(f"     Description: {tool['description']}")
        print(f"     Required inputs: {', '.join(tool['inputSchema']['required'])}")
    
    print("\n💡 This is like reading a restaurant menu!")
    print("   You now know what tools exist and what inputs they need.")
    
    input("\nPress Enter to continue...")
    return True

def lesson_3_call_a_tool():
    """Lesson 3: Calling a Tool"""
    print_header("LESSON 3: Calling a Tool (Your Questions!)")
    
    client = MCPLearningClient()
    
    if not client.check_server():
        print_error("MCP Server is not running!")
        return
    
    print("""
Now let's use the MCP tool to ask questions about Bose equipment!

You'll type a question, and we'll:
1. Format it as an MCP request
2. Send it to the MCP server (port 8001)
3. MCP server calls your RAG system
4. Get back a structured response
    """)
    
    # Example questions
    example_questions = [
        "What is the power rating of DM8SE?",
        "How many channels does the EX-1280 have?",
        "What is the impedance of DM8SE?"
    ]
    
    print("📝 Example questions:")
    for i, q in enumerate(example_questions, 1):
        print(f"   {i}. {q}")
    
    while True:
        print("\n" + "="*70)
        question = input(f"\n{Colors.BOLD}Your question (or 'quit' to exit): {Colors.END}").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        if not question:
            continue
        
        print_step(1, "Formatting as MCP request")
        request_data = {
            "name": "query_bose_documentation",
            "arguments": {
                "question": question
            }
        }
        print(f"   {json.dumps(request_data, indent=2)}")
        
        print_step(2, "Sending to MCP server (port 8001)")
        print_info("POST http://localhost:8001/mcp/tools/call")
        
        response = client.call_tool("query_bose_documentation", {"question": question})
        
        if "error" in response:
            print_error(f"Error: {response['error']}")
            continue
        
        print_step(3, "Received response!")
        
        # Extract and display the answer
        if 'content' in response and len(response['content']) > 0:
            content = response['content'][0]['text']
            
            print(f"\n{Colors.GREEN}{Colors.BOLD}{'─'*70}{Colors.END}")
            print(f"{Colors.GREEN}{Colors.BOLD}ANSWER:{Colors.END}")
            print(f"{Colors.GREEN}{'─'*70}{Colors.END}")
            print(content)
            print(f"{Colors.GREEN}{'─'*70}{Colors.END}\n")
        
        print_info("💡 What just happened:")
        print("   1. You typed a question")
        print("   2. We wrapped it in MCP format")
        print("   3. Sent HTTP request to port 8001")
        print("   4. MCP server called your RAG system")
        print("   5. RAG queried ChromaDB + Phi-2")
        print("   6. MCP returned structured response")
        print("   7. We extracted and displayed the answer")

def lesson_4_other_tools():
    """Lesson 4: Other Available Tools"""
    print_header("LESSON 4: Other MCP Tools")
    
    client = MCPLearningClient()
    
    if not client.check_server():
        print_error("MCP Server is not running!")
        return
    
    print("""
Your MCP server has 3 tools:
1. query_bose_documentation - Ask questions (what we just used!)
2. get_system_metrics - See performance stats
3. clear_cache - Clear the query cache

Let's try the other two!
    """)
    
    input("Press Enter to get system metrics...")
    
    print_step(1, "Getting system metrics")
    response = client.call_tool("get_system_metrics", {})
    
    if "error" not in response and 'content' in response:
        print_success("Metrics retrieved!")
        print(response['content'][0]['text'])
    
    input("\nPress Enter to see cache stats...")
    
    print_step(2, "Checking cache stats")
    print_info("This shows if queries are being cached for speed")
    
    # The metrics include cache info
    print("   (Included in metrics above)")
    
    print("\n💡 All these tools use the SAME MCP protocol:")
    print("   - They're listed in GET /mcp/tools")
    print("   - Called via POST /mcp/tools/call")
    print("   - Return structured responses")

def lesson_5_behind_the_scenes():
    """Lesson 5: What Happens Behind the Scenes"""
    print_header("LESSON 5: Behind the Scenes")
    
    print("""
🔍 When you call an MCP tool, here's the COMPLETE flow:

┌─────────────────────────────────────────────────────────────┐
│ YOU TYPE: "What is the power of DM8SE?"                    │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ mcp_client.py wraps it in MCP format:                      │
│ {                                                           │
│   "name": "query_bose_documentation",                      │
│   "arguments": {"question": "What is the power of DM8SE?"} │
│ }                                                           │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ HTTP POST to http://localhost:8001/mcp/tools/call          │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ mcp_server.py receives request                             │
│ - Checks tool name: "query_bose_documentation"             │
│ - Routes to: handle_query_tool()                           │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ handle_query_tool() calls your existing RAG:               │
│   result = rag.answer_query(question)                      │
│                                                             │
│ Your RAG (rag_phi.py) - NO CHANGES:                        │
│   1. Check cache                                            │
│   2. Query ChromaDB for relevant docs                       │
│   3. Send to Phi-2 LLM                                      │
│   4. Calculate confidence score                             │
│   5. Return result                                          │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ handle_query_tool() formats as MCP response:               │
│ {                                                           │
│   "content": [                                              │
│     {"type": "text", "text": "DM8SE has 125W power..."}   │
│   ],                                                        │
│   "isError": false                                          │
│ }                                                           │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ HTTP response back to mcp_client.py                        │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ mcp_client.py extracts answer and displays to YOU          │
└─────────────────────────────────────────────────────────────┘

KEY POINTS:
✓ Your RAG system is UNCHANGED
✓ MCP is just a WRAPPER around it
✓ MCP uses HTTP (works from any language)
✓ Standard protocol (other AIs can discover and use it)
✓ Runs on separate port (8001) from main app (8000)
    """)
    
    input("Press Enter to continue...")

def lesson_6_summary():
    """Lesson 6: Summary and Next Steps"""
    print_header("LESSON 6: Summary & Where to Write Queries")
    
    print("""
🎓 WHAT YOU LEARNED:

1. MCP = Standard way to expose AI tools
2. Server = Wrapper around your RAG (port 8001)
3. Client = Where you type questions
4. Protocol = Discover tools → Call tools → Get responses
5. Your RAG = Unchanged, just wrapped

📝 WHERE TO WRITE YOUR QUERIES:

Option 1: Modify mcp_client.py (Line 120+)
─────────────────────────────────────────
from mcp_client import MCPClient

client = MCPClient("http://localhost:8001")

# Type your questions here!
questions = [
    "What is the power of DM8SE?",
    "How to install DM6PE?",
    "What is the impedance?"
]

for q in questions:
    response = client.query_documentation(q)
    print(response)

Option 2: Create your own script (my_queries.py)
────────────────────────────────────────────────
import requests

response = requests.post(
    "http://localhost:8001/mcp/tools/call",
    json={
        "name": "query_bose_documentation",
        "arguments": {
            "question": "YOUR QUESTION HERE"
        }
    }
)

print(response.json())

Option 3: Use this interactive script!
──────────────────────────────────────
python learn_mcp_interactive.py
(You're using it right now!)

🚀 TO RUN MCP:

Terminal 1:              Terminal 2:
python mcp_server.py     python mcp_client.py
(Runs on port 8001)      (Type questions here)

OR

test_mcp.bat (runs both automatically)

📚 MORE DOCUMENTATION:

- MCP_VISUAL_GUIDE.md    - Diagrams and visuals
- MCP_README.md          - Complete technical docs
- MCP_QUICKSTART.md      - 5-minute quick start
- tutorial_mcp_basics.py - Core concepts code
    """)

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║            🎓 INTERACTIVE MCP LEARNING TUTORIAL 🎓                   ║
║                                                                      ║
║              Learn Model Context Protocol Step by Step              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    print("\nThis tutorial will help you understand MCP through:")
    print("  1. Simple explanations")
    print("  2. Live demonstrations")
    print("  3. Hands-on practice")
    
    input("\nPress Enter to start...")
    
    # Run lessons
    lesson_1_what_is_mcp()
    
    if lesson_2_discover_tools():
        lesson_3_call_a_tool()
    
    lesson_4_other_tools()
    lesson_5_behind_the_scenes()
    lesson_6_summary()
    
    print_header("🎉 Tutorial Complete!")
    print(f"\n{Colors.GREEN}{Colors.BOLD}You now understand MCP!{Colors.END}\n")
    print("Next steps:")
    print("  1. Modify mcp_client.py with your questions")
    print("  2. Create your own query scripts")
    print("  3. Read MCP_VISUAL_GUIDE.md for reference")
    print("\n")

if __name__ == "__main__":
    main()

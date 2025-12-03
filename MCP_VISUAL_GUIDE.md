# 🎨 MCP Visual Guide - Where Everything Lives

## 📁 File Structure

```
bose-rag-project/
│
├── 🏠 YOUR EXISTING SYSTEM (No Changes!)
│   ├── src/
│   │   └── interfaces/
│   │       └── rag_phi.py          ← Your RAG system (works as before)
│   ├── app.py                      ← Your main web app (port 8000)
│   └── data/vector_db/             ← Your ChromaDB
│
└── 🆕 NEW MCP LAYER (Wrapper Only!)
    ├── mcp_server.py               ← MCP Server (port 8001)
    ├── mcp_client.py               ← Test client (you type here!)
    └── test_mcp.bat                ← Easy launcher
```

## 🔄 How Data Flows

### Scenario 1: Using Main App (Before MCP)
```
You → http://localhost:8000 → app.py → BoseRAGPhi → ChromaDB → Phi-2
                                            ↓
                                        Answer
```

### Scenario 2: Using MCP (New Way)
```
You → mcp_client.py → HTTP → mcp_server.py → BoseRAGPhi → ChromaDB → Phi-2
      (Type here!)    8001    (Wrapper)       (Same RAG!)
                                                  ↓
                              ← JSON Response ← Answer
```

## 🎯 Where Do You Write Queries?

### Option 1: MCP Client (Python Script)
```python
# In mcp_client.py or your own script:

from mcp_client import MCPClient

client = MCPClient("http://localhost:8001")

# THIS IS WHERE YOU TYPE YOUR QUESTION! 👇
response = client.query_documentation("What is the power of DM8SE?")

print(response)
```

### Option 2: Command Line (curl)
```bash
# In PowerShell:

# Discover tools
Invoke-RestMethod -Uri "http://localhost:8001/mcp/tools" -Method Get

# Ask a question
$body = @{
    name = "query_bose_documentation"
    arguments = @{
        question = "What is the power of DM8SE?"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/mcp/tools/call" -Method Post -Body $body -ContentType "application/json"
```

### Option 3: Another Python Program
```python
import requests

# Discover available tools
tools = requests.get("http://localhost:8001/mcp/tools").json()
print("Available tools:", tools)

# Call a tool
response = requests.post(
    "http://localhost:8001/mcp/tools/call",
    json={
        "name": "query_bose_documentation",
        "arguments": {
            "question": "What is the impedance of DM8SE?"  # YOUR QUESTION
        }
    }
)

result = response.json()
print("Answer:", result['content'][0]['text'])
```

## 📊 Component Breakdown

### mcp_server.py (The Restaurant)
```python
# What it does:
# 1. Creates a "front desk" for your RAG system
# 2. Lists available tools (menu)
# 3. Routes requests to your RAG
# 4. Returns formatted responses

from fastapi import FastAPI
from src.interfaces.rag_phi import BoseRAGPhi

mcp_app = FastAPI()
rag = BoseRAGPhi()  # ← Your existing RAG!

@mcp_app.get("/mcp/tools")
def list_tools():
    """Show what tools are available"""
    return {"tools": [...]}

@mcp_app.post("/mcp/tools/call")
def call_tool(request):
    """Execute a tool"""
    if request.name == "query_bose_documentation":
        answer = rag.answer_query(request.arguments["question"])
        return {"content": [{"type": "text", "text": answer}]}
```

### mcp_client.py (Your Interface)
```python
# What it does:
# 1. Connects to MCP server
# 2. Provides easy-to-use functions
# 3. Formats output nicely

class MCPClient:
    def query_documentation(self, question):
        """Easy way to ask questions!"""
        response = requests.post(
            f"{self.base_url}/mcp/tools/call",
            json={
                "name": "query_bose_documentation",
                "arguments": {"question": question}
            }
        )
        return response.json()

# USAGE (where you type!):
client = MCPClient("http://localhost:8001")
result = client.query_documentation("Your question here")
```

## 🚀 Step-by-Step Usage

### Step 1: Start MCP Server
```powershell
# Terminal 1
python mcp_server.py

# You'll see:
# INFO: MCP Server starting on port 8001
# INFO: Application startup complete
```

### Step 2: Use the Client
```powershell
# Terminal 2
python mcp_client.py

# The script runs 6 tests automatically:
# Test 1: Server connection ✓
# Test 2: List tools ✓
# Test 3: Query documentation ✓
# Test 4: Get metrics ✓
# Test 5: Cache test ✓
# Test 6: Clear cache ✓
```

### Step 3: Modify Client for Your Questions
```python
# Edit mcp_client.py at the bottom:

if __name__ == "__main__":
    client = MCPClient("http://localhost:8001")
    
    # Your custom questions!
    questions = [
        "What is the power of DM8SE?",
        "How many channels does EX-1280 have?",
        "What is the coverage pattern of DM6PE?"
    ]
    
    for q in questions:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        print('='*60)
        response = client.query_documentation(q)
        print_response(response)
```

## 🎓 Why MCP is Useful

### Before MCP:
- Other programs need to import your Python code
- Hard to use from other languages (JavaScript, Java, etc.)
- Changes to your RAG require updating all clients

### With MCP:
- **Language Independent**: Use from any language via HTTP
- **Standardized**: Other AI systems know how to talk to you
- **Discoverable**: Tools are listed, no guessing
- **Versioned**: Change implementation without breaking clients
- **Shareable**: Anyone can use your RAG over the network

## 🔍 What Each File Does

| File | Purpose | You Type Here? |
|------|---------|----------------|
| `mcp_server.py` | Runs the MCP server (port 8001) | ❌ No |
| `mcp_client.py` | Test client with examples | ✅ Yes - modify bottom |
| `test_mcp.bat` | Automated test launcher | ❌ No |
| `src/interfaces/rag_phi.py` | Your RAG system | ❌ No changes needed |
| `app.py` | Main web app (port 8000) | ❌ No |

## 📝 Quick Reference

### Where Do I Type My Questions?

**Easiest:** Modify `mcp_client.py` at the bottom (line 120+):
```python
# Line 120 in mcp_client.py
client = MCPClient("http://localhost:8001")
response = client.query_documentation("YOUR QUESTION HERE")  # ← Type here!
print_response(response)
```

**Or create a new file:**
```python
# my_queries.py
from mcp_client import MCPClient

client = MCPClient("http://localhost:8001")

# Type all your questions here!
questions = [
    "What is DM8SE power rating?",
    "How to install DM6PE?"
]

for q in questions:
    response = client.query_documentation(q)
    print(response)
```

### How to Run

**Option 1:** Two terminals
```powershell
# Terminal 1
python mcp_server.py

# Terminal 2
python mcp_client.py
```

**Option 2:** Automated
```powershell
test_mcp.bat
```

**Option 3:** Your own script
```powershell
# Start server first
python mcp_server.py

# In another terminal
python my_queries.py
```

## 🎯 Key Takeaways

1. **MCP is a wrapper** - Your RAG system doesn't change
2. **Server = Restaurant** - Exposes tools via HTTP
3. **Client = Customer** - Calls tools, gets responses
4. **You type in client** - Either mcp_client.py or your own script
5. **Port 8001** - MCP server runs here (port 8000 is main app)
6. **Standard protocol** - Other AI systems can discover and use your tools

---

**Next:** Run `python tutorial_mcp_basics.py` to understand core concepts!

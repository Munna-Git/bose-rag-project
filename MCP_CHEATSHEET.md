# 🚀 MCP Quick Start Cheat Sheet

## ⚡ Super Quick Start (30 seconds)

```powershell
# Terminal 1 - Start server
python mcp_server.py

# Terminal 2 - Edit questions and run
# Edit: my_questions.py (line 16)
python my_questions.py
```

## 📋 What is MCP? (10 second answer)

**MCP = A standard way for other programs to discover and use your AI tools**

Your RAG system → MCP wraps it → Other programs can use it via HTTP

## 🎯 Where Do I Type Questions?

### Option 1: Easiest (Recommended) ⭐
```python
# File: my_questions.py
# Edit line 16:

MY_QUESTIONS = [
    "What is the power of DM8SE?",
    "Your question here",  # ← Add more
]

# Run: python my_questions.py
```

### Option 2: Interactive Tutorial
```powershell
python learn_mcp_interactive.py
# Type questions when prompted
```

### Option 3: Modify Test Client
```python
# File: mcp_client.py (line 120+)

if __name__ == "__main__":
    client = MCPClient("http://localhost:8001")
    
    # Add your questions here:
    response = client.query_documentation("Your question")
    print(response)
```

### Option 4: Command Line
```powershell
# PowerShell
$body = @{
    name = "query_bose_documentation"
    arguments = @{question = "What is DM8SE power?"}
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/mcp/tools/call" `
    -Method Post -Body $body -ContentType "application/json"
```

## 🏗️ How It Works (Visual)

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   You Type  │  →    │ MCP Server  │  →    │  Your RAG   │
│  Question   │       │  (Port 8001)│       │   System    │
└─────────────┘       └─────────────┘       └─────────────┘
                             ↓
                      ┌─────────────┐
                      │   Answer    │
                      │  (Formatted)│
                      └─────────────┘
```

## 📁 File Guide

| File | What It Does | Do You Edit? |
|------|--------------|--------------|
| `mcp_server.py` | Runs MCP server on port 8001 | ❌ No - just run it |
| `my_questions.py` | **YOUR QUESTIONS GO HERE** | ✅ **YES!** Line 16 |
| `mcp_client.py` | Test client with examples | Optional |
| `learn_mcp_interactive.py` | Interactive tutorial | ❌ No - just run it |
| `rag_phi.py` | Your RAG system (unchanged) | ❌ No |

## 🔧 3 Available Tools

1. **query_bose_documentation** - Ask questions about Bose products
2. **get_system_metrics** - See performance stats (cache hits, timing)
3. **clear_cache** - Clear the query cache

## 📊 Complete Flow Example

```python
# 1. You add question to my_questions.py
MY_QUESTIONS = ["What is DM8SE power?"]

# 2. Run: python my_questions.py

# 3. Behind the scenes:
#    - Wraps as: {"name": "query_bose_documentation", "arguments": {"question": "..."}}
#    - HTTP POST → localhost:8001/mcp/tools/call
#    - mcp_server.py receives request
#    - Calls: rag.answer_query(question)
#    - Your RAG queries ChromaDB + Phi-2
#    - Returns answer with confidence
#    - Formatted and displayed

# 4. You see answer!
```

## 🎓 Learning Path

1. **Understand basics** (5 min):
   ```
   python tutorial_mcp_basics.py
   ```

2. **See it with your RAG** (5 min):
   ```
   python tutorial_mcp_with_rag.py
   ```

3. **Interactive practice** (10 min):
   ```
   Terminal 1: python mcp_server.py
   Terminal 2: python learn_mcp_interactive.py
   ```

4. **Use it yourself** (∞):
   ```
   Edit: my_questions.py
   Run: python my_questions.py
   ```

## ⚠️ Common Issues

### "Connection refused"
```
Problem: MCP server not running
Solution: python mcp_server.py (in another terminal)
```

### "Port 8001 already in use"
```
Problem: Server already running
Solution: Close other terminal or restart
```

### "Module not found"
```
Problem: Not in project directory
Solution: cd d:\bose-rag-project
```

## 🎯 Quick Test

```powershell
# Terminal 1
python mcp_server.py
# Wait for: "MCP Server ready on port 8001"

# Terminal 2
python my_questions.py
# Should show 3 example answers
```

## 📚 Documentation Files

- **START HERE**: `MCP_VISUAL_GUIDE.md` - Visual explanations
- **LEARN**: `learn_mcp_interactive.py` - Hands-on tutorial
- **REFERENCE**: `MCP_README.md` - Complete technical docs
- **QUICK DEMO**: `MCP_QUICKSTART.md` - 5-minute demo
- **BASICS**: `tutorial_mcp_basics.py` - Core concepts

## 💡 Key Concepts

### MCP is NOT:
- ❌ A replacement for your RAG
- ❌ A new database
- ❌ A complicated system

### MCP IS:
- ✅ A wrapper around your RAG
- ✅ A standard protocol (HTTP + JSON)
- ✅ A way for others to use your tools

## 🎬 Interview Demo Script

```
1. Terminal 1: python mcp_server.py
   "MCP server exposes our RAG as discoverable tools"

2. Terminal 2: python my_questions.py
   "Here's how external programs query our system"

3. Show response with answer, confidence, sources
   "Notice structured response - other AIs can parse this"

4. Mention: "This follows MCP standard protocol"
   "Any MCP-compatible system can discover and use our tools"
```

## 🔑 One-Sentence Summary

**MCP wraps your RAG system in a standard protocol so other programs can discover and use it via HTTP.**

---

**Next Step:** Run `python tutorial_mcp_basics.py` to understand the concepts!

**To Use:** Edit `my_questions.py` (line 16) and run it!

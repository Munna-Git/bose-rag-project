"""
TUTORIAL 1: Understanding MCP Basics
Let's build the simplest possible MCP system step by step
"""

# ============================================================
# STEP 1: What is a "Tool"?
# ============================================================
# A tool is just a function that can be called remotely
# Think of it like a remote-controlled robot

def my_simple_tool(name: str) -> str:
    """This is a tool - just a function that does something"""
    return f"Hello, {name}! I'm a tool."

# Test it locally (no MCP yet)
print("STEP 1: Local Function")
print(my_simple_tool("Alice"))
print()

# ============================================================
# STEP 2: Describing a Tool (MCP Format)
# ============================================================
# MCP needs to know: What does this tool do? What inputs does it need?

tool_description = {
    "name": "my_simple_tool",
    "description": "Greets a person by name",
    "inputSchema": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The person's name"
            }
        },
        "required": ["name"]
    }
}

print("STEP 2: Tool Description (MCP Format)")
import json
print(json.dumps(tool_description, indent=2))
print()

# ============================================================
# STEP 3: Tool Discovery
# ============================================================
# When someone asks "What tools do you have?", we return a list

def list_tools():
    """This is like showing a menu at a restaurant"""
    return {
        "tools": [tool_description]
    }

print("STEP 3: Tool Discovery")
print("Question: What tools are available?")
print("Answer:", json.dumps(list_tools(), indent=2))
print()

# ============================================================
# STEP 4: Tool Execution
# ============================================================
# When someone says "Run this tool with these arguments"

def call_tool(tool_name: str, arguments: dict):
    """This is like placing an order at a restaurant"""
    if tool_name == "my_simple_tool":
        name = arguments.get("name", "Unknown")
        result = my_simple_tool(name)
        
        # Return in MCP format
        return {
            "content": [
                {"type": "text", "text": result}
            ],
            "isError": False
        }
    else:
        return {
            "content": [
                {"type": "text", "text": f"Tool '{tool_name}' not found"}
            ],
            "isError": True
        }

print("STEP 4: Tool Execution")
print("Request: Call 'my_simple_tool' with name='Bob'")
response = call_tool("my_simple_tool", {"name": "Bob"})
print("Response:", json.dumps(response, indent=2))
print()

# ============================================================
# STEP 5: Full MCP Flow
# ============================================================
print("=" * 60)
print("STEP 5: Complete MCP Flow")
print("=" * 60)

# A client would do this:
print("\n1. CLIENT: What tools are available?")
tools = list_tools()
print(f"   SERVER: Here are {len(tools['tools'])} tool(s)")
for tool in tools['tools']:
    print(f"   - {tool['name']}: {tool['description']}")

print("\n2. CLIENT: Call 'my_simple_tool' with name='Charlie'")
response = call_tool("my_simple_tool", {"name": "Charlie"})
print(f"   SERVER: {response['content'][0]['text']}")

print("\n" + "=" * 60)
print("That's MCP! It's just:")
print("  1. Describe what you can do (tools)")
print("  2. Let others discover your tools")
print("  3. Let others call your tools")
print("  4. Return structured responses")
print("=" * 60)

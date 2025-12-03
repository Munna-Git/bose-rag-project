"""
MCP (Model Context Protocol) Client
Simple client to test MCP server communication
"""
import requests
import json
from typing import Dict, Any


class MCPClient:
    """Simple MCP client for testing"""
    
    def __init__(self, server_url: str = "http://localhost:8001"):
        self.server_url = server_url
        self.session = requests.Session()
    
    def get_server_info(self) -> Dict:
        """Get MCP server information"""
        response = self.session.get(f"{self.server_url}/")
        response.raise_for_status()
        return response.json()
    
    def list_tools(self) -> Dict:
        """List available MCP tools"""
        response = self.session.get(f"{self.server_url}/mcp/tools")
        response.raise_for_status()
        return response.json()
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict:
        """Call an MCP tool"""
        payload = {
            "name": tool_name,
            "arguments": arguments
        }
        response = self.session.post(
            f"{self.server_url}/mcp/tools/call",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def query_documentation(self, question: str, verbose: bool = False) -> Dict:
        """Query Bose documentation (convenience method)"""
        return self.call_tool(
            "query_bose_documentation",
            {"question": question, "verbose": verbose}
        )
    
    def get_metrics(self) -> Dict:
        """Get system metrics (convenience method)"""
        return self.call_tool("get_system_metrics", {})
    
    def clear_cache(self) -> Dict:
        """Clear query cache (convenience method)"""
        return self.call_tool("clear_cache", {})


def print_response(response: Dict):
    """Pretty print MCP response"""
    print("\n" + "=" * 70)
    if response.get('isError'):
        print("❌ ERROR")
    else:
        print("✅ SUCCESS")
    print("=" * 70)
    
    for content_item in response.get('content', []):
        if content_item.get('type') == 'text':
            print(content_item.get('text', ''))
    print("=" * 70)


def main():
    """Test MCP client"""
    print("\n" + "=" * 70)
    print("MCP CLIENT - Testing Bose RAG MCP Server")
    print("=" * 70)
    
    # Initialize client
    client = MCPClient("http://localhost:8001")
    
    try:
        # Test 1: Get server info
        print("\n📡 TEST 1: Get Server Info")
        print("-" * 70)
        server_info = client.get_server_info()
        print(json.dumps(server_info, indent=2))
        
        # Test 2: List available tools
        print("\n🔧 TEST 2: List Available Tools")
        print("-" * 70)
        tools = client.list_tools()
        print(f"Available tools: {len(tools['tools'])}")
        for tool in tools['tools']:
            print(f"\n  • {tool['name']}")
            print(f"    {tool['description']}")
        
        # Test 3: Query documentation
        print("\n❓ TEST 3: Query Documentation")
        print("-" * 70)
        question = "What is the power rating of DesignMax DM8SE?"
        print(f"Question: {question}")
        
        response = client.query_documentation(question, verbose=False)
        print_response(response)
        
        # Test 4: Get system metrics
        print("\n📊 TEST 4: Get System Metrics")
        print("-" * 70)
        response = client.get_metrics()
        print_response(response)
        
        # Test 5: Test with another query
        print("\n❓ TEST 5: Another Query (should be cached)")
        print("-" * 70)
        question = "What is the power rating of DesignMax DM8SE?"
        print(f"Question: {question} (repeated)")
        
        response = client.query_documentation(question)
        print_response(response)
        
        # Test 6: Clear cache
        print("\n🗑️  TEST 6: Clear Cache")
        print("-" * 70)
        response = client.clear_cache()
        print_response(response)
        
        print("\n✅ All MCP tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to MCP server")
        print("Make sure the server is running:")
        print("  python mcp_server.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    main()

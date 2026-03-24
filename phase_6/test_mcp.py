import asyncio
import json
from phase_6.src.tools.mcp_manager import mcp_mgr

async def test_mcp():
    print("🚀 Starting MCP Diagnostic Test...")
    
    # Test 1: DuckDuckGo Search
    print("\n🔍 Testing DuckDuckGo MCP Search...")
    search_results = await mcp_mgr.call_duckduckgo_search("Reliance Industries latest news")
    if search_results:
        print("✅ DuckDuckGo MCP returned data!")
        # print(json.dumps(search_results[:1], indent=2))
    else:
        print("❌ DuckDuckGo MCP failed or returned no data.")

    # Test 2: Sequential Thinking
    print("\n🧠 Testing Sequential Thinking MCP...")
    thought_results = await mcp_mgr.call_sequential_thinking(
        thought="I am testing the connection between the Market Analyst agent and the thinking server.",
        context="Test environment"
    )
    if thought_results:
        print("✅ Sequential Thinking MCP returned data!")
    else:
        print("❌ Sequential Thinking MCP failed.")

if __name__ == "__main__":
    asyncio.run(test_mcp())

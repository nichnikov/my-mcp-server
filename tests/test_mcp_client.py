import asyncio
import sys
import os
import logging
import httpx

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.client.sse import sse_client
from mcp import ClientSession

async def test_search_gateway_direct(query: str):
    print(f"\n--- [STEP 1] Testing Search Gateway Direct (http://localhost:8002) ---")
    url = "http://localhost:8002/search/projects"
    payload = {
        "query": query,
        "limit": 3,
        "alpha": 0.5
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print(f"Sending POST to {url} with payload: {payload}")
            response = await client.post(url, json=payload, timeout=5.0)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                print("Response JSON snippet:", str(response.json())[:200] + "...")
                print("✅ Gateway is working!")
            else:
                print(f"❌ Gateway returned error: {response.text}")
        except Exception as e:
            print(f"❌ Error connecting to Gateway: {e}")

async def run_test():
    query = "строительные материалы"
    
    # Step 1: Direct Gateway Test
    await test_search_gateway_direct(query)

    # Step 2: MCP Server Test
    print(f"\n--- [STEP 2] Testing MCP Server via SSE (http://localhost:8000/sse) ---")
    print("Connecting to MCP SSE server...")
    
    async with sse_client("http://localhost:8000/sse") as (read, write):
        await asyncio.sleep(0.5)
        
        async with ClientSession(read, write) as session:
            print("Connected! Initializing session...")
            await session.initialize()
            
            print("\n--- Listing Tools ---")
            tools = await session.list_tools()
            print("названия инструметнов (tools):", tools)
            for tool in tools.tools:
                print(f"Tool: {tool.name}")
                # print(f"Description: {tool.description}")
            
            print(f"\n--- Calling Tool 'search_projects' with query='{query}' ---")
            
            # Note: In a real scenario, we might need to handle timeouts or errors
            # Adding read_timeout to ensure we don't wait forever if server hangs
            try:
                result = await asyncio.wait_for(
                    session.call_tool("search_projects", arguments={"query": query}),
                    timeout=10.0
                )
                
                print("Result:")
                for content in result.content:
                    if content.type == "text":
                        print(content.text)
                    else:
                        print(f"[{content.type}] {content}")
            except asyncio.TimeoutError:
                print("❌ Timeout waiting for tool execution result")
            except Exception as e:
                print(f"❌ Error calling tool: {e}")


if __name__ == "__main__":
    asyncio.run(run_test())

import asyncio
import sys
import os
import logging

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.client.sse import sse_client
from mcp import ClientSession

async def list_tools_only():
    print("Connecting to MCP SSE server at http://localhost:8000/sse...")
    
    try:
        async with sse_client("http://localhost:8000/sse") as (read, write):
            # Small delay for connection stability
            await asyncio.sleep(0.5)
            
            async with ClientSession(read, write) as session:
                print("Connected! Initializing session...")
                await session.initialize()
                
                print("\n--- Requesting Tools List ---")
                tools = await session.list_tools()
                
                print(f"\nFound {len(tools.tools)} tools:")
                for tool in tools.tools:
                    print(f"- Name: {tool.name}")
                    print(f"  Description: {tool.description}")
                    print(f"  Schema: {tool.inputSchema}")
                    print("-" * 30)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(list_tools_only())

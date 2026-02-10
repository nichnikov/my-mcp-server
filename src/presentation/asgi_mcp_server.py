import uvicorn
import logging
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route, Mount

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_asgi_server")

# Initialize MCP Server
server = Server("ASGI Stub Server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    logger.info("Client requested tool list")
    return [
        Tool(
            name="asgi_tool_1",
            description="Tool from ASGI server",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    logger.info(f"Client called tool: {name}")
    return [TextContent(type="text", text=f"Executed {name}")]

# SSE Transport Setup
sse = SseServerTransport("/sse/messages")

async def handle_sse(scope, receive, send):
    """
    Pure ASGI endpoint for SSE connection.
    Does not use Starlette Request/Response objects directly to avoid confusing Starlette's routing.
    """
    logger.info("New SSE connection established")
    try:
        async with sse.connect_sse(scope, receive, send) as streams:# sse.connect_sse(scope, receive, send) as streams:
            logger.info("SSE streams created, running server loop")
            # streams[0] is read stream, streams[1] is write stream
            await server.run(streams[0], streams[1], server.create_initialization_options())
    except Exception as e:
        logger.error(f"SSE connection error: {e}")
    finally:
        logger.info("SSE connection closed")

# Starlette App
starlette_app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        # Mount("/sse/messages", app=sse.handle_post_message),
        Mount("/sse", app=handle_sse),
    ],
)

if __name__ == "__main__":
    uvicorn.run(starlette_app, host="0.0.0.0", port=8000)

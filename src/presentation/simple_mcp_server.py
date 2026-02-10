import uvicorn
import sys
import os
import logging
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_simple_server")

# Initialize MCP Server
server = Server("Simple Stub Server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    logger.info("Client requested tool list")
    return [
        Tool(
            name="stub_tool_1",
            description="This is a test tool to verify list_tools works",
            inputSchema={"type": "object", "properties": {"arg": {"type": "string"}}}
        ),
        Tool(
            name="stub_tool_2",
            description="Another test tool",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    logger.info(f"Client called tool: {name}")
    return [TextContent(type="text", text=f"Executed {name}")]

# SSE Transport Setup
# Важно: указываем полный путь, куда клиент должен слать POST запросы
sse = SseServerTransport("/sse/messages")

async def handle_sse(request: Request):
    logger.info("New SSE connection attempt")
    try:
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            logger.info("SSE connection established, starting server loop")
            await server.run(streams[0], streams[1], server.create_initialization_options())
    except Exception as e:
        logger.error(f"SSE connection error: {e}")
    finally:
        logger.info("SSE connection closed")
    
    # Return a dummy response to satisfy Starlette
    from starlette.responses import Response
    return Response(status_code=200)

async def handle_messages(request: Request):
    logger.info("Received POST message")
    await sse.handle_post_message(request.scope, request.receive, request._send)
    logger.info("Processed POST message")

# Starlette App
# Используем Route вместо Mount для более явного контроля
starlette_app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/sse/messages", app=sse.handle_post_message),
    ],
)

if __name__ == "__main__":
    uvicorn.run(starlette_app, host="0.0.0.0", port=8000)

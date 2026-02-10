import uvicorn
import sys
import os
import logging
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent, EmbeddedResource, ImageContent
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.container import container

# Initialize MCP Server
server = Server("Weaviate Knowledge Base")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_projects",
            description="Поиск реализованных проектов и кейсов в портфолио компании. Используй это, когда пользователь спрашивает 'покажите примеры', 'есть ли опыт с...', 'делали ли вы сайты для...'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Поисковый запрос, описывающий тематику или тип проекта (например: 'интернет-магазин одежды', 'медицинский центр')."
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_prices",
            description="Поиск стоимости услуг и работ в прайс-листе. Используй этот инструмент для ответов на вопросы о бюджете, тарифах и ценах.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Название услуги (например: 'хостинг', 'разработка дизайна', 'интеграция с 1С')."
                    }
                },
                "required": ["query"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent | ImageContent | EmbeddedResource]:
    logger.info(f"Handling tool call: {name} with args: {arguments}")
    if not arguments:
        arguments = {}

    query = arguments.get("query", "")

    try:
        if name == "search_projects":
            # Now awaiting the async use case
            logger.info("Calling search_projects use case...")
            projects = await container.search_use_case.search_projects(query)
            logger.info(f"Got {len(projects) if projects else 0} projects")
            
            if not projects:
                return [TextContent(type="text", text="No projects found.")]
            
            result = f"Projects found for '{query}':\n\n"
            for p in projects:
                result += f"- PROJECT: {p.title}\n"
                if p.url:
                    result += f"  URL: {p.url}\n"
                result += f"  INFO: {p.description}\n\n"
            return [TextContent(type="text", text=result)]
        
        elif name == "search_prices":
            # Now awaiting the async use case
            logger.info("Calling search_services use case...")
            services = await container.search_use_case.search_services(query)
            logger.info(f"Got {len(services) if services else 0} services")

            if not services:
                return [TextContent(type="text", text="No services found.")]

            result = f"Services found for '{query}':\n\n"
            for s in services:
                result += f"- SERVICE: {s.name}\n  PRICE: {s.price} RUB\n"
                if s.description:
                    result += f"  NOTE: {s.description}\n"
                result += "\n"
            return [TextContent(type="text", text=result)]
        
        else:
            logger.error(f"Unknown tool: {name}")
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error executing tool: {e}")]

from starlette.requests import Request

# SSE Transport Setup
sse = SseServerTransport("/sse/messages")

async def handle_sse(request: Request):
    logger.info("New SSE connection established")
    try:
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            logger.info("SSE streams created, running server")
            await server.run(streams[0], streams[1], server.create_initialization_options())
    except Exception as e:
        logger.error(f"SSE connection error: {e}")
    finally:
        logger.info("SSE connection closed")

starlette_app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/sse/messages", app=sse.handle_post_message),
    ],
)

if __name__ == "__main__":
    uvicorn.run(starlette_app, host="0.0.0.0", port=8000)

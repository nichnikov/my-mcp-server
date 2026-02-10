import os
import sys
import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent, EmbeddedResource, ImageContent
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request


# Добавляем путь к инструментам
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agent_tools import KnowledgeBaseTool

# Инициализация инструментов
try:
    kb_tool = KnowledgeBaseTool()
    print("KnowledgeBaseTool initialized for SSE server")
except Exception as e:
    print(f"Error initializing tools: {e}")
    kb_tool = None

# Инициализация MCP сервера
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
    if not kb_tool:
        return [TextContent(type="text", text="Ошибка: Подключение к базе знаний не установлено.")]
    
    if not arguments:
        arguments = {}

    query = arguments.get("query", "")

    if name == "search_projects":
        result = kb_tool.search_projects(query)
        return [TextContent(type="text", text=result)]
    
    elif name == "search_prices":
        result = kb_tool.search_prices(query)
        return [TextContent(type="text", text=result)]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

# Настройка SSE транспорта с Starlette
sse = SseServerTransport("/messages")

async def handle_sse(scope, receive, send):
    async with sse.connect_sse(scope, receive, send) as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())

async def handle_messages(scope, receive, send):
    await sse.handle_post_message(scope, receive, send)

starlette_app = Starlette(
    debug=True,
    routes=[
        Mount("/sse", app=handle_sse),
        Mount("/messages", app=handle_messages),
    ],
)

if __name__ == "__main__":
    # Запуск сервера на порту 8000
    uvicorn.run(starlette_app, host="0.0.0.0", port=8000)

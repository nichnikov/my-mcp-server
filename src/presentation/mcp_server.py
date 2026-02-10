from mcp.server.fastmcp import FastMCP
import sys
import os
import asyncio

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.container import container

# Initialize MCP Server
mcp = FastMCP("Weaviate Knowledge Base")

@mcp.tool()
async def search_projects(query: str) -> str:
    """
    Поиск реализованных проектов и кейсов в портфолио. 
    Используй этот инструмент, когда пользователь спрашивает:
    - "Покажи примеры работ по..."
    - "Есть ли у вас опыт с..."
    - "Делали ли вы сайты для..."
    
    Args:
        query: Тематика или тип проекта (например: "интернет-магазин одежды", "медицинский центр").
    """
    projects = await container.search_use_case.search_projects(query)
    
    if not projects:
        return "No projects found."

    result = f"Projects found for '{query}':\n\n"
    for p in projects:
        result += f"- PROJECT: {p.title}\n"
        if p.url:
            result += f"  URL: {p.url}\n"
        result += f"  INFO: {p.description}\n\n"
    
    return result

@mcp.tool()
async def search_prices(query: str) -> str:
    """
    Поиск стоимости услуг и работ в прайс-листе.
    Используй этот инструмент для ответов на вопросы о бюджете, тарифах и ценах.
    
    Args:
        query: Название услуги (например: "хостинг", "разработка дизайна", "интеграция с 1С").
    """
    services = await container.search_use_case.search_services(query)

    if not services:
        return "No services found."

    result = f"Services found for '{query}':\n\n"
    for s in services:
        result += f"- SERVICE: {s.name}\n  PRICE: {s.price} RUB\n"
        if s.description:
            result += f"  NOTE: {s.description}\n"
        result += "\n"
        
    return result

if __name__ == "__main__":
    mcp.run()

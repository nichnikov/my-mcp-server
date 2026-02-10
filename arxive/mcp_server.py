from mcp.server.fastmcp import FastMCP
import os
import sys

# Добавляем текущую директорию в путь, чтобы импортировать соседние модули
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_tools import KnowledgeBaseTool

# Инициализируем MCP сервер
mcp = FastMCP("Weaviate Knowledge Base")

# Инициализируем наш инструмент работы с БД
# Он подключится к localhost:8080 (Weaviate) и localhost:9090 (Transformers)
try:
    kb_tool = KnowledgeBaseTool()
    print("KnowledgeBaseTool successfully initialized", file=sys.stderr)
except Exception as e:
    print(f"Error initializing KnowledgeBaseTool: {e}", file=sys.stderr)
    kb_tool = None

@mcp.tool()
def search_projects(query: str) -> str:
    """
    Поиск реализованных проектов и кейсов в портфолио. 
    Используй этот инструмент, когда пользователь спрашивает:
    - "Покажи примеры работ по..."
    - "Есть ли у вас опыт с..."
    - "Делали ли вы сайты для..."
    
    Args:
        query: Тематика или тип проекта (например: "интернет-магазин одежды", "медицинский центр").
    """
    if not kb_tool:
        return "Ошибка: Подключение к базе знаний не установлено."
    return kb_tool.search_projects(query)

@mcp.tool()
def search_prices(query: str) -> str:
    """
    Поиск стоимости услуг и работ в прайс-листе.
    Используй этот инструмент для ответов на вопросы о бюджете, тарифах и ценах.
    
    Args:
        query: Название услуги (например: "хостинг", "разработка дизайна", "интеграция с 1С").
    """
    if not kb_tool:
        return "Ошибка: Подключение к базе знаний не установлено."
    return kb_tool.search_prices(query)

if __name__ == "__main__":
    # Запуск сервера
    mcp.run()

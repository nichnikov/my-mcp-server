from mcp.server.fastmcp import FastMCP
from tools import KnowledgeBaseSearch

# Initialize logic
kb = KnowledgeBaseSearch()

# Create Server
mcp = FastMCP("Weaviate Knowledge Base")

@mcp.tool()
def search_portfolio(query: str) -> str:
    """
    Search for completed projects, case studies, and examples of work.
    Use this to show the user what the company has built before.
    
    Args:
        query: Description of the project type (e.g. "online shop", "medical site").
    """
    return kb.search_projects(query)

@mcp.tool()
def search_prices(query: str) -> str:
    """
    Search for service prices and tariffs.
    Use this when the user asks about costs, budgets, or specific service rates.
    
    Args:
        query: Service name (e.g. "hosting", "design", "integration").
    """
    return kb.search_services(query)

if __name__ == "__main__":
    # Standard MCP run (stdio)
    mcp.run()

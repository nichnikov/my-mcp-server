import sys
import os

# Импорт общих модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.text_processor import TextsTokenizer
from shared.client import get_weaviate_client, get_embedding

class KnowledgeBaseSearch:
    def __init__(self):
        self.client = get_weaviate_client()
        self.tknz = TextsTokenizer()

    def _prepare_search(self, query):
        """Helper to get lemmatized query and vector."""
        # 1. Lemmatize
        try:
            l_list = self.tknz([query])
            lemmatized = " ".join(l_list[0]) if l_list else query
        except:
            lemmatized = query
        
        # 2. Vectorize (External Service)
        vector = get_embedding(query)
        
        return lemmatized, vector

    def search_projects(self, query: str, limit: int = 3) -> str:
        """Search for portfolio projects."""
        if not self.client.is_ready():
            return "Error: Database unavailable."

        l_query, vector = self._prepare_search(query)
        collection = self.client.collections.get("PortfolioProject")

        # Hybrid Search
        response = collection.query.hybrid(
            query=l_query,
            vector=vector,
            limit=limit,
            query_properties=["lemmatized_text", "lemmatized_title"],
            alpha=0.5
        )

        if not response.objects:
            return "No projects found."

        result = f"Projects found for '{query}':\n\n"
        for obj in response.objects:
            title = obj.properties.get("title", "No Title")
            url = obj.properties.get("url", "")
            # Snippet from full text
            text = obj.properties.get("full_text", "")
            snippet = text[:200].replace("\n", " ") + "..."
            
            result += f"- PROJECT: {title}\n  URL: {url}\n  INFO: {snippet}\n\n"
        
        return result

    def search_services(self, query: str, limit: int = 5) -> str:
        """Search for services and prices."""
        if not self.client.is_ready():
            return "Error: Database unavailable."

        l_query, vector = self._prepare_search(query)
        collection = self.client.collections.get("PriceList")

        response = collection.query.hybrid(
            query=l_query,
            vector=vector,
            limit=limit,
            query_properties=["lemmatized_service", "lemmatized_description"],
            alpha=0.5
        )

        if not response.objects:
            return "No services found."

        result = f"Services found for '{query}':\n\n"
        for obj in response.objects:
            srv = obj.properties.get("service", "")
            price = obj.properties.get("price", 0)
            desc = obj.properties.get("description", "")
            
            result += f"- SERVICE: {srv}\n  PRICE: {price} RUB\n"
            if desc:
                result += f"  NOTE: {desc}\n"
            result += "\n"
            
        return result

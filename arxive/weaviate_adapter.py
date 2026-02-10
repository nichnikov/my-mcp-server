import weaviate
import weaviate.classes.init
import requests
from typing import List, Optional
from src.domain.interfaces import IKnowledgeBase
from src.domain.entities import ProjectEntity, ServiceEntity
from src.config.settings import settings
from src.infrastructure.nlp.tokenizer import TextsTokenizer

class WeaviateAdapter(IKnowledgeBase):
    def __init__(self):
        self.client = weaviate.connect_to_local(
            host=settings.WEAVIATE_HOST,
            port=settings.WEAVIATE_PORT,
            grpc_port=settings.WEAVIATE_GRPC_PORT,
            additional_config=weaviate.classes.init.AdditionalConfig(
                timeout=weaviate.classes.init.Timeout(init=2, query=10, insert=30)
            )
        )
        self.tokenizer = TextsTokenizer()

    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get vector embedding from the local transformers service."""
        try:
            response = requests.post(settings.TRANSFORMERS_URL, json={"text": text}, timeout=10)
            response.raise_for_status()
            return response.json().get("vector")
        except Exception as e:
            print(f"Error getting vector from {settings.TRANSFORMERS_URL}: {e}")
            return None

    def _prepare_search(self, query: str):
        """Helper to get lemmatized query and vector."""
        # 1. Lemmatize
        try:
            l_list = self.tokenizer([query])
            lemmatized = " ".join(l_list[0]) if l_list else query
        except:
            lemmatized = query
        
        # 2. Vectorize
        vector = self._get_embedding(query)
        
        return lemmatized, vector

    def search_projects(self, query: str, limit: int = 3) -> List[ProjectEntity]:
        if not self.client.is_ready():
            # In a real app, we might raise a custom domain exception here
            return []

        l_query, vector = self._prepare_search(query)
        collection = self.client.collections.get("PortfolioProject")

        response = collection.query.hybrid(
            query=l_query,
            vector=vector,
            limit=limit,
            query_properties=["lemmatized_text", "lemmatized_title"],
            alpha=0.5
        )

        results = []
        for obj in response.objects:
            title = obj.properties.get("title", "No Title")
            url = obj.properties.get("url")
            text = obj.properties.get("full_text", "")
            # Create a snippet if description is not explicitly stored, or use full text
            # The original code did: snippet = text[:200].replace("\n", " ") + "..."
            snippet = text[:200].replace("\n", " ") + "..." if text else ""
            
            results.append(ProjectEntity(
                title=title,
                url=url,
                description=snippet
            ))
        
        return results

    def search_services(self, query: str, limit: int = 5) -> List[ServiceEntity]:
        if not self.client.is_ready():
            return []

        l_query, vector = self._prepare_search(query)
        collection = self.client.collections.get("PriceList")

        response = collection.query.hybrid(
            query=l_query,
            vector=vector,
            limit=limit,
            query_properties=["lemmatized_service", "lemmatized_description"],
            alpha=0.5
        )

        results = []
        for obj in response.objects:
            srv = obj.properties.get("service", "")
            price = obj.properties.get("price", 0.0)
            desc = obj.properties.get("description", "")
            
            results.append(ServiceEntity(
                name=srv,
                price=float(price),
                description=desc
            ))
            
        return results

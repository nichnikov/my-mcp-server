import httpx
from typing import List
from src.domain.interfaces import IKnowledgeBase
from src.domain.entities import ProjectEntity, ServiceEntity
from src.config.settings import settings

class SearchGatewayAdapter(IKnowledgeBase):
    def __init__(self):
        self.base_url = settings.SEARCH_GATEWAY_URL
        self.timeout = 10.0

    async def _post_request(self, endpoint: str, payload: dict) -> dict:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}{endpoint}",
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error querying Search Gateway: {e}")
                return {"results": []}

    async def search_projects(self, query: str, limit: int = 3) -> List[ProjectEntity]:
        payload = {
            "query": query,
            "limit": limit,
            "alpha": 0.5
        }
        print(f"DEBUG: Querying Gateway for projects: {payload}")
        data = await self._post_request("/search/projects", payload)
        print(f"DEBUG: Gateway response data keys: {data.keys()}")
        
        results = []
        for item in data.get("results", []):
            results.append(ProjectEntity(
                title=item.get("title", "No Title"),
                url=item.get("url"),
                description=item.get("full_text", "")[:200] + "..."
            ))
        print(f"DEBUG: Parsed {len(results)} projects")
        return results

    async def search_services(self, query: str, limit: int = 5) -> List[ServiceEntity]:
        payload = {
            "query": query,
            "limit": limit,
            "alpha": 0.5
        }
        data = await self._post_request("/search/prices", payload)
        
        results = []
        for item in data.get("results", []):
            results.append(ServiceEntity(
                name=item.get("service", "Unknown Service"),
                price=float(item.get("price", 0.0)),
                description=item.get("full_text", "")
            ))
        return results

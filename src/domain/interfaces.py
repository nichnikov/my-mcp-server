from typing import Protocol, List
from src.domain.entities import ProjectEntity, ServiceEntity

class IKnowledgeBase(Protocol):
    async def search_projects(self, query: str, limit: int = 3) -> List[ProjectEntity]:
        """Search for projects in the knowledge base."""
        ...

    async def search_services(self, query: str, limit: int = 5) -> List[ServiceEntity]:
        """Search for services in the knowledge base."""
        ...

from typing import List
from src.domain.interfaces import IKnowledgeBase
from src.domain.entities import ProjectEntity, ServiceEntity

class SearchUseCase:
    def __init__(self, kb: IKnowledgeBase):
        self.kb = kb

    async def search_projects(self, query: str) -> List[ProjectEntity]:
        return await self.kb.search_projects(query)

    async def search_services(self, query: str) -> List[ServiceEntity]:
        return await self.kb.search_services(query)

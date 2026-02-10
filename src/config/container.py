from src.infrastructure.api.search_gateway import SearchGatewayAdapter
from src.application.use_cases import SearchUseCase

class Container:
    def __init__(self):
        self._kb = None
        self._search_use_case = None

    @property
    def kb(self) -> SearchGatewayAdapter:
        if not self._kb:
            self._kb = SearchGatewayAdapter()
        return self._kb

    @property
    def search_use_case(self) -> SearchUseCase:
        if not self._search_use_case:
            self._search_use_case = SearchUseCase(self.kb)
        return self._search_use_case

# Global container instance
container = Container()

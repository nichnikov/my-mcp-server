import weaviate
import weaviate.classes.query as wvq
import requests
import json
import os
import sys

# Добавляем путь к токенизатору
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from texts_processing import TextsTokenizer

class KnowledgeBaseTool:
    def __init__(self):
        self.weaviate_url = "localhost"
        self.weaviate_port = 8080
        self.weaviate_grpc_port = 50051
        self.transformers_url = "http://localhost:9090/vectors"
        
        self.client = weaviate.connect_to_local(
            host=self.weaviate_url,
            port=self.weaviate_port,
            grpc_port=self.weaviate_grpc_port
        )
        
        # Инициализация токенизатора один раз при запуске
        self.tknz = TextsTokenizer()

    def _get_vector(self, text):
        """Внутренний метод для получения вектора"""
        try:
            response = requests.post(self.transformers_url, json={"text": text}, timeout=10)
            response.raise_for_status()
            return response.json().get("vector")
        except Exception as e:
            print(f"Error getting vector: {e}")
            return None

    def _lemmatize(self, text):
        """Внутренний метод для лемматизации"""
        try:
            lemmas_list = self.tknz([text])
            return " ".join(lemmas_list[0]) if lemmas_list else text
        except Exception:
            return text

    def search_projects(self, query: str, limit: int = 3) -> str:
        """
        Ищет проекты в портфолио.
        Args:
            query: Поисковый запрос (например, "интернет-магазин одежды")
            limit: Количество результатов
        Returns:
            Отформатированная строка с результатами для LLM
        """
        if not self.client.is_ready():
            return "Ошибка: База знаний недоступна."

        collection = self.client.collections.get("PortfolioProject")
        
        # Подготовка данных для гибридного поиска
        lemmatized_query = self._lemmatize(query)
        query_vector = self._get_vector(query)

        response = collection.query.hybrid(
            query=lemmatized_query,
            vector=query_vector,
            limit=limit,
            query_properties=["lemmatized_text", "lemmatized_title"],
            alpha=0.5
        )

        if not response.objects:
            return "По вашему запросу проектов не найдено."

        # Формирование ответа для LLM
        result_text = f"Найдены проекты по запросу '{query}':\n\n"
        for obj in response.objects:
            props = obj.properties
            title = props.get('title', 'Без названия')
            url = props.get('url', '')
            cms = props.get('cms', 'N/A')
            # Берем сниппет из полного текста
            full_text = props.get('full_text', '')
            snippet = full_text[:300].replace('\n', ' ') + "..."
            
            result_text += f"- Проект: {title}\n"
            result_text += f"  CMS: {cms}\n"
            result_text += f"  Ссылка: {url}\n"
            result_text += f"  Описание: {snippet}\n\n"
            
        return result_text

    def search_prices(self, query: str, limit: int = 5) -> str:
        """
        Ищет услуги и цены в прайс-листе.
        Args:
            query: Поисковый запрос (например, "стоимость хостинга")
            limit: Количество результатов
        Returns:
            Отформатированная строка с результатами для LLM
        """
        if not self.client.is_ready():
            return "Ошибка: База знаний недоступна."

        collection = self.client.collections.get("PriceList")
        
        lemmatized_query = self._lemmatize(query)
        query_vector = self._get_vector(query)

        response = collection.query.hybrid(
            query=lemmatized_query,
            vector=query_vector,
            limit=limit,
            query_properties=["lemmatized_service", "lemmatized_description"],
            alpha=0.5
        )

        if not response.objects:
            return "По вашему запросу услуг в прайс-листе не найдено."

        result_text = f"Найдены услуги по запросу '{query}':\n\n"
        for obj in response.objects:
            props = obj.properties
            service = props.get('service', '')
            price = props.get('price', 0)
            desc = props.get('description', '')
            
            result_text += f"- Услуга: {service}\n"
            result_text += f"  Цена: {price} руб.\n"
            if desc:
                result_text += f"  Примечание: {desc}\n"
            result_text += "\n"
            
        return result_text

    def close(self):
        self.client.close()

# Пример использования (если запустить файл напрямую)
if __name__ == "__main__":
    tools = KnowledgeBaseTool()
    try:
        print("--- Тест поиска проектов ---")
        print(tools.search_projects("разработка магазина"))
        
        print("--- Тест поиска цен ---")
        print(tools.search_prices("хостинг"))
    finally:
        tools.close()

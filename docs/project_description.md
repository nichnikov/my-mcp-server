# Анализ проекта и соответствие требованиям

## Общее описание
Проект представляет собой сервер MCP (Model Context Protocol), предоставляющий инструменты для поиска по базе знаний (Weaviate). Реализованы два варианта сервера:
1.  `mcp_server.py`: Стандартный MCP сервер (stdio).
2.  `mcp_sse_server.py`: SSE (Server-Sent Events) сервер на базе Starlette/Uvicorn.

Проект использует Weaviate как векторную базу данных и локальный сервис трансформеров для получения эмбеддингов.

## Анализ соответствия требованиям (.cursor/rules)

### 1. Архитектура (Pure Architecture)
**Статус: Не соответствует**

Проект не следует структуре, описанной в `pure-architecture.mdc`.
*   **Текущая структура:** Плоская, смешанная.
    *   `mcp_server/` содержит и логику инструментов, и точку входа.
    *   `shared/` содержит утилиты.
    *   Отсутствует разделение на слои `domain`, `application`, `infrastructure`.
*   **Требуемая структура:**
    *   `src/domain`: Интерфейсы, сущности.
    *   `src/application`: Логика агентов/инструментов.
    *   `src/infrastructure`: Реализация работы с Weaviate, HTTP клиенты.
    *   `src/presentation`: MCP серверы.

### 2. Стандарты кода (Python Standards)
**Статус: Частично соответствует**

*   **Type Safety:** Используется типизация, но не везде (например, `get_embedding` не имеет возвращаемого типа). Не используются Pydantic модели для внутренних структур данных.
*   **Dependency Injection:** Отсутствует. Клиенты создаются напрямую внутри классов (`KnowledgeBaseSearch` создает `weaviate_client` в `__init__`).
*   **Imports:** Используется `sys.path.append` для импортов, что нарушает принципы чистого кода.

### 3. Рекомендации по рефакторингу
Для приведения проекта в соответствие с правилами необходимо:
1.  Создать структуру папок `src/domain`, `src/application`, `src/infrastructure`.
2.  Выделить интерфейсы для поиска (например, `IKnowledgeBase`).
3.  Реализовать `WeaviateAdapter` в `infrastructure`.
4.  Использовать Dependency Injection для внедрения зависимостей.
5.  Заменить словари на Pydantic модели.
6.  Убрать `sys.path.append` и использовать правильную структуру пакетов.

## Технический стек
*   **Language:** Python
*   **MCP Framework:** `mcp` (FastMCP)
*   **Web Server:** `uvicorn`, `starlette`
*   **Database:** `weaviate-client` (v4)
*   **NLP:** `pymystem3` (лемматизация)
*   **HTTP Client:** `requests`

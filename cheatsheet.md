# Cheatsheet

## Setup
```bash
uv sync
cp .env.example .env   # uzupełnij klucze
```

## Notebooki
```bash
# edycja
uv run marimo edit notebooks/01_opening.py

# tryb aplikacji (tylko widok)
uv run marimo run notebooks/01_opening.py

# eksport do HTML (statyczny, z speaker view)
uv run marimo export html notebooks/01_opening.py -o out/01_opening.html

# lint
uv run marimo check notebooks/01_opening.py
```
Layout slides: w edytorze Preview → layout „slides" (zapisuje się w `notebooks/layouts/`, wersjonuj).

## Notebook 02 (modele)
```bash
uv run marimo edit notebooks/02_models.py
```
Wymaga kluczy `OPENAI_API_KEY` i `ANTHROPIC_API_KEY` w `.env`.

## Notebooks 03-06 (structured output, chaining LCEL, tools, ReAct + create_agent)
```bash
uv run marimo edit notebooks/03_structured_output.py
uv run marimo edit notebooks/04_chaining.py
uv run marimo edit notebooks/05_tools.py
uv run marimo edit notebooks/06_react_agent.py
```
Wspólne narzędzia (support): `notebooks/support_tools.py`.

## Notebook 07 (middleware + HITL)
```bash
uv run marimo edit notebooks/07_middleware.py
```

## MCP: serwer Keycloak (`notebooks/keycloak_mcp_server.py`)
```bash
# interaktywny MCP Inspector w przeglądarce (wymaga Node.js)
uv run fastmcp dev inspector notebooks/keycloak_mcp_server.py

# sam serwer (stdio, uruchamiany przez klienta MCP)
uv run python notebooks/keycloak_mcp_server.py
```
Wymaga w `.env`: `KEYCLOAK_URL`, `KEYCLOAK_REALM`, `KEYCLOAK_CLIENT_ID`, `KEYCLOAK_CLIENT_SECRET` (klient z service account i rolą `view-clients`).

## Notebook 08 (MCP)
```bash
uv run marimo edit notebooks/08_mcp.py
```

## Notebook 09 (memory: checkpointer + store)
```bash
uv run marimo edit notebooks/09_memory.py
```

## Notebook 10 (RAG)
```bash
uv run marimo edit notebooks/10_rag.py
```

## Notebook 11 (LangGraph: teoria)
```bash
uv run marimo edit notebooks/11_langgraph.py
```

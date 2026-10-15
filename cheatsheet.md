# Ściągawka

## Przygotowanie środowiska
```bash
uv sync
cp .env.example .env   # uzupełnij klucze
```

## Notebook `01_opening.py` — wprowadzenie
```bash
uv run marimo edit notebooks/01_opening.py
```

```bash
uv run marimo run notebooks/01_opening.py
```

```bash
uv run marimo check notebooks/01_opening.py
```
Tryb slajdów: w edytorze wybierz podgląd („Preview”) → układ „slides” (zapisuje się w `notebooks/layouts/`; dodaj te pliki do kontroli wersji).

## Notebook `02_models.py` — modele
```bash
uv run marimo edit notebooks/02_models.py
```

```bash
uv run marimo run notebooks/02_models.py
```

```bash
uv run marimo check notebooks/02_models.py
```

Wymaga kluczy `OPENAI_API_KEY` i `ANTHROPIC_API_KEY` w `.env`.

## Notebook `03_structured_output.py` — ustrukturyzowane odpowiedzi

```bash
uv run marimo edit notebooks/03_structured_output.py
```

```bash
uv run marimo run notebooks/03_structured_output.py
```

```bash
uv run marimo check notebooks/03_structured_output.py
```

## Notebook `04_chaining.py` — łączenie wywołań za pomocą LCEL

```bash
uv run marimo edit notebooks/04_chaining.py
```

```bash
uv run marimo run notebooks/04_chaining.py
```

```bash
uv run marimo check notebooks/04_chaining.py
```

## Notebook `05_tools.py` — narzędzia

```bash
uv run marimo edit notebooks/05_tools.py
```

```bash
uv run marimo run notebooks/05_tools.py
```

```bash
uv run marimo check notebooks/05_tools.py
```

## Notebook `06_react_agent.py` — agent ReAct i `create_agent`

```bash
uv run marimo edit notebooks/06_react_agent.py
```

```bash
uv run marimo run notebooks/06_react_agent.py
```

```bash
uv run marimo check notebooks/06_react_agent.py
```

Wspólne narzędzia do obsługi klienta: `notebooks/support_tools.py`.

## Notebook `07_middleware.py` — warstwa pośrednia i udział człowieka (HITL)

```bash
uv run marimo edit notebooks/07_middleware.py
```

```bash
uv run marimo run notebooks/07_middleware.py
```

```bash
uv run marimo check notebooks/07_middleware.py
```

## Notebook `08_mcp.py` — MCP

```bash
uv run marimo edit notebooks/08_mcp.py
```

```bash
uv run marimo run notebooks/08_mcp.py
```

```bash
uv run marimo check notebooks/08_mcp.py
```

### MCP: serwer Keycloak (`notebooks/keycloak_mcp_server.py`)

```bash
# interaktywny MCP Inspector w przeglądarce (wymaga Node.js)
uv run fastmcp dev inspector notebooks/keycloak_mcp_server.py

# sam serwer (stdio, uruchamiany przez klienta MCP)
uv run python notebooks/keycloak_mcp_server.py
```
Wymaga w `.env`: `KEYCLOAK_URL`, `KEYCLOAK_REALM`, `KEYCLOAK_CLIENT_ID`, `KEYCLOAK_CLIENT_SECRET` (klient z kontem serwisowym i rolą `view-clients`).

## Notebook `09_memory.py` — pamięć: checkpointer i store

```bash
uv run marimo edit notebooks/09_memory.py
```

```bash
uv run marimo run notebooks/09_memory.py
```

```bash
uv run marimo check notebooks/09_memory.py
```

## Notebook `10_rag.py` — generowanie odpowiedzi wspomagane wyszukiwaniem (RAG)

```bash
uv run marimo edit notebooks/10_rag.py
```

```bash
uv run marimo run notebooks/10_rag.py
```

```bash
uv run marimo check notebooks/10_rag.py
```

## Notebook `11_langgraph.py` — LangGraph: teoria

```bash
uv run marimo edit notebooks/11_langgraph.py
```

```bash
uv run marimo run notebooks/11_langgraph.py
```

```bash
uv run marimo check notebooks/11_langgraph.py
```

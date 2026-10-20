# Cheatsheet

## Environment setup
```bash
uv sync
cp .env.example .env   # fill in the API keys
```

## Notebook `01_opening.py` — introduction
```bash
uv run marimo edit notebooks/01_opening.py
```

```bash
uv run marimo run notebooks/01_opening.py
```

```bash
uv run marimo check notebooks/01_opening.py
```
Slides mode: in the editor, select Preview → the "slides" layout (saved in `notebooks/layouts/`; add these files to version control).

## Notebook `02_models.py` — models
```bash
uv run marimo edit notebooks/02_models.py
```

```bash
uv run marimo run notebooks/02_models.py
```

```bash
uv run marimo check notebooks/02_models.py
```

Requires `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` in `.env`.

Local model (Ollama):
```bash
ollama serve
```
```bash
ollama run qwen3.5
```

## Notebook `03_structured_output.py` — structured output

```bash
uv run marimo edit notebooks/03_structured_output.py
```

```bash
uv run marimo run notebooks/03_structured_output.py
```

```bash
uv run marimo check notebooks/03_structured_output.py
```

## Notebook `04_chaining.py` — chaining with LCEL

```bash
uv run marimo edit notebooks/04_chaining.py
```

```bash
uv run marimo run notebooks/04_chaining.py
```

```bash
uv run marimo check notebooks/04_chaining.py
```

## Notebook `05_tools.py` — tools

```bash
uv run marimo edit notebooks/05_tools.py
```

```bash
uv run marimo run notebooks/05_tools.py
```

```bash
uv run marimo check notebooks/05_tools.py
```

## Notebook `06_react_agent.py` — ReAct agent and `create_agent`

```bash
uv run marimo edit notebooks/06_react_agent.py
```

```bash
uv run marimo run notebooks/06_react_agent.py
```

```bash
uv run marimo check notebooks/06_react_agent.py
```

Shared customer support tools: `notebooks/support_tools.py`.

## Notebook `07_middleware.py` — middleware and human-in-the-loop (HITL)

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

### MCP: Keycloak server (`notebooks/keycloak_mcp_server.py`)

```bash
# interactive MCP Inspector in the browser (requires Node.js)
uv run fastmcp dev inspector notebooks/keycloak_mcp_server.py
```

```bash
# standalone server (stdio, launched by the MCP client)
uv run python notebooks/keycloak_mcp_server.py
```
Requires `KEYCLOAK_URL`, `KEYCLOAK_REALM`, `KEYCLOAK_CLIENT_ID`, and `KEYCLOAK_CLIENT_SECRET` in `.env` (a client with a service account and the `view-clients` role).

## Notebook `09_memory.py` — memory: checkpointer and store

```bash
uv run marimo edit notebooks/09_memory.py
```

```bash
uv run marimo run notebooks/09_memory.py
```

```bash
uv run marimo check notebooks/09_memory.py
```

## Notebook `10_rag.py` — retrieval-augmented generation (RAG)

```bash
uv run marimo edit notebooks/10_rag.py
```

```bash
uv run marimo run notebooks/10_rag.py
```

```bash
uv run marimo check notebooks/10_rag.py
```

## Notebooks `11_*` — LangGraph: theory + 9 examples

Theory and one notebook per example. The examples are standalone and need `OPENAI_API_KEY` in `.env`.

```bash
uv run marimo edit notebooks/11_00_langgraph_theory.py
```

```bash
uv run marimo edit notebooks/11_01_langgraph_ex1_first_graph.py
```

```bash
uv run marimo edit notebooks/11_02_langgraph_ex2_cond_and_rout.py
```

```bash
uv run marimo edit notebooks/11_03_langgraph_ex3_pipeline.py
```

```bash
uv run marimo edit notebooks/11_04_langgraph_ex4_loop.py
```

```bash
uv run marimo edit notebooks/11_05_langgraph_ex5_generate_validate.py
```

```bash
uv run marimo edit notebooks/11_06_langgraph_ex6_parallel.py
```

```bash
uv run marimo edit notebooks/11_07_langgraph_ex7_map_reduce.py
```

```bash
uv run marimo edit notebooks/11_08_langgraph_ex8_subgraphs.py
```

```bash
uv run marimo edit notebooks/11_09_langgraph_ex9_agent.py
```

Check all of them at once:

```bash
uv run marimo check notebooks/11_*.py
```

## Notebook `bonus_docling.py` — Docling: documents to structured Markdown (bonus)

```bash
uv run marimo edit notebooks/bonus_docling.py
```

```bash
uv run marimo run notebooks/bonus_docling.py
```

```bash
uv run marimo check notebooks/bonus_docling.py
```

The first run downloads Docling models (needs internet, takes a while). Run it once before the talk. No API key needed.

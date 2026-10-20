import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # Introduction to LangChain and LangGraph

    - Practical, code-first
    - Every part (almost) of this talk is a marimo notebook you can run yourself
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## How did we get here? A timeline

    | When | Who | What |
    |---|---|---|
    | 1995 | Russell & Norvig (textbook *AI: A Modern Approach*) | The classic term **"intelligent agent"**: something that perceives, decides and acts. The word is old, long before LLMs |
    | Oct 6, 2022 | Yao et al. (Princeton, Google) | **ReAct** paper: an LLM interleaves *reasoning* and *acting* (tool calls). The recipe of today's LLM agents |
    | Oct 2022 | Harrison Chase | **LangChain** is created: first building blocks for LLM apps; "agents" become one of its core ideas |
    | Nov 30, 2022 | OpenAI | **ChatGPT** opens to everyone (a free research preview on chatgpt.com) |
    | Mar 1, 2023 | OpenAI | **ChatGPT API** (REST, `gpt-3.5-turbo`): developers can build on it |
    | Late Mar 2023 | Yohei Nakajima, Toran Bruce Richards | **BabyAGI** (Mar 28) and **Auto-GPT** (Mar 30): "autonomous AI agents" go viral. This is when **"agent"** becomes a buzzword for LLM apps |
    | Jun 13, 2023 | OpenAI | **Function calling** in the API: the model can request a tool in a structured way |
    | 2024 | LangChain team | **LangGraph**: agents as graphs |
    | Nov 2024 | Anthropic | **MCP**: an open standard for connecting tools to AI apps |
    | 2025 | The whole industry | Coding and research agents go mainstream; **LangChain 1.0 and LangGraph 1.0** |
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## What is an agent?

    **An agent is an LLM that decides what to do next, uses tools to do it, and repeats until the goal is reached.**

    ```text
    goal → think → call a tool → observe the result → think → ... → answer
    ```

    ### Chat or agent?

    | | **Chat** | **Agent** |
    |---|---|---|
    | **Output** | Text answer | Actions + final answer |
    | **Tools** | None | Search, database, APIs, files, code |
    | **Steps** | One prompt → one answer | Many steps, number decided by the model |
    | **Who decides the flow** | You (the user) | The model |
    | **Effect on the world (!!!)** | None | Can read and change things |
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Agents you may already know

    | Product | Chat mode | Agent mode |
    |---|---|---|
    | **GitHub Copilot** | Chat answers a coding question | Agent mode edits files, runs commands, fixes its own errors |
    | **Claude Code** | n/a | Reads the repo, runs tools, iterates until the task is done |
    | **ChatGPT / Claude** | Plain conversation | Web search, deep research, code execution |
    | **Customer support bot** | FAQ answers | Looks up an order, issues a refund after approval |
    """)
    return


@app.cell
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## Inference engines: where the model actually runs

    A model is just a **file with weights**. Something has to load it into memory (GPU / CPU) and turn your prompt into tokens. That software is an **inference engine** (*inference* = using a trained model, as opposed to *training* it).

    - It loads the model and generates the answer, as fast and as cheaply as possible.
    - It exposes an **API**, very often **OpenAI-compatible**, so any client can talk to it.
    - OpenAI or Anthropic run their own engines for you (a *managed* service). Locally, you pick one yourself.
    """),
        mo.mermaid(
            """
            flowchart LR
                A["Our app<br/>(LangChain / LangGraph)"] -->|"HTTP API"| E["Inference engine"]
                E --> W["Model weights"]
                W --> H["GPU / CPU"]
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    | Engine | What it is | Typical use |
    |---|---|---|
    | **Ollama** | One command to download and run a model | Local development, demos, a laptop |
    | **llama.cpp** (`llama-server`) | Lightweight C++ engine, runs on CPU and Apple Silicon | Local, small footprint, quantized (GGUF) models |
    | **LM Studio** | Desktop app with a GUI and a local API server | Trying models without the terminal |
    | **vLLM** | High-throughput server for GPUs | Production: many users at once, own servers |
    | **OpenAI / Anthropic API** | Managed engines in the provider's cloud | No hardware to run, pay per token |

    **For us:** LangChain talks to all of them through the same chat model interface (section 2): `init_chat_model("ollama:...")`, or `ChatOpenAI(base_url=...)` for any OpenAI-compatible server.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## LangChain and LangGraph

    | | **LangChain** | **LangGraph** |
    |---|---|---|
    | **What it is** | A toolkit for building LLM apps and agents | An engine that runs your workflow as a graph |
    | **It gives you** | Models, prompts, tools, ready-made agent | Steps, branches, loops, saved state, pauses for approval |
    | **Choose it when** | You want a working agent quickly | You need control over the order of steps |

    **They work together:** a LangChain agent runs on top of LangGraph. Start with LangChain, go deeper into LangGraph when you need more control.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What will we cover in this talk?

    | # | Topic | You will see |
    |---|---|---|
    | 2 | Models | Switch OpenAI → Claude → local Ollama |
    | 3 | Structured output | LLM answer → Pydantic object |
    | 4 | Chaining (LCEL) | `prompt \| model \| parser` |
    | 5 | Tools | Custom tools, tool calling by hand |
    | 6 | ReAct agents | `create_agent`, web search, ready-made tools |
    | 7 | Middleware & HITL | Approve a tool call before it runs |
    | 8 | MCP | Inspect Keycloak clients from the console |
    | 9 | Memory | Short-term and long-term |
    | 10 | RAG | Chunks, embeddings, vector store, RAG as a tool |
    | 11 | LangGraph | Routing, parallel, map-reduce, subgraphs, agent as a graph |
    | 12 | LangSmith | Tracing and evaluation |
    """)
    return


if __name__ == "__main__":
    app.run()

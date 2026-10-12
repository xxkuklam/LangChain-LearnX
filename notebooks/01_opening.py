import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # Introduction to LangChain and LangGraph

    **From a single prompt to a working AI application**

    - Practical, code-first
    - Every part of this talk is a marimo notebook you can run yourself
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
    ## Agent vs. LLM application

    - **LLM application** = any software that uses an LLM as one of its parts (a summarizer, a chatbot, a document search...).
    - **Agent** = an LLM application where the **LLM decides what happens next**, instead of our code.

    So every agent is an LLM application, but not every LLM application is an agent.

    **The key question: who decides the next step, our code or the model?**
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    | | **Workflow** | **Agent** |
    |---|---|---|
    | **Path** | Predefined in code | Decided by the model at runtime |
    | **Predictable** | High | Lower |
    | **Flexible** | Low | High |
    | **Typical use** | Invoice processing, classification | Research, coding, open-ended support |

    Most production systems **mix both**: fixed structure around agent-like steps. That is exactly where LangGraph helps.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## A short history

    | When | What |
    |---|---|
    | 2022 | **ChatGPT** brings LLMs to everyone; **ReAct** paper (reason + act); **LangChain** appears |
    | 2023 | **Function / tool calling** in APIs; first agent experiments (e.g. AutoGPT) |
    | 2024 | **LangGraph** (agents as graphs); **MCP** standard for connecting tools |
    | 2025 | Coding and research agents go mainstream; **LangChain 1.0 and LangGraph 1.0** |
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
    mo.md(r"""
    ## What an LLM application looks like
    """)
    return


@app.cell
def _(mo):
    mo.mermaid(
        """
        flowchart LR
            U["User"] --> APP

            subgraph APP["Your application"]
                direction LR
                M["Model"]
                T["Tools / APIs"]
                D["Your data (RAG, SQL)"]
                MEM["Memory"]
                H["Human approval"]
                M <--> T
                M <--> D
                M <--> MEM
                M --> H
            end

            APP --> R["Result"]
        """
    )
    return


@app.cell
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


@app.cell
def _(mo):
    mo.md(r"""
    ## What will we cover in this talk?

    | # | Topic | You will see |
    |---|---|---|
    | 2 | Models | Switch OpenAI → Claude → local Ollama |
    | 3 | Structured output | LLM answer → Pydantic object |
    | 4 | Tools & agents | Tool calling, ReAct, web search, SQL |
    | 5 | Middleware & HITL | Approve a tool call before it runs |
    | 6 | MCP | Inspect Keycloak clients from the console |
    | 7 | Memory | Short-term and long-term |
    | 8 | RAG | FAISS and pgvector |
    | 9 | LangGraph | Routing, parallel, map-reduce, subgraphs |
    | 10 | LangSmith | Tracing and evaluation |
    """)
    return


if __name__ == "__main__":
    app.run()

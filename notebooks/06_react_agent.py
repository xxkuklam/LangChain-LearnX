import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 4. Tools and agents

    ## ReAct and `create_agent`
    """)
    return


@app.cell
def _():
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv(usecwd=True))  # load API keys from .env
    return


@app.cell
def _():
    # The support tools from the previous notebook (code in support_tools.py)
    from langchain.chat_models import init_chat_model
    from langchain.messages import HumanMessage, SystemMessage
    from support_tools import SYSTEM_PROMPT, TOOLS, USER_MESSAGE

    MODEL = "openai:gpt-5.4-mini"

    tools = TOOLS
    tools_by_name = {t.name: t for t in tools}
    model_with_tools = init_chat_model(MODEL).bind_tools(tools)
    messages = [SystemMessage(SYSTEM_PROMPT), HumanMessage(USER_MESSAGE)]
    return (
        HumanMessage,
        MODEL,
        SYSTEM_PROMPT,
        USER_MESSAGE,
        init_chat_model,
        messages,
        model_with_tools,
        tools,
        tools_by_name,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## ReAct: Reason + Act

    In the previous notebook we ran the tools by hand. That loop is a pattern called **ReAct** (Reasoning + Acting):

    1. **Reason:** the model looks at the history and decides what to do next.
    2. **Act:** it asks for a tool.
    3. **Observe:** our code runs the tool and the result goes back into the history.
    4. Repeat until the model can answer without any tool.

    The loop below is all there is to it. We only add `max_steps` to protect against endless (paid!) loops.
    """),
        mo.mermaid(r"""
    flowchart LR
        Q["Question"] --> R["Reason<br/>(model)"]
        R -->|"tool_calls"| A["Act<br/>(run tools)"]
        A -->|"ToolMessage"| R
        R -->|"no tool_calls"| F["Final answer"]
    """),
    ])
    return


@app.cell
def _(messages, model_with_tools, tools_by_name):
    def run_react_loop(history, max_steps=5):
        for _ in range(max_steps):
            ai_message = model_with_tools.invoke(history)  # Reason
            history = [*history, ai_message]
            if not ai_message.tool_calls:
                return history  # final answer
            for call in ai_message.tool_calls:  # Act + Observe
                history.append(tools_by_name[call["name"]].invoke(call))
        return history


    manual_history = run_react_loop(messages)
    print(manual_history[-1].text)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## `create_agent`: the same loop, done for us

    ```python
    from langchain.agents import create_agent
    ```

    Give it a model, tools and a system prompt. It returns a ready-to-run agent (a compiled **LangGraph** graph) that runs the ReAct loop for you.
    """)
    return


@app.cell
def _(MODEL, SYSTEM_PROMPT, tools):
    from langchain.agents import create_agent

    agent = create_agent(
        model=MODEL,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )
    return agent, create_agent


@app.cell
def _(HumanMessage, USER_MESSAGE, agent):
    # Input is a state dict with messages, not a string
    result = agent.invoke({"messages": [HumanMessage(USER_MESSAGE)]})

    print(result["messages"][-1].text)  # final answer
    print("messages in state:", len(result["messages"]))
    return (result,)


@app.cell
def _(result):
    # The whole history: Human -> AI(tool_calls) -> Tool -> ... -> AI
    for message_in_state in result["messages"]:
        message_in_state.pretty_print()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Watch the agent work: `stream`

    `stream(..., stream_mode="updates")` yields one update per step, handy for progress bars and live demos.
    """)
    return


@app.cell
def _(HumanMessage, USER_MESSAGE, agent):
    for step in agent.stream({"messages": [HumanMessage(USER_MESSAGE)]}, stream_mode="updates"):
        for node_name, update in step.items():
            last = update["messages"][-1]
            print(f"[{node_name}]", last.type, "->", last.text or last.tool_calls)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Under the hood: the agent is a graph
    """)
    return


@app.cell
def _(agent, mo):
    mo.mermaid(agent.get_graph().draw_mermaid())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model vs. agent

    | | **Chat model** | **Agent** (`create_agent`) |
    |---|---|---|
    | Input | string or messages | state dict `{"messages": [...]}` |
    | Output | one `AIMessage` | full state (all messages) |
    | Tools | only *asks* for them | *runs* them and loops |
    | LLM calls per `invoke` | 1 | as many as needed |
    | Extras | none | memory, middleware, human approval |

    ## Takeaways

    - **ReAct** = reason, act, observe, repeat.
    - **`create_agent`** is that loop, ready-made, built on LangGraph.
    - Write the loop yourself to understand it, use `create_agent` in real code.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## A local model with web search

    A local model knows only what it learned during training, so it cannot know recent facts.
    Give it a **search tool** and the same model can find them.

    We ask the same question twice, to the same local model (Ollama):

    - **Agent A**: no tools
    - **Agent B**: web search tool (Tavily)
    """),
        mo.mermaid(r"""
    flowchart LR
        subgraph A["Agent A"]
            QA["Question"] --> MA["Local model<br/>(Ollama)"] --> RA["Answer from memory"]
        end
        subgraph B["Agent B"]
            QB["Question"] --> MB["Local model<br/>(Ollama)"]
            MB <-->|"tool call"| T["Tavily search"]
            MB --> RB["Answer from the web"]
        end
    """),
    ])
    return


@app.cell
def _(create_agent, init_chat_model):
    from langchain_tavily import TavilySearch

    LOCAL_MODEL = "ollama:qwen3.5:latest"
    SEARCH_QUESTION = "What is the latest version of the Python LangChain package and what changed in it?"

    local_model = init_chat_model(LOCAL_MODEL, reasoning=False)  # reasoning off = faster answers
    tavily_search = TavilySearch(max_results=3)  # needs TAVILY_API_KEY in .env

    agent_a = create_agent(model=local_model, tools=[])
    agent_b = create_agent(
        model=local_model,
        tools=[tavily_search],
        system_prompt="You are a helpful assistant. Use web search for anything.",
    )
    return SEARCH_QUESTION, agent_a, agent_b


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Agent A: no tools
    """)
    return


@app.cell
def _(HumanMessage, SEARCH_QUESTION, agent_a):
    result_a = agent_a.invoke({"messages": [HumanMessage(SEARCH_QUESTION)]})
    answer_a = result_a["messages"][-1].text

    print(answer_a)
    return (answer_a,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Agent B: with Tavily search

    We print every step to see **when the model searches**.
    """)
    return


@app.cell
def _(HumanMessage, SEARCH_QUESTION, agent_b):
    answer_b = ""
    for step_b in agent_b.stream({"messages": [HumanMessage(SEARCH_QUESTION)]}, stream_mode="updates"):
        for node_b, update_b in step_b.items():
            last_b = update_b["messages"][-1]
            if last_b.type == "ai" and last_b.tool_calls:
                print(f"[{node_b}] search request:", last_b.tool_calls[0]["args"])
            elif last_b.type == "tool":
                print(f"[{node_b}] got {len(last_b.content)} characters of search results")
            else:
                answer_b = last_b.text

    print()
    print(answer_b)
    return (answer_b,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Comparison
    """)
    return


@app.cell
def _(answer_a, answer_b):
    import json
    from importlib.metadata import version
    from urllib.request import urlopen

    # Ground truth: what PyPI says right now
    with urlopen("https://pypi.org/pypi/langchain/json", timeout=10) as response_pypi:
        latest_on_pypi = json.load(response_pypi)["info"]["version"]

    print("Installed in this project:", version("langchain"))
    print("Latest on PyPI right now: ", latest_on_pypi)
    print()
    print("=== Agent A (no tools) ===")
    print(answer_a)
    print()
    print("=== Agent B (Tavily search) ===")
    print(answer_b)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What we learned

    - A local model is **frozen in time**: it answers from training data, confidently but possibly outdated.
    - A **tool** gives it fresh information. The model decides *when* to search and what to search for.
    - The model stays **local**: only the search query goes to the internet.
    - Same agent code, the only difference is `tools=[tavily_search]`.
    - Tool calling quality of local models varies, so always test the model you plan to use.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Pre-built & community tools (1/2): partner packages

    You do not have to write every tool. LangChain has a large catalog of integrations: install the package, create the tool, put it in `tools=[...]`.

    | Category | Examples (package) | What it gives the agent |
    |---|---|---|
    | **Search** | Tavily (`langchain-tavily`), Exa (`langchain-exa`), Perplexity (`langchain-perplexity`), Google (`langchain-google-community`) | Fresh information from the web |
    | **Code interpreter** | Bedrock AgentCore, Azure Container Apps sessions, Capsule | Run code in a sandbox (calculations, data analysis) |
    | **Productivity** | Gmail and Google Calendar toolkits (`langchain-google-community`), Composio (`composio-langchain`) | Read and send mail, manage events, 500+ SaaS apps with OAuth |
    | **Web browsing / scraping** | Firecrawl (`langchain-firecrawl`), Hyperbrowser, Stagehand, Browserless | Open pages, click, extract content |
    | **Databases** | MCP Toolbox (`toolbox-langchain`), Memgraph, Stardog | Query SQL and graph databases |
    | **Finance** | Stripe Agent Toolkit (`stripe-agent-toolkit`) | Payments and billing actions |
    | **Security** | URLCheck, Tonic Textual (PII detection), SidClaw (approval policies) | Check links, hide personal data, control risky calls |
    | **Media** | Magic Hour, Google Imagen (`langchain-google-vertexai`) | Generate images and video |

    **Other sources of tools:**

    - **MCP servers**: any tool server that speaks the Model Context Protocol (next sections).
    - **Provider built-in tools**: some model providers run tools such as web search on their side.
    - **Your own `@tool` functions**: like the support tools in this talk.

    Always check what a tool can *do* before you give it to an agent: reading is safe, sending e-mail or paying money is not. That is what human approval (next section) is for.

    Full catalog: https://docs.langchain.com/oss/python/integrations/tools
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Pre-built & community tools (2/2): `langchain-community`

    The `langchain-community` package (`uv add langchain-community`) collects **hundreds of community-maintained tools and toolkits**. A *toolkit* is a ready-made **group of tools** for one system: `toolkit.get_tools()` returns a list you pass to the agent.

    ### Toolkits (`langchain_community.agent_toolkits`)

    | Toolkit | What the agent can do |
    |---|---|
    | **`SQLDatabaseToolkit`** | List tables, read the schema, check and run SQL queries |
    | **`FileManagementToolkit`** | Read, write, copy, move, delete and search local files |
    | **`GmailToolkit`** | Search, read and send Gmail messages |
    | **`O365Toolkit`** | Office 365: mail and calendar |
    | **`SlackToolkit`** | Read channels, send Slack messages |
    | **`JiraToolkit`** | Create and search Jira issues |
    | **`PlayWrightBrowserToolkit`** | Control a real browser: navigate, click, extract text |
    | **`OpenAPIToolkit`** | Call any REST API described by an OpenAPI spec |
    | **`JsonToolkit`** | Explore a large JSON document |
    | **`PowerBIToolkit`**, **`SparkSQLToolkit`** | Query Power BI datasets or Spark SQL |
    | **`ZapierToolkit`**, **`ConneryToolkit`** | Trigger actions in thousands of apps through Zapier or Connery |
    | **`AmadeusToolkit`**, **`NasaToolkit`**, **`PolygonToolkit`**, **`SteamToolkit`** | Travel, NASA, market data and Steam APIs |

    ### Single tools (`langchain_community.tools`)

    | Tool | What it does |
    |---|---|
    | `DuckDuckGoSearchRun` | Web search without an API key |
    | `WikipediaQueryRun`, `ArxivQueryRun`, `PubmedQueryRun` | Look things up in Wikipedia, arXiv, PubMed |
    | `OpenWeatherMapQueryRun` | Current weather (needs an API key) |
    | `YouTubeSearchTool` | Search YouTube |
    | `RequestsGetTool` | Make an HTTP GET request |
    | `ShellTool` | Run shell commands |
    | `HumanInputRun` | Ask the human a question and wait for the answer |

    ### Use with care

    - **Quality varies**: community code is maintained by volunteers and vendors. Check the code and version before relying on it.
    - **Powerful = risky**: `ShellTool`, `FileManagementToolkit`, `PlayWrightBrowserToolkit`, `GmailToolkit` can change or send things. Give an agent only the tools it needs (for example read-only file tools) and add human approval for the rest.
    - **SQL**: `SQLDatabaseToolkit` is a good start, but use a **read-only** database user.
    - **Not always the best option**: a small custom `@tool` or an MCP server is often simpler and safer.

    Reference: https://reference.langchain.com/python/langchain-community
    """)
    return


if __name__ == "__main__":
    app.run()

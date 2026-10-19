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
    # 8. MCP: Model Context Protocol

    ## One standard way to give tools to any AI application
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## The problem: every integration is custom

    Our `@tool` functions from section 5 live **inside one Python app**.
    What if the same capability (e.g. "read from Keycloak", "search Jira") is needed by **many** AI apps, written in different languages?

    Without a standard: every app needs its own connector for every system, **N × M integrations**.
    """),
        mo.mermaid(
            """
            flowchart LR
                subgraph Apps
                    A1["Our agent"]
                    A2["IDE assistant"]
                    A3["Chat app"]
                end
                subgraph Systems
                    S1["Keycloak"]
                    S2["Jira"]
                    S3["Database"]
                end
                A1 --- S1 & S2 & S3
                A2 --- S1 & S2 & S3
                A3 --- S1 & S2 & S3
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## The idea: a standard plug

    **MCP is an open protocol** that defines how an AI application talks to external tools and data.
    Think of **USB-C**: one connector, any device.

    - Each system gets **one MCP server** (written once).
    - Each AI app gets **one MCP client** (built once).
    - Now it is **N + M** instead of N × M.
    """),
        mo.mermaid(
            """
            flowchart LR
                subgraph Apps["AI apps (MCP clients)"]
                    A1["Our agent"]
                    A2["IDE assistant"]
                    A3["Chat app"]
                end
                P(("MCP"))
                subgraph Servers["MCP servers"]
                    S1["Keycloak"]
                    S2["Jira"]
                    S3["Database"]
                end
                A1 --- P
                A2 --- P
                A3 --- P
                P --- S1
                P --- S2
                P --- S3
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## Who is who

    | Role | What it is | Example |
    |---|---|---|
    | **Host** | The AI application the user talks to | Our LangChain agent, Claude Desktop, an IDE |
    | **Client** | Connector inside the host, one per server | `MCPAdapter` from `langchain.mcp` |
    | **Server** | A small program that exposes capabilities | Our Keycloak server |

    The server knows **nothing** about the model. It only answers protocol requests.
    """),
        mo.mermaid(
            """
            flowchart LR
                U["User"] --> H
                subgraph H["Host (our agent)"]
                    M["LLM"]
                    C["MCP client"]
                    M <--> C
                end
                C <-->|"MCP"| S["MCP server"]
                S <--> X["Keycloak"]
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What can a server expose?

    | Primitive | What it is | Who decides to use it | Example |
    |---|---|---|---|
    | **Tools** | Functions the model can call | The **model** | `list_clients(realm)` |
    | **Resources** | Read-only data (files, records) | The **application** | A config file, a DB schema |
    | **Prompts** | Reusable prompt templates | The **user** | "Review this realm's clients" |

    In this talk we focus on **tools**: that is what agents use most, and it is what we already know from section 5.

    Good to know: MCP also lets a server ask the user for input (*elicitation*) and ask the host's model to generate text (*sampling*).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Transports: how client and server talk

    The messages are always **JSON-RPC**. Only the "pipe" differs:

    | Transport | How it works | Use it for |
    |---|---|---|
    | **stdio** | Client starts the server as a **subprocess**, talks via stdin/stdout | Local tools, development, our demo |
    | **Streamable HTTP** | Server runs as a **web service** at a URL, e.g. `https://host/mcp` | Remote / shared / team servers |

    ⚠️ The older **SSE** transport is deprecated in the MCP spec: prefer Streamable HTTP for anything remote.

    **Rule of thumb:** stdio = "a plugin on my machine", HTTP = "a service in my company".
    """)
    return


@app.cell(hide_code=True, expand_output=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## What happens on the wire

    Three steps are enough to understand the whole protocol:

    1. **initialize**: client and server agree on the protocol version and capabilities.
    2. **tools/list**: the client asks "what can you do?" and gets names, descriptions and **JSON schemas** of the arguments.
    3. **tools/call**: the client runs one tool with arguments and gets the result.

    The tool list is **discovered at runtime**: add a tool on the server and every client sees it, with no change in the agent code.
    """),
        mo.mermaid(
            """
            sequenceDiagram
                participant A as Agent (MCP client)
                participant S as MCP server
                A->>S: initialize
                S-->>A: version + capabilities
                A->>S: tools/list
                S-->>A: names, descriptions, input schemas
                Note over A: the schemas go to the LLM as tool definitions
                A->>S: tools/call list_clients {realm: "master"}
                S-->>A: result (text / JSON)
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## MCP tool vs. our own `@tool`

    For the LLM there is **no difference**: it sees a name, a description and an argument schema.
    The difference is **where the code lives**.

    | | `@tool` function | MCP tool |
    |---|---|---|
    | **Code runs** | Inside our Python process | In a separate server process / service |
    | **Language** | Python | Any |
    | **Reuse** | Copy the module | Any MCP client connects to it |
    | **Credentials** | In our app | Stay on the server |
    | **Who owns it** | Us | Can be another team or a vendor |
    | **Extra moving part** | None | A server to run and update |

    **Use `@tool`** for logic specific to one app. **Use MCP** when the capability is shared, owned by someone else, or must keep its secrets away from the agent.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Security: an MCP server is code you run

    - A **stdio** server runs on your machine with **your permissions**: install only servers you trust.
    - Tool **names and descriptions go into the prompt**: a malicious server can try to steer the model (prompt injection).
    - Give the server the **minimum rights**. Our Keycloak server will be **read-only**: its service account only has `view-*` roles.
    - Combine with what we saw before: **human in the loop** for anything that changes data.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## MCP in LangChain: `langchain.mcp`

    MCP support ships **inside LangChain** (extra `mcp`, beta):

    ```bash
    uv add "langchain[mcp]"
    ```

    ```python
    from pathlib import Path
    from langchain.agents import create_agent
    from langchain.mcp import MCPAdapter

    async with MCPAdapter(Path("server.py")) as adapter:      # stdio: a script we start
        tools = await adapter.list_tools()                    # MCP tools -> LangChain tools
        agent = create_agent(MODEL, tools)                    # the rest is the same as before
    ```

    | Target passed to `MCPAdapter` | Transport |
    |---|---|
    | `Path("server.py")` | stdio (starts a subprocess) |
    | `"https://host/mcp"` | Streamable HTTP |
    | `{"mcpServers": {...}}` | Several servers at once (tools get a `server_` prefix) |

    ⚠️ Przestarzałe: `langchain-mcp-adapters` (`MultiServerMCPClient`) → obecnie: `langchain.mcp.MCPAdapter`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Demo: an MCP server for a local Keycloak

    **Scenario:** an agent acts as a **Keycloak / OAuth 2.0 / OIDC expert** and reviews the *Access settings* of our clients.

    - The server is `notebooks/keycloak_mcp_server.py` (built with `fastmcp`).
    - It has **two read-only tools**: `list_realms()` and `list_clients(realm)`.
    - It logs in with a dedicated **service account** that only has the `view-*` roles: it cannot change anything.

    **Who is who in this demo:**

    | Role | In this demo |
    |---|---|
    | **Host** | This notebook: the agent (`create_agent` + LLM) |
    | **Client** | `MCPAdapter` (it uses a `fastmcp` client underneath) |
    | **Server** | `keycloak_mcp_server.py`, started as a **subprocess** (stdio), because we pass a `Path(...)` |
    """)
    return


@app.cell
def _():
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv(usecwd=True))  # KEYCLOAK_* settings and the LLM key
    return


@app.cell
def _():
    from pathlib import Path

    from langchain.agents import create_agent
    from langchain.mcp import MCPAdapter

    # MODEL = "anthropic:claude-opus-5-5"
    MODEL = "openai:gpt-5.4-mini"  # cheaper and faster, but a less precise review
    SERVER = Path(__file__).parent / "keycloak_mcp_server.py"
    return MCPAdapter, MODEL, SERVER, create_agent


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 1: connect to the server and discover its tools

    `MCPAdapter` starts the server as a subprocess (stdio), runs `initialize` + `tools/list`
    and converts every MCP tool into a normal LangChain tool.
    """)
    return


@app.cell
async def _(MCPAdapter, SERVER):
    async with MCPAdapter(SERVER) as adapter:
        tools = await adapter.list_tools()

    for tool in tools:
        print(f"{tool.name}: {tool.description}")
        print("  arguments:", tool.args)
    return (tools,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    These are the same kind of objects as our `@tool` functions from section 5.
    The description and the argument schema come **from the server**: the agent code knows nothing about Keycloak.

    ### Step 2: an agent with an expert role
    """)
    return


@app.cell
def _(MODEL, create_agent, tools):
    system_prompt = """You are an expert in Keycloak, OAuth 2.0 and OpenID Connect (OIDC).
    You review client configuration and point out security problems.
    Use the tools to get the data. Never guess: base every finding on data returned by the tools.

    Rules:
    - Skip the built-in clients: account, account-console, admin-cli, broker, realm-management,
      security-admin-console and every '<realm>-realm' client.
    - Empty or missing rootUrl, baseUrl and adminUrl are NOT problems. Never mention them.
    - Plain http:// URLs to localhost or 127.0.0.1 are NOT problems (local development).
    - Report only: wildcard redirect URIs or web origins ('*', '/*'), empty-string entries ([""]),
      and http:// URLs that point to a non-local host.
    - Several post logout redirect URIs in one string separated by '##' is valid.
    - Do not list clients without findings."""

    agent = create_agent(MODEL, tools, system_prompt=system_prompt)
    return (agent,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 3: ask for a review of all realms

    The agent has to find the realms first (`list_realms`), then list the clients of each realm (`list_clients`).
    We never told it that order: it plans the calls itself.
    """)
    return


@app.cell
async def _(agent):
    user_prompt = (
        "List the clients of ALL realms and identify problems in the client configuration "
        "related to 'Access settings' (root URL, home URL, valid redirect URIs, "
        "valid post logout redirect URIs, web origins, admin URL). "
        "Group the findings by realm and client, and give each finding a severity (high / medium / low)."
    )

    result = await agent.ainvoke({"messages": [{"role": "user", "content": user_prompt}]})

    # The tool calls the agent decided to make
    for message in result["messages"]:
        for tool_call in getattr(message, "tool_calls", []):
            print("tool call:", tool_call["name"], tool_call["args"])

    # The expert's report (.text = plain text, without thinking blocks)
    print()
    print(result["messages"][-1].text)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ---
    ### Example result (Claude Opus 5.5)

    ---
    ## heimdall-realm

    ### Client: `cm-infotorg-broker-client` (confidential)
    | # | Setting | Value | Problem | Severity |
    |---|---|---|---|---|
    | 1 | Valid redirect URIs | `["/*"]` | Any path is accepted as a redirect target. Because Root URL is empty, Keycloak checks this relative pattern against its own address, so any path on that host passes. This weakens the main protection against stolen authorization codes and open redirects. List the exact redirect URIs instead. | **High** |
    | 2 | Web origins | `["/*"]` | Wildcard CORS origin. Cross-origin requests from origins you didn't intend to allow may be accepted. List only the specific origins that need access, or use `+` once the redirect URIs are exact. | **Medium** |

    Valid post logout redirect URIs is set to `+`, which means "use the same list as the redirect URIs". So it also allows any path at logout, and fixing #1 fixes it too.

    ---
    ## infotorg-realm

    ### Client: `cm-test-client` (public)
    | # | Setting | Value | Problem | Severity |
    |---|---|---|---|---|
    | 1 | Web origins | `['']` | Contains an empty-string entry. This is a broken or leftover setting with unclear behaviour. Remove it or replace it with the real origin(s). | **Low** |
    | 2 | Valid redirect URIs | `["http://localhost:8080/realms/infotorg-realm/account/*"]` | Ends in a `/*` wildcard. The `http://localhost` part is fine for local development, but any path under `/account/` is accepted on a public client. Narrow it to the exact callback path if you can. | **Low** |

    ### Client: `cm-flask-debug-client`: no findings
    It only uses `localhost` / `127.0.0.1` URLs, and the post logout URIs separated by `##` are valid.

    ---
    ## master

    ### Client: `mcp-demo` (confidential)
    | # | Setting | Value | Problem | Severity |
    |---|---|---|---|---|
    | 1 | Valid redirect URIs | `['']` | Contains an empty-string entry and no real redirect URI. This is a broken setting with unclear behaviour. Set the exact redirect URI(s), or remove the entry if the client doesn't use a browser login. | **Medium** |
    | 2 | Web origins | `['']` | Contains an empty-string entry. Remove it or set the real origin(s). | **Low** |

    ## Summary
    | Realm | Client | High | Medium | Low |
    |---|---|---|---|---|
    | heimdall-realm | cm-infotorg-broker-client | 1 | 1 | 0 |
    | infotorg-realm | cm-test-client | 0 | 0 | 2 |
    | master | mcp-demo | 0 | 1 | 1 |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Read the output above: `list_realms`, then one `list_clients` per realm, then the expert's report.

    **Why this is useful:** the model never had Keycloak credentials. The **MCP server** holds them and exposes only two read-only operations.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## MCP: summary

    - **MCP = a standard plug** between AI apps (clients) and capabilities (servers): N + M instead of N × M.
    - A server exposes **tools** (also resources and prompts); the client **discovers** them with `tools/list`.
    - Transports: **stdio** (local subprocess) and **Streamable HTTP** (remote service).
    - For the LLM an MCP tool looks like any other tool; `MCPAdapter.list_tools()` returns normal LangChain tools.
    - A server is code you run: trust it, give it minimal rights.

    **Demo:** our own read-only MCP server for Keycloak, used by an expert agent.
    """)
    return


if __name__ == "__main__":
    app.run()

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
    # 7. Middleware and human in the loop

    ## Middleware: hooks around model and tool calls
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The problem

    Our support agent (from previous examples) works, but look at what we **cannot control**:

    - It can refund money **without anyone approving it**.
    - It can loop and make **unlimited paid calls**.
    - A failed model call or tool call **breaks the whole run**.
    - Customer data (e-mail, card numbers) flows to the model **unfiltered**.
    - Long conversations grow until they **hit the context limit**.

    We could put `if` statements into every tool and prompt. Middleware is the clean way to do it **once, in one place**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## What is middleware?

    **Middleware = code that runs at fixed points of the agent loop** and can look at, change or stop what is happening.

    Think of **checkpoints on a production line**: the product (the conversation) moves through the same steps, and inspectors at each checkpoint can log it, fix it, reject it or call a manager.

    - It is **not a separate runtime**: hooks run inside the LangGraph that `create_agent` builds.
    - The agent logic stays unchanged. Rules live **next to** the agent, not inside the prompt or tools.
    """),
        mo.hstack(
            [
                mo.image(src=mo.notebook_dir() / "static" / "agent_loop.png", width=300, caption="Agent loop"),
                mo.image(
                    src=mo.notebook_dir() / "static" / "agent_loop_with_middleware.png",
                    width=380,
                    caption="Agent loop with middleware hooks",
                ),
            ],
            justify="center",
            align="start",
            gap=3,
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What is it used for?

    | Goal | Example |
    |---|---|
    | **Safety** | Ask a human before a risky tool runs (HITL), block forbidden actions |
    | **Cost control** | Limit the number of model or tool calls |
    | **Reliability** | Retry failed calls, fall back to another model |
    | **Privacy** | Redact or block e-mails, card numbers, other PII |
    | **Context** | Summarize or trim long history |
    | **Visibility** | Log every model and tool call |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Attaching middleware

    ```python
    from langchain.agents import create_agent
    from langchain.agents.middleware import SummarizationMiddleware, HumanInTheLoopMiddleware

    agent = create_agent(
        model="<provider>:<model-id>",
        tools=[...],
        middleware=[
            SummarizationMiddleware(...),
            HumanInTheLoopMiddleware(...),
        ],
    )
    ```

    One new argument: a **list of middleware** (the order matters, see below). The rest of the agent code stays the same.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Built-in middleware

    Import from `langchain.agents.middleware`.

    | Middleware | What it does |
    |---|---|
    | **`HumanInTheLoopMiddleware`** | Pauses before a tool runs: **approve, edit or reject**. Needs a checkpointer |
    | **`ModelCallLimitMiddleware`** | Caps model calls per run or per thread (`run_limit`, `thread_limit`) |
    | **`ToolCallLimitMiddleware`** | Caps tool calls, globally or for one tool (`tool_name`) |
    | **`ModelRetryMiddleware`** | Retries failed model calls with exponential backoff |
    | **`ToolRetryMiddleware`** | Retries failed tool calls (transient errors) |
    | **`ToolErrorMiddleware`** | Turns tool exceptions into messages the model can read and react to |
    | **`ModelFallbackMiddleware`** | Switches to another model when the first one fails |
    | **`SummarizationMiddleware`** | Compresses old history when it gets close to a token limit |
    | **`ContextEditingMiddleware`** | Clears old tool outputs when the context grows |
    | **`PIIMiddleware`** | Detects PII and `redact`, `mask`, `hash` or `block` it |
    | **`LLMToolSelectorMiddleware`** | Lets a small model pick relevant tools first (useful with 10+ tools) |
    | **`TodoListMiddleware`** | Gives the agent a `write_todos` planning tool |
    | **`ShellToolMiddleware`**, **`FilesystemFileSearchMiddleware`** | Persistent shell session, file search tools |
    | **`LLMToolEmulator`** | Replaces real tools with LLM-generated answers (for testing) |

    Providers also ship their own middleware (e.g. prompt caching, content moderation).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Built-in middleware: configuration at a glance

    ```python
    ModelCallLimitMiddleware(run_limit=5, thread_limit=10, exit_behavior="end")

    ToolCallLimitMiddleware(tool_name="issue_refund", run_limit=1)

    ModelRetryMiddleware(max_retries=3, backoff_factor=2.0)

    PIIMiddleware("email", strategy="redact", apply_to_input=True)

    SummarizationMiddleware(model="<small-model>", trigger=("tokens", 4000), keep=("messages", 20))

    HumanInTheLoopMiddleware(interrupt_on={
        "issue_refund": {"allowed_decisions": ["approve", "edit", "reject"]},
        "get_order_status": False,   # no approval needed
    })
    ```

    - Several middleware can be combined: each one does **one job**.
    - Tools are matched by their `.name` (the function name for `@tool`).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Custom middleware: two kinds of hooks

    | Style | Hooks | What they do |
    |---|---|---|
    | **Node-style** | `before_agent`, `before_model`, `after_model`, `after_agent` | Run at a fixed point. Good for logging, validation, state updates |
    | **Wrap-style** | `wrap_model_call`, `wrap_tool_call` | Receive a `handler` and decide to call it **0, 1 or many times**. Good for retries, caching, blocking a call |

    ### Two ways to write it

    - **Decorator** (`@before_model`, `@wrap_tool_call`, ...): one hook, no configuration.
    - **Class** (`AgentMiddleware`): several hooks or init-time settings (e.g. a limit).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Custom middleware: shape of the code

    ```python
    from langchain.agents.middleware import before_model, wrap_tool_call, AgentState
    from langgraph.runtime import Runtime

    @before_model                                   # node-style: just look
    def log_before(state: AgentState, runtime: Runtime):
        print(f"Calling model with {len(state['messages'])} messages")
        return None                                 # None = change nothing

    @wrap_tool_call                                 # wrap-style: around each tool call
    def log_tool(request, handler):
        print("Tool:", request.tool_call["name"], request.tool_call["args"])
        return handler(request)                     # run the real tool (or skip it!)

    agent = create_agent(model=..., tools=[...], middleware=[log_before, log_tool])
    ```

    - Node-style hooks return a **dict** to update the state (or `None`).
    - Wrap-style hooks return what the handler returns, or **their own result** to short-circuit.
    - `jump_to` (`"end"`, `"model"`, `"tools"`) lets a hook stop the loop early.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Summary

    - **Middleware** = hooks around each model and tool call of the agent loop.
    - One `middleware=[...]` argument adds safety, limits, retries, privacy and context control **without touching tools or prompts**.
    - Use **built-in** middleware first; write **custom** middleware (node-style or wrap-style) for your own rules.
    - Order matters.

    **Next:** human in the loop. We add `HumanInTheLoopMiddleware` to our support agent so that **no refund is paid without approval**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    # Human in the loop (HITL)

    **Goal:** the support agent may investigate on its own, but **no refund is paid without a human decision**.

    `HumanInTheLoopMiddleware` runs *after* the model answers and *before* the tools run. If the model asks for a protected tool, the agent **pauses** and waits.

    | Decision | What happens |
    |---|---|
    | **approve** | The tool runs exactly as the model asked |
    | **edit** | The tool runs with arguments changed by the human |
    | **reject** | The tool does **not** run. The model gets the reason and can react |

    **Requirements:** a **checkpointer** (the paused state must be saved) and a **`thread_id`** (to resume the same conversation).
    """),
        mo.mermaid(r"""
    sequenceDiagram
        participant A as Agent
        participant H as Human
        participant T as issue_refund
        A->>A: get_order_status, get_bank_payments (no approval needed)
        A->>H: PAUSE: issue_refund(4821, 1200 NOK)?
        alt approve
            H->>T: run as requested
        else edit
            H->>T: run with changed arguments
        else reject
            H-->>A: "denied" (tool not run)
        end
        A->>A: final answer
    """),
    ])
    return


@app.cell
def _():
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv(usecwd=True))  # load API keys from .env
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Two things we need: `checkpointer` and `config`

    **Checkpointer** = the agent's **save game**.

    - When the agent pauses, its whole state (messages, tool calls) is **saved** by the checkpointer.
    - When the human decides, the agent **loads** it and continues exactly where it stopped.
    - Here we use `InMemorySaver` (RAM, lost when the program ends). In production: a database.
    - Checkpointers are also the base of **memory** and **time travel**. We will spend more time on them later in the talk.

    **Config** = the **label of the save slot**.

    ```python
    config = {"configurable": {"thread_id": "case-4821"}}
    ```

    - `thread_id` identifies **one conversation**. The same `thread_id` = continue the same saved state, a new one = a fresh start.
    - We pass the same `config` when we **start** the agent and when we **resume** it.
    """)
    return


@app.cell
def _():
    from langchain.agents import create_agent
    from langchain.agents.middleware import HumanInTheLoopMiddleware
    from langchain.messages import HumanMessage
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.types import Command
    from support_tools import SYSTEM_PROMPT, TOOLS, USER_MESSAGE

    MODEL = "openai:gpt-5.4-mini"
    return (
        Command,
        HumanInTheLoopMiddleware,
        HumanMessage,
        InMemorySaver,
        MODEL,
        SYSTEM_PROMPT,
        TOOLS,
        USER_MESSAGE,
        create_agent,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Agent 1: the human approves, the customer gets a **100% refund**

    ### Step 1: create the agent
    """)
    return


@app.cell
def _(
    HumanInTheLoopMiddleware,
    InMemorySaver,
    MODEL,
    SYSTEM_PROMPT,
    TOOLS,
    create_agent,
):
    agent_1 = create_agent(
        model=MODEL,
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "issue_refund": {"allowed_decisions": ["approve", "edit", "reject"]},
                    "get_order_status": False,  # read-only: no approval
                    "get_bank_payments": False,  # read-only: no approval
                },
            ),
        ],
        checkpointer=InMemorySaver(),  # agent 1 has its own save game
    )

    config_1 = {"configurable": {"thread_id": "agent-1"}}  # and its own save slot
    return agent_1, config_1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 2: run it. The agent investigates, then **pauses** before the refund
    """)
    return


@app.cell
def _(HumanMessage, USER_MESSAGE, agent_1, config_1):
    result_1 = agent_1.invoke(
        {"messages": [HumanMessage(USER_MESSAGE)]},
        config=config_1,
        version="v2",
    )

    print("Paused:", len(result_1.interrupts) > 0)
    print("Waiting for approval:", result_1.interrupts[0].value["action_requests"])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 3: the human decides: **approve**

    Same `config` = the same saved conversation.

    ### What is `Command`?

    ```python
    from langgraph.types import Command
    ```

    - Normally we call the agent with **new input** (a message).
    - `Command` is a different kind of input: **an instruction for the paused agent**, not a new message.
    - `Command(resume=...)` means: *"continue from the pause, and here is the answer to the question you asked"*.
    - Here the answer is the human's decision:

    ```python
    Command(resume={"decisions": [{"type": "approve"}]})
    ```

    - `decisions` is a list with **one decision per pending action**, in the same order as in `action_requests`.
    - `Command` can do more in LangGraph (for example update the state or jump to another node). We will see it again later.
    """)
    return


@app.cell
def _(Command, agent_1, config_1):
    resumed_1 = agent_1.invoke(
        Command(resume={"decisions": [{"type": "approve"}]}),
        config=config_1,
        version="v2",
    )

    print("Tool result:", resumed_1.value["messages"][-2].content)
    print()
    print("Final answer:", resumed_1.value["messages"][-1].text)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Agent 2: the human rejects, **no refund**, the case goes to further investigation

    A completely separate agent: its own checkpointer, its own `config`. It knows nothing about agent 1.

    ### Step 1: create the agent
    """)
    return


@app.cell
def _(
    HumanInTheLoopMiddleware,
    InMemorySaver,
    MODEL,
    SYSTEM_PROMPT,
    TOOLS,
    create_agent,
):
    agent_2 = create_agent(
        model=MODEL,
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "issue_refund": {"allowed_decisions": ["approve", "edit", "reject"]},
                    "get_order_status": False,  # read-only: no approval
                    "get_bank_payments": False,  # read-only: no approval
                },
            ),
        ],
        checkpointer=InMemorySaver(),  # agent 2 has its own save game
    )

    config_2 = {"configurable": {"thread_id": "agent-2"}}  # and its own save slot
    return agent_2, config_2


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 2: run it. Again the agent **pauses** before the refund
    """)
    return


@app.cell
def _(HumanMessage, USER_MESSAGE, agent_2, config_2):
    result_2 = agent_2.invoke(
        {"messages": [HumanMessage(USER_MESSAGE)]},
        config=config_2,
        version="v2",
    )

    print("Paused:", len(result_2.interrupts) > 0)
    print("Waiting for approval:", result_2.interrupts[0].value["action_requests"])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 3: the human decides: **reject**

    The refund tool does **not** run. Our message goes back to the model, which passes the case on.
    """)
    return


@app.cell
def _(Command, agent_2, config_2):
    resumed_2 = agent_2.invoke(
        Command(
            resume={
                "decisions": [
                    {
                        "type": "reject",
                        "message": (
                            "Refund not approved. Do not retry. Set the case status to "
                            "'under investigation' and tell the customer it was passed on for further investigation."
                        ),
                    }
                ]
            }
        ),
        config=config_2,
        version="v2",
    )

    print("Tool result:", resumed_2.value["messages"][-2].content)
    print()
    print("Final answer:", resumed_2.value["messages"][-1].text)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## HITL: summary

    - **One middleware, one config** (`interrupt_on`): choose which tools need approval and which decisions are allowed.
    - The agent **pauses** (state saved by the checkpointer) and **resumes** with `Command(resume={"decisions": [...]})`, one decision per pending action.
    - **approve / edit / reject**: reject sends your reason back to the model.
    - Read-only tools run freely, **risky tools wait for a human**.

    **In production:**

    - Use a **persistent checkpointer** (e.g. Postgres) instead of `InMemorySaver`: the human may answer minutes or days later, even after a restart.
    - The "human" is usually a **UI** (an approval inbox, Slack message, Agent Chat UI), not Python code.
    - Interrupt only when needed: `when=` lets you pause for risky arguments only (e.g. refunds above 1000 NOK).
    - Keep the **audit trail**: who approved what, and when.
    """)
    return


if __name__ == "__main__":
    app.run()

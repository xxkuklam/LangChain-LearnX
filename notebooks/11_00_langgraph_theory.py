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
    # 11. LangGraph

    ## Workflows as graphs: full control over the flow
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## LangChain vs. LangGraph: a quick recap

    | | **LangChain** | **LangGraph** |
    |---|---|---|
    | **What it is** | High-level toolbox | Low-level orchestration framework and runtime |
    | **Main question** | "Which model, tools and prompt?" | "In which order, under which conditions, with what state?" |
    | **You write** | `create_agent(model, tools, ...)` | Nodes, edges and state |
    | **Who decides the next step** | The **model** (the agent loop) | **You**, the model, or both |
    | **Good for** | Getting an agent running in minutes | Workflows with branches, loops, parallel work, approvals |
    | **Analogy** | A ready-made **car** | The **engine and chassis** to build your own vehicle |
    """)
    return


@app.cell(hide_code=True, expand_output=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## They are not competitors: LangChain runs on LangGraph

    - `init_chat_model`, tools, messages, middleware: the **building blocks** (LangChain).
    - `create_agent`: a **ready-made graph** built from those blocks.
    - LangGraph underneath provides the **runtime**: state, persistence (checkpointers), streaming, interrupts.

    We have used LangGraph all along: the `thread_id`, the checkpointer and the human-in-the-loop pause all came from it.
    """),
        mo.mermaid(
            """
            flowchart TB
                subgraph LC["LangChain: high-level, fast start"]
                    A["create_agent"]
                    B["init_chat_model"]
                    C["tools, middleware, messages"]
                end
                subgraph LG["LangGraph: runtime and low-level API"]
                    D["StateGraph: state, nodes, edges"]
                    E["checkpointers (persistence)"]
                    F["streaming"]
                    G["interrupts (human in the loop)"]
                end
                A -->|"builds"| D
                B -.->|"used inside nodes"| D
                C -.->|"used inside nodes"| D
                D --- E
                D --- F
                D --- G
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## `create_agent` is a graph

    The agent loop from the ReAct section is a small graph with two nodes and a loop.
    With `create_agent` this graph is built **for you**. With LangGraph you can build **your own**.

    Both return the **same type**: `create_agent(...)` and `builder.compile()` give a `CompiledStateGraph`, so `invoke`, `stream`, `get_state` and `get_graph()` work identically. Only the state differs (`messages` for the agent, your own keys for a custom graph).
    """),
        mo.mermaid(
            """
            flowchart LR
                S(["START"]) --> M["model"]
                M -->|"tool calls?"| T["tools"]
                T --> M
                M -->|"no tool calls"| E(["END"])
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## The idea of LangGraph: a flowchart that runs

    Think of a **flowchart on a whiteboard**: boxes (steps) and arrows (what happens next).
    LangGraph turns that drawing into a **program**.

    - Every box is a **node**: a normal Python function.
    - Every arrow is an **edge**: "go there next", or "go there **if** this condition holds".
    - Everybody works on one shared **state** (think of a clipboard passed along the line).

    A step can call an LLM, a tool, a database, or just plain Python. The graph does not care.
    """),
        mo.mermaid(
            """
            flowchart LR
                S(["START"]) --> C["classify the ticket<br/>(LLM)"]
                C -->|"billing"| B["check the invoice<br/>(tool)"]
                C -->|"technical"| T["search the knowledge base<br/>(RAG)"]
                C -->|"complaint"| H["escalate to a human"]
                B --> R["write the reply<br/>(LLM)"]
                T --> R
                H --> E(["END"])
                R --> E
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The three building blocks

    | Block | What it is | In code |
    |---|---|---|
    | **State** | The shared data: everything the workflow knows right now | A `TypedDict` (or dataclass / Pydantic model) |
    | **Node** | One step: reads the state, returns **what changed** | A function `def my_node(state) -> dict` |
    | **Edge** | What runs next | `add_edge(a, b)` or `add_conditional_edges(a, router)` |

    Plus two special markers: **`START`** (entry point) and **`END`** (finish).

    The rule that makes it work: a node **never edits the state directly**. It returns a **partial update**, and LangGraph merges it into the state.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## State and reducers

    ```python
    from typing_extensions import TypedDict

    class State(TypedDict):
        question: str
        category: str
        answer: str
    ```

    - Each key is a **channel**. A node returns only the keys it wants to change: `{"category": "billing"}`.
    - By default the new value **replaces** the old one.
    - A **reducer** changes how updates are merged. The classic case is a list that should **grow**:

    ```python
    from operator import add
    from typing import Annotated
    from langgraph.graph.message import add_messages

    class State(TypedDict):
        steps: Annotated[list[str], add]                      # new items are appended
        messages: Annotated[list[AnyMessage], add_messages]   # appended and merged by message id
    ```

    `MessagesState` is a ready-made state with a `messages` key and the `add_messages` reducer. It is what agents use.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## Reducers in pictures

    Two nodes both write to the same key. What is in the state afterwards?

    | Key | Reducer | Node A returns | Node B returns | Result |
    |---|---|---|---|---|
    | `category` | none (replace) | `"billing"` | `"urgent"` | `"urgent"` (the last write wins) |
    | `steps` | `add` (append) | `["classified"]` | `["replied"]` | `["classified", "replied"]` |

    Without a reducer, **parallel nodes writing to the same key** would be a conflict. With a reducer their results are combined. We use this in the parallelization and map-reduce examples.
    """),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Nodes and edges in code

    ```python
    from langgraph.graph import StateGraph, START, END

    def classify(state: State) -> dict:                 # a node: state in, partial update out
        return {"category": "billing"}

    def reply(state: State) -> dict:
        return {"answer": f"Reply about {state['category']}"}

    def route(state: State) -> str:                     # a router: returns the name of the next node
        return "reply" if state["category"] == "billing" else END

    builder = StateGraph(State)                         # 1. describe the graph
    builder.add_node("classify", classify)
    builder.add_node("reply", reply)
    builder.add_edge(START, "classify")
    builder.add_conditional_edges("classify", route)    # a fork decided by code

    graph = builder.compile()                           # 2. compile

    graph.invoke({"question": "Where is my invoice?"})  # 3. run -> the final state
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## Edge types

    | Edge | Code | Meaning |
    |---|---|---|
    | **Normal** | `add_edge("a", "b")` | After `a` always go to `b` |
    | **Conditional** | `add_conditional_edges("a", router)` | A function looks at the state and picks the next node |
    | **Entry / exit** | `add_edge(START, "a")`, `add_edge("b", END)` | Where the graph starts and ends |
    | **Fan-out** | Two edges from one node | The targets run **in parallel** |
    | **`Send`** | Return `[Send("node", input), ...]` from a router | Run a node **once per item** (map-reduce) |
    | **`Command`** | A node returns `Command(update=..., goto=...)` | Update the state **and** choose the next node in one step |

    The router can be anything: an `if` on the state, or a call to an LLM. **That is the knob between "code decides" and "model decides".**
    """),
        mo.mermaid(
            """
            flowchart LR
                A["a"] --> B["b"]
                B --> R{"router(state)"}
                R -->|"x"| C["c"]
                R -->|"y"| D["d"]
                B -.-> P1["parallel 1"]
                B -.-> P2["parallel 2"]
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## How a graph runs

    1. **Build**: `StateGraph(State)`, `add_node`, `add_edge`.
    2. **Compile**: `builder.compile()` checks the graph and returns a runnable object. Optional: `checkpointer=`.
    3. **Invoke**: `graph.invoke(input)` returns the **final state**. Also `stream`, `ainvoke`, `astream`, like every Runnable.

    Under the hood the graph runs in **steps** (super-steps): in each step all nodes that are ready run, **in parallel**, and their updates are merged before the next step.
    The `recursion_limit` (a config key) stops runaway loops: too many steps raises `GraphRecursionError`.
    """),
        mo.mermaid(
            """
            flowchart LR
                B["Build<br/>StateGraph + nodes + edges"] --> C["Compile<br/>validate, add checkpointer"]
                C --> I["Invoke<br/>input state"]
                I --> S1["Step 1<br/>run ready nodes"]
                S1 --> S2["Step 2<br/>merge updates, next nodes"]
                S2 --> SN["..."]
                SN --> O["Final state"]
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What the LangGraph runtime gives you

    Because the whole workflow is an explicit graph with an explicit state, the runtime can offer a lot **for free**:

    | Feature | What it does | Where we use it |
    |---|---|---|
    | **Persistence** | A checkpointer saves the state after every step | Memory section, `thread_id` |
    | **Human in the loop** | `interrupt()` pauses the graph, you resume later with `Command(resume=...)` | Approval of a refund |
    | **Streaming** | Watch every node, update or token as it happens | Progress in the UI |
    | **Durable execution** | After a crash the run continues from the last checkpoint | Long jobs |
    | **Time travel** | Go back to an earlier checkpoint and replay or branch | Debugging |
    | **Subgraphs** | A compiled graph used as a node of another graph | Splitting big workflows |
    | **Parallelism** | Independent nodes run at the same time | Faster answers |
    | **Runtime context** | Pass config (user id, model name) that is not part of the state | Multi-user apps |
    | **Observability** | Every step is traced in LangSmith; LangGraph Studio shows the graph | Debugging, demos |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## When to use what

    **Start simple. Move down only when you need to.**
    """),
        mo.mermaid(
            """
            flowchart TD
                Q1{"One LLM call,<br/>no tools?"} -->|"yes"| A["init_chat_model<br/>(+ structured output)"]
                Q1 -->|"no"| Q2{"The model should decide<br/>which tools to call, in a loop?"}
                Q2 -->|"yes"| Q3{"Standard loop is enough?<br/>(+ middleware, memory, HITL)"}
                Q3 -->|"yes"| B["create_agent"]
                Q3 -->|"no"| D["LangGraph"]
                Q2 -->|"no, the steps are known"| Q4{"Branches, loops, parallel work,<br/>approvals, several agents?"}
                Q4 -->|"yes"| D
                Q4 -->|"no, a straight line"| E["plain Python<br/>(or a simple chain)"]
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Use LangChain (`create_agent`, `init_chat_model`) when...

    - You need **one model call**, or a **standard tool-using agent**.
    - The model should **decide freely** which tools to use and when to stop.
    - You are **prototyping** and want results in minutes.
    - Customising with **middleware** (approvals, summarisation, retries, limits) is enough.

    ## Use LangGraph when...

    - The process has **known steps** and **business rules** that must be followed in a fixed order.
    - You need **branches, loops, parallel work** or **map-reduce** over a list.
    - **Several agents or steps** cooperate and share a state.
    - You want an **explicit, drawable, testable** flow that people other than the author can read.
    - You need **approvals**, **long-running** jobs, **resume after failure** or full control over **what is saved**.
    - Part of the work is **deterministic code** and only part needs an LLM.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Pros and cons

    | | **LangChain** (`create_agent`) | **LangGraph** (`StateGraph`) |
    |---|---|---|
    | **Pros** | Few lines of code | Full control of the flow |
    | | Quick to learn and to change | Predictable: the path is in the graph, not only in the prompt |
    | | Sensible defaults (loop, state, tools) | Mix code and LLM steps freely |
    | | Middleware for common needs | Branches, loops, parallelism, subgraphs |
    | | | Easy to **draw, test and debug** node by node |
    | **Cons** | Less control: the model decides the path | More code and more concepts (state, reducers, edges) |
    | | Hard to enforce a strict order of steps | You design the architecture yourself |
    | | Harder to debug when the agent "wanders" | Easy to over-engineer a task that is a simple agent |
    | **Risk** | Unpredictable cost and path | Rigid graphs: a new case means a new node |

    **Rule of thumb:** the more you can describe the process as a flowchart in advance, the more LangGraph pays off.
    The more open-ended the task, the more a plain agent fits.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## Workflow vs. agent, again

    The first slide of this talk asked: **who decides the next step, our code or the model?**
    LangGraph lets you choose **per step**:

    | | Workflow | Agent | In LangGraph |
    |---|---|---|---|
    | Next step | Fixed by our code | Chosen by the model | Both in one graph |
    | Example | Classify, then always reply | The model picks tools in a loop | Fixed classification, then an agent node for the hard cases |

    Real systems are usually **hybrids**: a deterministic skeleton with agents (or LLM calls) in a few nodes.
    """),
        mo.mermaid(
            """
            flowchart LR
                S(["START"]) --> C["classify<br/>(plain code)"]
                C -->|"simple"| F["fixed reply<br/>(LLM call)"]
                C -->|"hard"| A["agent node<br/>(create_agent)"]
                F --> E(["END"])
                A --> E
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Combining both worlds

    - **An agent as a node.** A compiled `create_agent` graph can be used as a node (or a subgraph) in a bigger graph.
    - **LangChain parts inside nodes.** `init_chat_model`, tools, structured output and retrievers are the normal way to do work *inside* a node.
    - **A graph as a tool.** A whole graph can be wrapped in a `@tool`, so another agent can call it.
    - **The same extras everywhere.** Checkpointers, streaming, LangSmith and human-in-the-loop work the same for agents and for hand-made graphs.

    You do not choose once for the whole project. You choose **per problem**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Good to know before we build

    - **A node returns a partial update**, never the whole state, and never mutates the input.
    - **Reducers matter** as soon as two nodes write to the same key, or a loop appends to a list.
    - **Loops need an exit.** Always have a condition that leads to `END`, and keep `recursion_limit` as a safety net.
    - **Keep nodes small.** One responsibility per node: easier to test, to trace and to reuse.
    - **Idempotent side effects.** After an interrupt or a retry a node starts again from the top: sending an e-mail twice is a bug.
    - **Type the router's return** (`Literal["a", "b"]`): the graph can then be drawn correctly.
    - **Draw the graph.** `graph.get_graph().draw_mermaid()` gives a diagram you can put on a slide, and we will do that in every example.
    - **You do not need LangGraph for everything.** A simple agent that works is better than a graph nobody can maintain.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## LangGraph: theory recap

    - **LangChain = building blocks and ready-made agents. LangGraph = the runtime and the low-level API to build your own flows.**
    - `create_agent` **is** a LangGraph graph, so you can always go one level deeper.
    - A graph = **State** (shared data) + **Nodes** (functions returning partial updates) + **Edges** (fixed, conditional, parallel).
    - **Reducers** define how updates are merged (replace or append).
    - Build, **compile**, **invoke**; the runtime adds persistence, streaming, interrupts and tracing.
    - Choose by control: **open-ended task = agent, known process = graph, hybrids are common**.

    **In this section we build (one notebook per example, `11_NN_langgraph_...`):**

    1. State, nodes and edges: the first graph
    2. Conditions and routing
    3. A pipeline of LLM nodes
    4. A loop: write and critique
    5. Generate and validate (LLM plus business rules)
    6. Parallelization
    7. Map-reduce with `Send`
    8. Subgraphs
    9. An agent as a graph
    10. Human in the loop with `interrupt` (planned)
    11. LangGraph Studio (planned)
    """)
    return


if __name__ == "__main__":
    app.run()

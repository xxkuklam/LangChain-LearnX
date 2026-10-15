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
    # 9. LangGraph

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

    **In this section we build:**

    1. State, nodes and edges: the first graph
    2. Conditions and routing
    3. Parallelization
    4. Map-reduce
    5. Subgraphs
    6. An agent as a graph
    7. Human in the loop with `interrupt`
    8. LangGraph Studio
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Example 1: the first graph

    The smallest graph that shows all the pieces: **state, two nodes, one edge, one conditional edge**.
    No LLM yet, only plain Python, so we see exactly what LangGraph does.

    ```text
    START -> classify -> (router) -> reply -> END
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 1: the state
    """)
    return


@app.cell
def _():
    from typing import Literal

    from typing_extensions import TypedDict

    from langgraph.graph import END, START, StateGraph


    class State(TypedDict):
        question: str
        category: str
        answer: str

    return END, Literal, START, State, StateGraph, TypedDict


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 2: the nodes and the router

    - A **node** gets the state and returns **only what it changes**.
    - A **router** gets the state and returns **the name of the next node**.
    """)
    return


@app.cell
def _(END, Literal, State):
    def classify(state: State) -> dict:  # a node: state in, partial update out
        return {"category": "billing"}


    def reply(state: State) -> dict:
        return {"answer": f"Reply about {state['category']}"}


    def route(state: State) -> Literal["reply", "__end__"]:  # a router: the name of the next node
        return "reply" if state["category"] == "billing" else END

    return classify, reply, route


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 3: build and compile the graph
    """)
    return


@app.cell
def _(START, State, StateGraph, classify, reply, route):
    builder = StateGraph(State)  # 1. describe the graph
    builder.add_node("classify", classify)
    builder.add_node("reply", reply)
    builder.add_edge(START, "classify")
    builder.add_conditional_edges("classify", route)  # a fork decided by code

    graph = builder.compile()  # 2. compile

    print(type(graph))
    return (graph,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 4: draw the graph

    The router's return type (`Literal[...]`) tells LangGraph where the fork can lead, so the diagram is correct.
    """)
    return


@app.cell
def _(graph, mo):
    mo.mermaid(graph.get_graph().draw_mermaid())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 5: run it

    `invoke` takes the **initial state** (only `question`) and returns the **final state**: all three keys.
    """)
    return


@app.cell
def _(graph):
    result_1 = graph.invoke({"question": "Where is my invoice?"})

    print(result_1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Read it as a story: `classify` added `category`, then the router picked `reply`, which added `answer`. `question` stayed untouched.

    ## The same type: `create_agent` vs. our graph

    Now an agent made with `create_agent` (no tools, we only want the object).
    """)
    return


@app.cell
def _():
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv(usecwd=True))  # API key from .env
    return


@app.cell
def _():
    from langchain.agents import create_agent

    MODEL = "openai:gpt-5.4-mini"

    agent = create_agent(MODEL, tools=[])
    return MODEL, agent


@app.cell
def _(agent, graph):
    print("our graph:  ", type(graph))
    print("the agent:  ", type(agent))
    print()
    print("the same class?", type(graph) is type(agent))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Same class: `CompiledStateGraph`.** An agent is just a graph that someone else built for us.
    So everything we know about graphs works for agents: `invoke`, `stream`, `get_state`, `get_graph()`.

    #### The agent drawn like our graph
    """)
    return


@app.cell
def _(agent, mo):
    mo.mermaid(agent.get_graph().draw_mermaid())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Different state, different input and output

    | | Our graph | The agent |
    |---|---|---|
    | State schema | `question`, `category`, `answer` | `messages` |
    | Input | `{"question": "..."}` | `{"messages": [...]}` |
    | Output | the three keys | `{"messages": [...]}` |
    """)
    return


@app.cell
def _(agent):
    result_2 = agent.invoke({"messages": [{"role": "user", "content": "Say hello in one word."}]})

    print("keys of the final state:", list(result_2.keys()))
    print("last message:", result_2["messages"][-1].text)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Example 2: conditions and routing

    A real fork: a support ticket goes to a **different branch** depending on its category.

    ```text
    START -> classify -> billing_reply   -> END
                      -> technical_reply -> END
                      -> escalate        -> END
    ```

    We build the same graph three times. Only **who decides** changes:

    1. **Rules** (plain Python): fast, free, predictable.
    2. **An LLM** classifies, the router is still code.
    3. **`Command`**: the node itself says where to go next.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Version 1: the decision is made by rules
    """)
    return


@app.cell
def _(Literal, TypedDict):
    class TicketState(TypedDict):
        question: str
        category: str
        answer: str


    def classify_rules(state: TicketState) -> dict:
        text = state["question"].lower()
        if "invoice" in text or "refund" in text or "payment" in text:
            return {"category": "billing"}
        if "error" in text or "crash" in text or "not working" in text:
            return {"category": "technical"}
        return {"category": "other"}


    def billing_reply(state: TicketState) -> dict:
        return {"answer": "Billing team: we will check your invoice and payments."}


    def technical_reply(state: TicketState) -> dict:
        return {"answer": "Support team: please send us the error message and your app version."}


    def escalate(state: TicketState) -> dict:
        return {"answer": "A human agent will contact you today."}


    def route_by_category(state: TicketState) -> Literal["billing_reply", "technical_reply", "escalate"]:
        if state["category"] == "billing":
            return "billing_reply"
        if state["category"] == "technical":
            return "technical_reply"
        return "escalate"

    return (
        TicketState,
        billing_reply,
        classify_rules,
        escalate,
        route_by_category,
        technical_reply,
    )


@app.cell
def _(
    END,
    START,
    StateGraph,
    TicketState,
    billing_reply,
    classify_rules,
    escalate,
    route_by_category,
    technical_reply,
):
    builder_rules = StateGraph(TicketState)
    builder_rules.add_node("classify", classify_rules)
    builder_rules.add_node("billing_reply", billing_reply)
    builder_rules.add_node("technical_reply", technical_reply)
    builder_rules.add_node("escalate", escalate)

    builder_rules.add_edge(START, "classify")
    builder_rules.add_conditional_edges("classify", route_by_category)
    builder_rules.add_edge("billing_reply", END)
    builder_rules.add_edge("technical_reply", END)
    builder_rules.add_edge("escalate", END)

    graph_rules = builder_rules.compile()
    return (graph_rules,)


@app.cell
def _(graph_rules, mo):
    mo.mermaid(graph_rules.get_graph().draw_mermaid())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Three tickets, the same graph, three different paths:
    """)
    return


@app.cell
def _(graph_rules):
    result_3 = graph_rules.invoke({"question": "Where is my invoice?"})
    print(result_3["category"], "->", result_3["answer"])

    result_4 = graph_rules.invoke({"question": "The app crashes with an error"})
    print(result_4["category"], "->", result_4["answer"])

    result_5 = graph_rules.invoke({"question": "My anti-gravity boots flew away!"})
    print(result_5["category"], "->", result_5["answer"])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Keywords are fast and free, but brittle: "I was charged twice" has none of our words and goes to a human.

    ### Version 2: an LLM classifies, the code still routes

    Only the `classify` node changes: it asks a model for the category (structured output, like in section 3).
    The other nodes, the router and the edges are **exactly the same**.
    """)
    return


@app.cell
def _(Literal, MODEL, TicketState):
    from langchain.chat_models import init_chat_model
    from pydantic import BaseModel


    class Category(BaseModel):
        category: Literal["billing", "technical", "other"]


    model_classifier = init_chat_model(MODEL).with_structured_output(Category)


    def classify_llm(state: TicketState) -> dict:
        result = model_classifier.invoke(
            "Classify this support ticket as billing, technical or other: " + state["question"]
        )
        return {"category": result.category}

    return Category, classify_llm, init_chat_model


@app.cell
def _(
    END,
    START,
    StateGraph,
    TicketState,
    billing_reply,
    classify_llm,
    escalate,
    route_by_category,
    technical_reply,
):
    builder_llm = StateGraph(TicketState)
    builder_llm.add_node("classify", classify_llm)  # the only difference
    builder_llm.add_node("billing_reply", billing_reply)
    builder_llm.add_node("technical_reply", technical_reply)
    builder_llm.add_node("escalate", escalate)

    builder_llm.add_edge(START, "classify")
    builder_llm.add_conditional_edges("classify", route_by_category)
    builder_llm.add_edge("billing_reply", END)
    builder_llm.add_edge("technical_reply", END)
    builder_llm.add_edge("escalate", END)

    graph_llm = builder_llm.compile()
    return (graph_llm,)


@app.cell
def _(graph_llm):
    result_6 = graph_llm.invoke({"question": "I was charged twice for the same order"})
    print(result_6["category"], "->", result_6["answer"])

    result_7 = graph_llm.invoke({"question": "The app is not working since the update"})
    print(result_7["category"], "->", result_7["answer"])

    result_8 = graph_llm.invoke({"question": "My anti-gravity boots flew away!"})
    print(result_8["category"], "->", result_8["answer"])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The LLM understood "charged twice" without any keyword. We gained flexibility and paid with one model call and a little unpredictability.

    **The pattern:** the LLM does the *understanding*, the code does the *deciding* what happens next. The path stays under our control.

    ### Version 3: `Command`: the node chooses the next step

    Instead of a separate router, a node can return a **`Command`**: a state update **and** the name of the next node in one object.
    """)
    return


@app.cell
def _(Literal, TicketState):
    from langgraph.types import Command


    def classify_command(state: TicketState) -> Command[Literal["billing_reply", "technical_reply", "escalate"]]:
        text = state["question"].lower()
        if "invoice" in text or "refund" in text or "payment" in text:
            return Command(update={"category": "billing"}, goto="billing_reply")
        if "error" in text or "crash" in text or "not working" in text:
            return Command(update={"category": "technical"}, goto="technical_reply")
        return Command(update={"category": "other"}, goto="escalate")

    return (classify_command,)


@app.cell
def _(
    END,
    START,
    StateGraph,
    TicketState,
    billing_reply,
    classify_command,
    escalate,
    technical_reply,
):
    builder_command = StateGraph(TicketState)
    builder_command.add_node("classify", classify_command)
    builder_command.add_node("billing_reply", billing_reply)
    builder_command.add_node("technical_reply", technical_reply)
    builder_command.add_node("escalate", escalate)

    builder_command.add_edge(START, "classify")  # no add_conditional_edges: the Command decides
    builder_command.add_edge("billing_reply", END)
    builder_command.add_edge("technical_reply", END)
    builder_command.add_edge("escalate", END)

    graph_command = builder_command.compile()
    return (graph_command,)


@app.cell
def _(graph_command, mo):
    mo.mermaid(graph_command.get_graph().draw_mermaid())
    return


@app.cell
def _(graph_command):
    result_9 = graph_command.invoke({"question": "I need a refund"})
    print(result_9["category"], "->", result_9["answer"])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The diagram is the same. `Command` needs the **return annotation** (`Command[Literal[...]]`) so that LangGraph can draw the possible paths.

    #### Router function or `Command`?

    | | **Router** (`add_conditional_edges`) | **`Command`** (`goto`) |
    |---|---|---|
    | Where is the decision | In a separate function | Inside the node, next to the work |
    | State update | The node returns it, the router only reads | One object: update **and** goto |
    | Reuse | One router for many nodes | Each node decides for itself |
    | Pick it when | The routing logic is separate and reusable | The node already knows the answer (e.g. an LLM decided) |

    Do not use both on the same node: choose one way of routing per node.

    ### Routing: summary

    - A **conditional edge** = a function that reads the state and returns the next node.
    - Annotate the return type with `Literal[...]`: the graph can then be drawn correctly.
    - The decision can be **rules, an LLM, or both**: LLM understands, code decides.
    - **`Command(update=..., goto=...)`** puts the update and the routing into the node.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Example 3: a graph with real LLM calls (pipeline)

    `START -> summarize -> classify -> draft_reply -> END`: three LLM nodes, each with its own prompt.
    **Notice:** every node reads what the previous ones wrote to the state and adds one key (`summary`, `category`, `reply`).
    """)
    return


@app.cell
def _(Category, END, MODEL, START, StateGraph, TypedDict, init_chat_model, mo):
    llm = init_chat_model(MODEL)


    class PipelineState(TypedDict):
        ticket: str
        summary: str
        category: str
        reply: str


    def summarize_ticket(state: PipelineState) -> dict:
        response = llm.invoke("Summarize this support ticket in one sentence: " + state["ticket"])
        return {"summary": response.text}


    def classify_ticket(state: PipelineState) -> dict:
        result = llm.with_structured_output(Category).invoke("Classify this ticket: " + state["summary"])
        return {"category": result.category}


    def draft_reply(state: PipelineState) -> dict:
        response = llm.invoke(
            f"Write a polite reply (max 3 sentences) to a {state['category']} ticket. Ticket summary: {state['summary']}"
        )
        return {"reply": response.text}


    builder_pipeline = StateGraph(PipelineState)
    builder_pipeline.add_node("summarize", summarize_ticket)
    builder_pipeline.add_node("classify", classify_ticket)
    builder_pipeline.add_node("draft_reply", draft_reply)
    builder_pipeline.add_edge(START, "summarize")
    builder_pipeline.add_edge("summarize", "classify")
    builder_pipeline.add_edge("classify", "draft_reply")
    builder_pipeline.add_edge("draft_reply", END)
    graph_pipeline = builder_pipeline.compile()

    result_10 = graph_pipeline.invoke({
        "ticket": "Hello, two weeks ago I ordered the anti-gravity boots and my card was charged twice (1299 USD each time). "
        "I received only one pair. Please fix this as soon as possible."
    })
    print("SUMMARY: ", result_10["summary"])
    print("CATEGORY:", result_10["category"])
    print("REPLY:   ", result_10["reply"])

    mo.mermaid(graph_pipeline.get_graph().draw_mermaid())
    return (llm,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Example 4: a loop (write and critique)

    `write -> critique -> (not approved? back to write) -> END`.
    **Notice:** the critic is a second LLM call that returns a structured verdict; the router sends the flow back to `write`
    with the feedback, and a **counter** stops the loop after 3 attempts (no infinite loops).
    """)
    return


@app.cell
def _(END, Literal, START, StateGraph, TypedDict, llm, mo):
    from pydantic import BaseModel as _BaseModel


    class Review(_BaseModel):
        approved: bool
        feedback: str


    class LoopState(TypedDict):
        draft: str
        feedback: str
        attempts: int


    def write_slogan(state: LoopState) -> dict:
        prompt = "Write ONE slogan for ACME anti-gravity boots. Return only the slogan."
        if state["feedback"]:
            prompt += f" Your previous slogan was '{state['draft']}'. Fix it: {state['feedback']}"
        slogan = llm.invoke(prompt).text
        print(f"[write] attempt {state['attempts'] + 1}: {slogan}")
        return {"draft": slogan, "attempts": state["attempts"] + 1}


    def critique_slogan(state: LoopState) -> dict:
        review = llm.with_structured_output(Review).invoke(
            "Review this slogan. Rules: at most 4 words, contains the word 'gravity', no comma. "
            f"Approve only if ALL rules hold. Slogan: {state['draft']}"
        )
        print(f"[critique] approved={review.approved} | {review.feedback}")
        return {"feedback": "" if review.approved else review.feedback}


    def route_after_critique(state: LoopState) -> Literal["write", "__end__"]:
        if state["feedback"] == "" or state["attempts"] >= 3:  # approved, or out of attempts
            return END
        return "write"


    builder_loop = StateGraph(LoopState)
    builder_loop.add_node("write", write_slogan)
    builder_loop.add_node("critique", critique_slogan)
    builder_loop.add_edge(START, "write")
    builder_loop.add_edge("write", "critique")
    builder_loop.add_conditional_edges("critique", route_after_critique)
    graph_loop = builder_loop.compile()

    result_11 = graph_loop.invoke({"draft": "", "feedback": "", "attempts": 0})
    print("FINAL SLOGAN:", result_11["draft"], f"(after {result_11['attempts']} attempts)")

    mo.mermaid(graph_loop.get_graph().draw_mermaid())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Example 5: LLM plus business rules (generate and validate)

    `generate -> validate (plain Python) -> (rule broken? back to generate with the error) -> END`.
    **Notice:** `validate` is **not** an LLM: hard rules are checked by code, deterministically. The error message goes back to the model as an instruction.
    """)
    return


@app.cell
def _(END, Literal, START, StateGraph, TypedDict, llm, mo):
    class RulesState(TypedDict):
        message: str
        error: str
        attempts: int


    def generate_message(state: RulesState) -> dict:
        prompt = "Write a short reply to a customer whose order 4821 is delayed. Apologise and offer a solution."
        if state["error"]:
            prompt += f" Your previous reply was rejected: {state['error']} Rewrite it. Previous reply: {state['message']}"
        message = llm.invoke(prompt).text
        print(f"[generate] attempt {state['attempts'] + 1}: {message}")
        return {"message": message, "attempts": state["attempts"] + 1}


    def validate_message(state: RulesState) -> dict:  # plain Python: no LLM here
        text = state["message"].lower()
        if len(state["message"].split()) > 50:
            error = "Too long: use at most 50 words."
        elif "4821" not in text:
            error = "Mention the order number 4821."
        elif "refund" in text:
            error = "Never promise a refund."
        elif "[" in text:
            error = "No placeholders in square brackets: write the final text."
        else:
            error = ""
        print(f"[validate] {error or 'OK'}")
        return {"error": error}


    def route_after_validation(state: RulesState) -> Literal["generate", "__end__"]:
        if state["error"] == "" or state["attempts"] >= 4:
            return END
        return "generate"


    builder_rules_loop = StateGraph(RulesState)
    builder_rules_loop.add_node("generate", generate_message)
    builder_rules_loop.add_node("validate", validate_message)
    builder_rules_loop.add_edge(START, "generate")
    builder_rules_loop.add_edge("generate", "validate")
    builder_rules_loop.add_conditional_edges("validate", route_after_validation)
    graph_rules_loop = builder_rules_loop.compile()

    result_12 = graph_rules_loop.invoke({"message": "", "error": "", "attempts": 0})
    print("FINAL MESSAGE:", result_12["message"])

    mo.mermaid(graph_rules_loop.get_graph().draw_mermaid())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Example 6: parallelization (fan-out and fan-in)

    Three independent analyses of one ticket: **sentiment**, **products mentioned**, **priority**. None needs the result of another, so they can run **at the same time**.

    `START -> (sentiment | products | priority) -> join -> END`

    - **Fan-out:** several edges leave one node (here `START`); the targets run in the same step.
    - **Reducer:** all three write to `analyses`. `Annotated[list[str], operator.add]` appends the results instead of failing.
    - **Fan-in:** `join` waits for **all** incoming branches.

    We build the graph twice with the **same nodes**: parallel and sequential, and measure the time.
    """)
    return


@app.cell
def _(END, START, StateGraph, TypedDict, llm, mo):
    import operator
    import time
    from typing import Annotated


    class ParallelState(TypedDict):
        ticket: str
        analyses: Annotated[list[str], operator.add]  # reducer: results of parallel nodes are appended
        report: str


    def analyze_sentiment(state: ParallelState) -> dict:
        answer = llm.invoke("Sentiment of this ticket (max 3 words): " + state["ticket"]).text
        return {"analyses": [f"sentiment: {answer}"]}


    def extract_products(state: ParallelState) -> dict:
        answer = llm.invoke("Which products are mentioned? Only names, comma separated: " + state["ticket"]).text
        return {"analyses": [f"products: {answer}"]}


    def suggest_priority(state: ParallelState) -> dict:
        answer = llm.invoke("Priority of this ticket: low, medium or high. One word: " + state["ticket"]).text
        return {"analyses": [f"priority: {answer}"]}


    def join(state: ParallelState) -> dict:  # runs only after ALL three branches finished
        return {"report": " | ".join(state["analyses"])}


    # Parallel: three edges leave START
    builder_parallel = StateGraph(ParallelState)
    builder_parallel.add_node("sentiment", analyze_sentiment)
    builder_parallel.add_node("products", extract_products)
    builder_parallel.add_node("priority", suggest_priority)
    builder_parallel.add_node("join", join)
    builder_parallel.add_edge(START, "sentiment")
    builder_parallel.add_edge(START, "products")
    builder_parallel.add_edge(START, "priority")
    builder_parallel.add_edge(["sentiment", "products", "priority"], "join")  # fan-in: wait for ALL three
    builder_parallel.add_edge("join", END)
    graph_parallel = builder_parallel.compile()

    # Sequential: the same nodes in a chain
    builder_sequential = StateGraph(ParallelState)
    builder_sequential.add_node("sentiment", analyze_sentiment)
    builder_sequential.add_node("products", extract_products)
    builder_sequential.add_node("priority", suggest_priority)
    builder_sequential.add_node("join", join)
    builder_sequential.add_edge(START, "sentiment")
    builder_sequential.add_edge("sentiment", "products")
    builder_sequential.add_edge("products", "priority")
    builder_sequential.add_edge("priority", "join")
    builder_sequential.add_edge("join", END)
    graph_sequential = builder_sequential.compile()

    ticket_text = (
        "My anti-gravity boots stopped charging after a week and your support did not answer my two e-mails. "
        "I am really annoyed. I also want to buy the invisible cap, but not before this is solved."
    )

    start = time.perf_counter()
    result_13 = graph_sequential.invoke({"ticket": ticket_text, "analyses": []})
    time_sequential = time.perf_counter() - start

    start = time.perf_counter()
    result_14 = graph_parallel.invoke({"ticket": ticket_text, "analyses": []})
    time_parallel = time.perf_counter() - start

    print(result_14["report"])
    print()
    print(f"sequential: {time_sequential:.1f} s")
    print(f"parallel:   {time_parallel:.1f} s")

    mo.hstack([mo.mermaid(graph_parallel.get_graph().draw_mermaid()), mo.mermaid(graph_sequential.get_graph().draw_mermaid())])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Parallelization: summary

    - **Fan-out:** several `add_edge(source, target)` from one node; the targets run in the **same step**, in parallel.
    - **Fan-in:** `add_edge(["a", "b", "c"], "join")` (a **list** of sources) makes `join` wait for **all** of them.
      Separate `add_edge("a", "join")`, `add_edge("b", "join")` only work if the branches finish in the same step: with branches of different length `join` would run **twice**.
    - **Reducer required** when parallel nodes write to the same key (`Annotated[list, operator.add]`). Without it you get `InvalidUpdateError`.
    - Biggest gain with **slow, independent calls** (LLM, APIs). Total time is about the time of the **slowest** branch, not the sum.
    - Order of results in a reducer list is deterministic (sorted by node name), not by finishing time.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Example 7: map-reduce with `Send`

    **Task:** summarize every ACME product sheet, then write one catalog overview.
    The number of sheets is **not known in advance** (here 5 files from a folder), so we cannot draw one edge per sheet.

    `START -> (map: summarize_sheet x N, in parallel) -> (reduce: write_overview) -> END`

    - **Map:** a router returns a list of **`Send("node", input)`**: one call of the node **per item**, each with its **own input**.
    - **Reduce:** the results land in one list (reducer `operator.add`), then a single node combines them.
    """)
    return


@app.cell
def _(END, START, StateGraph, TypedDict, llm, mo):
    import operator as _operator
    from pathlib import Path
    from typing import Annotated as _Annotated

    from langgraph.types import Send


    class MapReduceState(TypedDict):
        sheets: list[str]  # the input: one text per product sheet
        summaries: _Annotated[list[str], _operator.add]  # reducer: collects the results of all map calls
        overview: str


    class SheetState(TypedDict):  # the private input of ONE map call
        sheet: str


    def fan_out(state: MapReduceState) -> list[Send]:  # the router: one Send per sheet
        return [Send("summarize_sheet", {"sheet": sheet}) for sheet in state["sheets"]]


    def summarize_sheet(state: SheetState) -> dict:  # MAP: runs once per sheet
        summary = llm.invoke("Summarize this product sheet in ONE sentence: " + state["sheet"]).text
        return {"summaries": [summary]}


    def write_overview(state: MapReduceState) -> dict:  # REDUCE: runs once, sees all summaries
        text = "\n".join(f"- {summary}" for summary in state["summaries"])
        overview = llm.invoke("Write a 2-sentence catalog introduction based on these product summaries:\n" + text).text
        return {"overview": overview}


    builder_map_reduce = StateGraph(MapReduceState)
    builder_map_reduce.add_node("summarize_sheet", summarize_sheet)
    builder_map_reduce.add_node("write_overview", write_overview)
    builder_map_reduce.add_conditional_edges(START, fan_out, ["summarize_sheet"])
    builder_map_reduce.add_edge("summarize_sheet", "write_overview")
    builder_map_reduce.add_edge("write_overview", END)
    graph_map_reduce = builder_map_reduce.compile()

    sheet_files = sorted(Path(__file__).parent.glob("static/acme-corp-dataset/products/*.md"))
    sheets = [file.read_text() for file in sheet_files]

    result_15 = graph_map_reduce.invoke({"sheets": sheets, "summaries": []})

    print(f"Sheets: {len(sheets)} -> summaries: {len(result_15['summaries'])}")
    for _summary in result_15["summaries"]:
        print("-", _summary)
    print()
    print("OVERVIEW:", result_15["overview"])

    mo.mermaid(graph_map_reduce.get_graph().draw_mermaid())
    return (graph_map_reduce,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Map-reduce: summary

    - **`Send(node, input)`** starts a node with its **own input state**. A router returns a **list** of them: the length can change on every run.
    - All map calls run **in parallel**; their results are merged by the **reducer** (`operator.add`).
    - The **reduce** node runs once, after all map calls finished, and sees the whole list.
    - The diagram shows one box for the map node, although it ran N times.
    - Use it for: summarizing many documents, scoring many candidates, calling an API per item.
    """)
    return


@app.cell
def _(graph_map_reduce):
    # Same graph, a different number of items: 2 sheets instead of 5
    result_16 = graph_map_reduce.invoke({
        "sheets": ["Invisible Cap: a bowler hat that makes you invisible, USD 4,999.", "Pocket Hole: a portable hole, USD 799."],
        "summaries": [],
    })
    print(f"Sheets: 2 -> summaries: {len(result_16['summaries'])}")
    print("OVERVIEW:", result_16["overview"])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Example 8: subgraphs

    **Task:** write a reply, then run it through a reusable **quality check** (length and tone).

    `START -> write_reply -> quality_check (a whole graph used as ONE node) -> END`

    - A **subgraph** is a compiled graph used as a node of another graph.
    - Parent and subgraph **share state keys** (`reply`, `issues`): the subgraph is added directly with `add_node("quality_check", subgraph)`.
    - `get_graph(xray=True)` draws what is inside.
    """)
    return


@app.cell
def _(END, START, StateGraph, TypedDict, llm, mo):
    # --- The subgraph: a small, reusable quality check with its own two nodes ---
    class CheckState(TypedDict):
        reply: str
        issues: list[str]


    def check_length(state: CheckState) -> dict:
        words = len(state["reply"].split())
        return {"issues": state["issues"] + ([f"too long: {words} words (max 50)"] if words > 50 else [])}


    def check_tone(state: CheckState) -> dict:
        return {"issues": state["issues"] + (["too many exclamation marks"] if "!" in state["reply"] else [])}


    builder_check = StateGraph(CheckState)
    builder_check.add_node("check_length", check_length)
    builder_check.add_node("check_tone", check_tone)
    builder_check.add_edge(START, "check_length")
    builder_check.add_edge("check_length", "check_tone")
    builder_check.add_edge("check_tone", END)
    subgraph_check = builder_check.compile()


    # --- The parent graph: it has the keys reply and issues too, plus its own: question ---
    class ReplyState(TypedDict):
        question: str
        reply: str
        issues: list[str]


    def write_reply(state: ReplyState) -> dict:
        reply = llm.invoke("Write a very friendly, enthusiastic reply of about 80 words to this customer: " + state["question"]).text
        return {"reply": reply}


    builder_parent = StateGraph(ReplyState)
    builder_parent.add_node("write_reply", write_reply)
    builder_parent.add_node("quality_check", subgraph_check)  # the compiled subgraph is the node
    builder_parent.add_edge(START, "write_reply")
    builder_parent.add_edge("write_reply", "quality_check")
    builder_parent.add_edge("quality_check", END)
    graph_parent = builder_parent.compile()

    result_17 = graph_parent.invoke({"question": "My order is 3 days late. Where is it?", "issues": []})

    print("REPLY:", result_17["reply"])
    print("ISSUES:", result_17["issues"])

    mo.mermaid(graph_parent.get_graph(xray=True).draw_mermaid())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Subgraphs with a different state

    When the schemas **differ**, you cannot add the subgraph directly. Wrap it in a normal node:
    translate the parent state into the subgraph input, call `subgraph.invoke(...)`, translate the result back.
    """)
    return


@app.cell
def _(END, START, StateGraph, TypedDict):
    # --- A subgraph with its OWN schema: text -> words ---
    class CounterState(TypedDict):
        text: str
        words: int


    def count_words(state: CounterState) -> dict:
        return {"words": len(state["text"].split())}


    builder_counter = StateGraph(CounterState)
    builder_counter.add_node("count_words", count_words)
    builder_counter.add_edge(START, "count_words")
    builder_counter.add_edge("count_words", END)
    subgraph_counter = builder_counter.compile()


    # --- A parent with a different schema: the wrapper node does the translation ---
    class ArticleState(TypedDict):
        article: str
        length: int


    def measure(state: ArticleState) -> dict:
        sub_result = subgraph_counter.invoke({"text": state["article"]})  # parent -> subgraph input
        return {"length": sub_result["words"]}  # subgraph output -> parent state


    builder_article = StateGraph(ArticleState)
    builder_article.add_node("measure", measure)
    builder_article.add_edge(START, "measure")
    builder_article.add_edge("measure", END)
    graph_article = builder_article.compile()

    result_18 = graph_article.invoke({"article": "LangGraph subgraphs make big workflows modular."})
    print(result_18)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Subgraphs: summary

    - **Same keys:** `add_node("name", compiled_subgraph)`. Shared keys pass in and out automatically.
    - **Different keys:** wrap `subgraph.invoke(...)` in a function node and map the state yourself.
    - Why: **reuse** (one quality check, many graphs), **teams** (each owns a subgraph), **clear structure** of big graphs.
    - `get_graph(xray=True)` shows the inside; without it the subgraph is a single box.
    - Note: `create_agent(...)` returns a compiled graph too, so **an agent can be a node** of your graph. That is our next example.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Example 9: an agent as a graph (ReAct by hand)

    `create_agent` returns a graph. Here we **build the same loop ourselves**: reason → act → observe.

    `START -> agent -> (tool calls?) -> tools -> agent -> ... -> END`

    - **`agent` node:** the model, with the tools bound (`bind_tools`). It answers or **requests** tools.
    - **`tools` node:** the ready-made `ToolNode(TOOLS)` runs the requested tools and appends the results.
    - **`tools_condition`:** ready-made router: tool calls in the last message → `"tools"`, otherwise → `END`.
    - **State:** `MessagesState`. The messages list is the agent's memory within one run.
    """)
    return


@app.cell
def _(END, START, StateGraph, llm, mo):
    from langchain_core.messages import SystemMessage
    from langgraph.graph import MessagesState
    from langgraph.prebuilt import ToolNode, tools_condition
    from support_tools import SYSTEM_PROMPT, TOOLS, USER_MESSAGE

    llm_with_tools = llm.bind_tools(TOOLS)  # the model may now request these tools


    def call_model(state: MessagesState) -> dict:
        response = llm_with_tools.invoke([SystemMessage(SYSTEM_PROMPT)] + state["messages"])
        return {"messages": [response]}


    builder_react = StateGraph(MessagesState)
    builder_react.add_node("agent", call_model)
    builder_react.add_node("tools", ToolNode(TOOLS))
    builder_react.add_edge(START, "agent")
    builder_react.add_conditional_edges("agent", tools_condition)  # tool calls -> "tools", else -> END
    builder_react.add_edge("tools", "agent")  # the loop: observe, then reason again
    graph_react = builder_react.compile()

    result_19 = graph_react.invoke({"messages": [("user", USER_MESSAGE)]})

    for _message in result_19["messages"]:
        if _message.type == "ai" and _message.tool_calls:
            print("AI requests:", [(call["name"], call["args"]) for call in _message.tool_calls])
        elif _message.type == "tool":
            print("TOOL result:", _message.content)
        else:
            print(_message.type.upper() + ":", _message.text)

    mo.mermaid(graph_react.get_graph().draw_mermaid())
    return (graph_react,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Agent as a graph: summary

    - An agent is a **loop in a graph**: `agent` ⇄ `tools`, with a condition that leaves the loop.
    - The model only **requests** tools. The `tools` node **executes** them (same rule as in the tools notebook).
    - The diagram is the same as the one of `create_agent`. We just saw how it is built.
    - Why build it by hand: you can **add nodes inside the loop** (a check before a tool, a limit, an approval) or **embed the agent in a bigger workflow**.
    - Next: pause this loop for a human with **`interrupt`**.
    """)
    return


if __name__ == "__main__":
    app.run()

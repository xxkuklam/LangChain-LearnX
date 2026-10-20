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

    ## Example 2 of 9: conditions and routing
    """)
    return


@app.cell
def _():
    from typing import Literal

    from dotenv import find_dotenv, load_dotenv
    from langgraph.graph import END, START, StateGraph
    from typing_extensions import TypedDict

    load_dotenv(find_dotenv(usecwd=True))  # API key from .env

    MODEL = "openai:gpt-5.4-mini"
    return END, Literal, MODEL, START, StateGraph, TypedDict


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
    # Node names in one place: used by routers, Command and add_node / add_edge
    CLASSIFY_NODE_NAME = "classify"
    BILLING_REPLY_NODE_NAME = "billing_reply"
    TECHNICAL_REPLY_NODE_NAME = "technical_reply"
    ESCALATE_NODE_NAME = "escalate"


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


    def route_by_category(state: TicketState) -> Literal[BILLING_REPLY_NODE_NAME, TECHNICAL_REPLY_NODE_NAME, ESCALATE_NODE_NAME]:
        if state["category"] == "billing":
            return BILLING_REPLY_NODE_NAME
        if state["category"] == "technical":
            return TECHNICAL_REPLY_NODE_NAME
        return ESCALATE_NODE_NAME

    return (
        BILLING_REPLY_NODE_NAME,
        CLASSIFY_NODE_NAME,
        ESCALATE_NODE_NAME,
        TECHNICAL_REPLY_NODE_NAME,
        TicketState,
        billing_reply,
        classify_rules,
        escalate,
        route_by_category,
        technical_reply,
    )


@app.cell
def _(
    BILLING_REPLY_NODE_NAME,
    CLASSIFY_NODE_NAME,
    END,
    ESCALATE_NODE_NAME,
    START,
    StateGraph,
    TECHNICAL_REPLY_NODE_NAME,
    TicketState,
    billing_reply,
    classify_rules,
    escalate,
    route_by_category,
    technical_reply,
):
    builder_rules = StateGraph(TicketState)
    builder_rules.add_node(CLASSIFY_NODE_NAME, classify_rules)
    builder_rules.add_node(BILLING_REPLY_NODE_NAME, billing_reply)
    builder_rules.add_node(TECHNICAL_REPLY_NODE_NAME, technical_reply)
    builder_rules.add_node(ESCALATE_NODE_NAME, escalate)

    builder_rules.add_edge(START, CLASSIFY_NODE_NAME)
    builder_rules.add_conditional_edges(CLASSIFY_NODE_NAME, route_by_category)
    builder_rules.add_edge(BILLING_REPLY_NODE_NAME, END)
    builder_rules.add_edge(TECHNICAL_REPLY_NODE_NAME, END)
    builder_rules.add_edge(ESCALATE_NODE_NAME, END)

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
    BILLING_REPLY_NODE_NAME,
    CLASSIFY_NODE_NAME,
    END,
    ESCALATE_NODE_NAME,
    START,
    StateGraph,
    TECHNICAL_REPLY_NODE_NAME,
    TicketState,
    billing_reply,
    classify_llm,
    escalate,
    route_by_category,
    technical_reply,
):
    builder_llm = StateGraph(TicketState)
    builder_llm.add_node(CLASSIFY_NODE_NAME, classify_llm)  # the only difference
    builder_llm.add_node(BILLING_REPLY_NODE_NAME, billing_reply)
    builder_llm.add_node(TECHNICAL_REPLY_NODE_NAME, technical_reply)
    builder_llm.add_node(ESCALATE_NODE_NAME, escalate)

    builder_llm.add_edge(START, CLASSIFY_NODE_NAME)
    builder_llm.add_conditional_edges(CLASSIFY_NODE_NAME, route_by_category)
    builder_llm.add_edge(BILLING_REPLY_NODE_NAME, END)
    builder_llm.add_edge(TECHNICAL_REPLY_NODE_NAME, END)
    builder_llm.add_edge(ESCALATE_NODE_NAME, END)

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
def _(
    BILLING_REPLY_NODE_NAME,
    ESCALATE_NODE_NAME,
    Literal,
    TECHNICAL_REPLY_NODE_NAME,
    TicketState,
):
    from langgraph.types import Command


    def classify_command(state: TicketState) -> Command[Literal[BILLING_REPLY_NODE_NAME, TECHNICAL_REPLY_NODE_NAME, ESCALATE_NODE_NAME]]:
        text = state["question"].lower()
        if "invoice" in text or "refund" in text or "payment" in text:
            return Command(update={"category": "billing"}, goto=BILLING_REPLY_NODE_NAME)
        if "error" in text or "crash" in text or "not working" in text:
            return Command(update={"category": "technical"}, goto=TECHNICAL_REPLY_NODE_NAME)
        return Command(update={"category": "other"}, goto=ESCALATE_NODE_NAME)

    return (classify_command,)


@app.cell
def _(
    BILLING_REPLY_NODE_NAME,
    CLASSIFY_NODE_NAME,
    END,
    ESCALATE_NODE_NAME,
    START,
    StateGraph,
    TECHNICAL_REPLY_NODE_NAME,
    TicketState,
    billing_reply,
    classify_command,
    escalate,
    technical_reply,
):
    builder_command = StateGraph(TicketState)
    builder_command.add_node(CLASSIFY_NODE_NAME, classify_command)
    builder_command.add_node(BILLING_REPLY_NODE_NAME, billing_reply)
    builder_command.add_node(TECHNICAL_REPLY_NODE_NAME, technical_reply)
    builder_command.add_node(ESCALATE_NODE_NAME, escalate)

    builder_command.add_edge(START, CLASSIFY_NODE_NAME)  # no add_conditional_edges: the Command decides
    builder_command.add_edge(BILLING_REPLY_NODE_NAME, END)
    builder_command.add_edge(TECHNICAL_REPLY_NODE_NAME, END)
    builder_command.add_edge(ESCALATE_NODE_NAME, END)

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


if __name__ == "__main__":
    app.run()

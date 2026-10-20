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
    # 11.6 LangGraph
    """)
    return


@app.cell
def _():
    from typing import Literal

    from dotenv import find_dotenv, load_dotenv
    from langchain.chat_models import init_chat_model
    from langgraph.graph import END, START, StateGraph
    from typing_extensions import TypedDict

    load_dotenv(find_dotenv(usecwd=True))  # API key from .env

    MODEL = "openai:gpt-5.4-mini"
    llm = init_chat_model(MODEL)
    return END, START, StateGraph, TypedDict, llm


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


if __name__ == "__main__":
    app.run()

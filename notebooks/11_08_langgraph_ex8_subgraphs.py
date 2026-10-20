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
    # 11.8 LangGraph
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
    import operator
    from typing import Annotated


    # --- The subgraph: a small, reusable quality check with its own two nodes ---
    class CheckState(TypedDict):
        reply: str
        issues: Annotated[list[str], operator.add]  # reducer: each check appends its findings


    def check_length(state: CheckState) -> dict:
        words = len(state["reply"].split())
        return {"issues": [f"too long: {words} words (max 50)"] if words > 50 else []}


    def check_tone(state: CheckState) -> dict:
        return {"issues": ["too many exclamation marks"] if "!" in state["reply"] else []}


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


if __name__ == "__main__":
    app.run()

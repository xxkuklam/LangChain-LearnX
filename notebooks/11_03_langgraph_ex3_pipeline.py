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

    ## Example 3 of 9: a pipeline of LLM nodes
    """)
    return


@app.cell
def _():
    from typing import Literal

    from dotenv import find_dotenv, load_dotenv
    from langchain.chat_models import init_chat_model
    from langgraph.graph import END, START, StateGraph
    from pydantic import BaseModel
    from typing_extensions import TypedDict

    load_dotenv(find_dotenv(usecwd=True))  # API key from .env

    MODEL = "openai:gpt-5.4-mini"


    class Category(BaseModel):  # the structured answer of the classifier (as in example 2)
        category: Literal["billing", "technical", "other"]

    return Category, END, MODEL, START, StateGraph, TypedDict, init_chat_model


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


if __name__ == "__main__":
    app.run()

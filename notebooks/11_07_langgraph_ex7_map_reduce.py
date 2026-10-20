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

    ## Example 7 of 9: map-reduce with Send
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
    return END, Literal, START, StateGraph, TypedDict, llm


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


if __name__ == "__main__":
    app.run()

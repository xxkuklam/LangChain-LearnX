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

    ## Example 4 of 9: a loop (write and critique)
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
        if state["feedback"] == "" or state["attempts"] >= 5:  # approved, or out of attempts
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


if __name__ == "__main__":
    app.run()

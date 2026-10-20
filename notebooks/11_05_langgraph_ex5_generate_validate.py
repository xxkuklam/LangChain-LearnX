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
    # 11.5 LangGraph
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


if __name__ == "__main__":
    app.run()

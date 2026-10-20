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

    ## Example 9 of 9: an agent as a graph
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
def _(START, StateGraph, llm, mo):
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
    return


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

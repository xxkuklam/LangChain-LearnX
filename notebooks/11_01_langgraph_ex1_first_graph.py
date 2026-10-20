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
    # 11.1 LangGraph
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

    return END, Literal, START, State, StateGraph


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
    return (agent,)


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


if __name__ == "__main__":
    app.run()

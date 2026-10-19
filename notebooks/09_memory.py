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
    # 9. Memory

    ## Checkpointers (short-term) and stores (long-term)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The problem: the model remembers nothing

    An LLM is **stateless**. Every call starts from zero.

    What looks like "memory" in ChatGPT is the application **sending the whole conversation again** with every new message.

    So an agent needs two things:

    1. A place to **keep the conversation** between calls.
    2. A way to tell **which conversation** a new message belongs to.

    LangGraph gives us both, and `create_agent` uses them out of the box.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Two kinds of memory

    | | **Short-term memory** | **Long-term memory** |
    |---|---|---|
    | **Lives** | Inside **one conversation** (thread) | **Across** conversations and users |
    | **Holds** | The message history and the agent state | Facts, preferences, knowledge |
    | **Mechanism** | **Checkpointer** | **Store** |
    | **Keyed by** | `thread_id` | `namespace` + `key` |
    | **Example** | "What did I just ask you?" | "This customer prefers short answers" |
    | **Analogy** | The notepad on the table during **one meeting** | The **customer file** in the archive |
    """)
    return


@app.cell(hide_code=True, expand_output=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## Checkpointer: save the state after every step

    A **checkpointer** saves a **snapshot of the agent state** (messages and more) after each step of the run.

    - Snapshots are grouped by **`thread_id`**: one thread = one conversation.
    - Next call with the same `thread_id`: the agent **loads the last snapshot** and continues.
    - Another `thread_id`: a clean start, the conversations never mix.

    Same idea as the *save game* from the human-in-the-loop example: the checkpointer is what made the pause possible.
    """),
        mo.mermaid(
            """
            sequenceDiagram
                participant U as User
                participant A as Agent
                participant C as Checkpointer
                U->>A: "Top 3 Norwegian metal bands?" (thread 1)
                A->>C: load thread 1 (empty)
                A->>C: save: question + answer
                U->>A: "Their best songs?" (thread 1)
                A->>C: load thread 1
                C-->>A: question + answer
                A->>C: save: whole history + new answer
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Checkpointer: which one to use?

    | Checkpointer | Package | Use it for |
    |---|---|---|
    | `InMemorySaver` | `langgraph` (built in) | Demos, tests. **Lost when the process ends** |
    | `SqliteSaver` | `langgraph-checkpoint-sqlite` | Local tools, small apps |
    | `PostgresSaver` | `langgraph-checkpoint-postgres` | **Production**, shared between instances |

    ```python
    from langgraph.checkpoint.memory import InMemorySaver

    agent = create_agent(MODEL, tools, checkpointer=InMemorySaver())

    config = {"configurable": {"thread_id": "customer-42"}}
    agent.invoke({"messages": [...]}, config)      # same config = same conversation
    ```

    Besides memory, checkpoints give us: **human in the loop** (pause and resume), **recovery after a crash** and **time travel** (replay from an earlier step).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Long conversations: the history keeps growing

    A checkpointer stores **everything**. After many turns the history is:

    - **too long** for the context window,
    - **expensive** (we pay for all tokens on every call),
    - **noisy** (old, irrelevant messages confuse the model).

    Options (all are middleware, you know the idea from section 7):

    | Strategy | How | Trade-off |
    |---|---|---|
    | **Trim** | Keep the first and the last N messages (`@before_model`) | Simple, loses the middle |
    | **Delete** | Remove chosen messages with `RemoveMessage` | Keep tool calls and results paired |
    | **Summarize** | `SummarizationMiddleware`: old part becomes a summary | One extra model call, keeps the gist |
    """)
    return


@app.cell(hide_code=True, expand_output=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## Store: memory that survives the conversation

    A checkpointer is **per thread**. A new thread knows nothing about the old ones.

    A **store** is a small **key-value database for JSON documents**, shared by all threads:

    - **namespace**: a tuple, like a folder path, e.g. `("users", "anne")`,
    - **key**: the name of the document,
    - **value**: a JSON-serializable dict.

    ```python
    store.put(("users", "anne"), "preferences", {"language": "Norwegian", "style": "short"})
    item = store.get(("users", "anne"), "preferences")      # item.value -> the dict
    items = store.search(("users", "anne"), query="how does she like answers?")   # semantic search
    ```
    """),
        mo.mermaid(
            """
            flowchart LR
                T1["Thread 1 (Monday)"] -->|"put"| S[("Store<br/>users / anne")]
                T2["Thread 2 (Friday)"] -->|"get / search"| S
                T3["Thread 3 (other user)"] -.->|"other namespace"| S2[("Store<br/>users / ingrid")]
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Store: how an agent uses it

    The store is passed to the agent, and **tools** read and write it through `runtime.store`.
    The model decides **when** to save or recall something, the code decides **where** it goes.

    | Store | Package | Use it for |
    |---|---|---|
    | `InMemoryStore` | `langgraph` (built in) | Demos, tests |
    | `PostgresStore` | `langgraph-checkpoint-postgres` | **Production** |

    - With an embedding model the store supports **semantic search** (`query=...`), not only exact key lookup.
    - **Who owns the data?** Always put the user id into the namespace, so users never see each other's memories.
    - Long-term memory is **personal data**: decide what is saved, for how long, and how a user can delete it.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Checkpointer vs. store

    | | **Checkpointer** | **Store** |
    |---|---|---|
    | Question it answers | "Where were we in **this** conversation?" | "What do we know about **this user**?" |
    | Scope | One `thread_id` | All threads |
    | Filled by | Automatically, after each step | Explicitly, by tools or code |
    | Content | Full state (messages, ...) | Any JSON you choose |
    | You can use | Without a store | Without a checkpointer |

    **Rule of thumb:** a checkpointer gives the agent a *short-term memory*, a store gives it a *long-term memory*. Real applications often use both.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Demo: the same two questions, without and with a checkpointer

    1. **Question 1:** "Which are the 3 most popular metal bands in Norway?"
    2. **Question 2:** "What are the most popular songs of **these** bands?"

    The second question only makes sense if the agent **remembers the first answer**.
    """)
    return


@app.cell
def _():
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv(usecwd=True))  # API keys from .env
    return


@app.cell
def _():
    from langchain.agents import create_agent
    from langgraph.checkpoint.memory import InMemorySaver

    MODEL = "openai:gpt-5.4-mini"
    QUESTION_1 = "Which are the 3 most popular metal bands in Norway? Just list the names."
    QUESTION_2 = "What are the most popular songs of these bands?"
    return InMemorySaver, MODEL, QUESTION_1, QUESTION_2, create_agent


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Example 1: no checkpointer

    Every `invoke` is a **separate run**: the agent only sees the message we pass in.
    """)
    return


@app.cell
def _(MODEL, create_agent):
    agent_no_memory = create_agent(MODEL, tools=[], system_prompt="You are a concise music expert.")
    return (agent_no_memory,)


@app.cell
def _(QUESTION_1, agent_no_memory):
    print("USER:", QUESTION_1)

    result_1 = agent_no_memory.invoke({"messages": [{"role": "user", "content": QUESTION_1}]})
    print("AGENT:", result_1["messages"][-1].text)
    return


@app.cell
def _(QUESTION_2, agent_no_memory):
    print("USER:", QUESTION_2)

    result_2 = agent_no_memory.invoke({"messages": [{"role": "user", "content": QUESTION_2}]})
    print("AGENT:", result_2["messages"][-1].text)
    print()
    print("Messages the agent saw in this run:", len(result_2["messages"]))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The agent has **no idea** which bands we mean. It saw only 2 messages: our question and its own answer.

    ### Example 2: with a checkpointer

    Two changes:

    1. `checkpointer=InMemorySaver()` when we create the agent.
    2. The **same `config` with `thread_id`** in both calls.
    """)
    return


@app.cell
def _(InMemorySaver, MODEL, create_agent):
    agent_with_memory = create_agent(
        MODEL,
        tools=[],
        system_prompt="You are a concise music expert.",
        checkpointer=InMemorySaver(),
    )

    config_metal = {"configurable": {"thread_id": "metal-1"}}
    return agent_with_memory, config_metal


@app.cell
def _(QUESTION_1, agent_with_memory, config_metal):
    print("USER:", QUESTION_1)

    result_3 = agent_with_memory.invoke({"messages": [{"role": "user", "content": QUESTION_1}]}, config_metal)
    print("AGENT:", result_3["messages"][-1].text)
    return


@app.cell
def _(QUESTION_2, agent_with_memory, config_metal):
    print("USER:", QUESTION_2)

    result_4 = agent_with_memory.invoke({"messages": [{"role": "user", "content": QUESTION_2}]}, config_metal)
    print("AGENT:", result_4["messages"][-1].text)
    print()
    print("Messages the agent saw in this run:", len(result_4["messages"]))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now the agent knows what **"these bands"** are: the first question and answer were loaded from the checkpoint.
    The second call saw 4 messages instead of 2, **and we sent only the new question**.

    ### Example 3: another thread = another conversation

    Same agent, same checkpointer, different `thread_id`.
    """)
    return


@app.cell
def _(QUESTION_2, agent_with_memory):
    config_other = {"configurable": {"thread_id": "metal-2"}}

    print("USER (thread metal-2):", QUESTION_2)

    result_5 = agent_with_memory.invoke({"messages": [{"role": "user", "content": QUESTION_2}]}, config_other)
    print("AGENT:", result_5["messages"][-1].text)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A new thread starts **empty**: the memory belongs to the thread, not to the agent.
    This is how one agent can serve thousands of customers at once without mixing their conversations.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Looking inside: the saved state

    The checkpointer is a database of snapshots. We can read the current state of any thread:
    """)
    return


@app.cell
def _(agent_with_memory, config_metal):
    snapshot = agent_with_memory.get_state(config_metal)

    for message in snapshot.values["messages"]:
        print(f"{message.type:>5}: {message.text[:80]!r}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Long-term memory: a store shared by all threads

    **Scenario:** a user tells the agent what they like. Days later, in a **brand new conversation**, the agent should still know it.

    The plan:

    1. A **store** keeps facts under the namespace `("users", <user_id>)`.
    2. Two tools: **`save_memory`** and **`get_memories`**, both use `runtime.store`.
    3. The system prompt tells the agent **when** to use them.
    4. The user id travels in the **context** (not in the prompt), so the model cannot "choose" another user's memories.
    """)
    return


@app.cell
def _():
    import uuid
    from dataclasses import dataclass

    from langchain.tools import ToolRuntime, tool
    from langgraph.store.memory import InMemoryStore

    store = InMemoryStore()  # demo only; production: PostgresStore


    @dataclass
    class Context:
        user_id: str  # who is talking: passed on every call


    @tool
    def save_memory(fact: str, runtime: ToolRuntime[Context]) -> str:
        """Save a lasting fact or preference about the user (e.g. favourite music, preferred answer style)."""
        runtime.store.put(("users", runtime.context.user_id), str(uuid.uuid4()), {"fact": fact})
        return f"Saved: {fact}"


    @tool
    def get_memories(runtime: ToolRuntime[Context]) -> str:
        """Get everything we remember about the user. Call this at the start of a conversation."""
        items = runtime.store.search(("users", runtime.context.user_id))
        if not items:
            return "No memories about this user yet."
        return "\n".join(f"- {item.value['fact']}" for item in items)

    return Context, get_memories, save_memory, store


@app.cell
def _(
    Context,
    InMemorySaver,
    MODEL,
    create_agent,
    get_memories,
    save_memory,
    store,
):
    agent_long_term = create_agent(
        MODEL,
        tools=[save_memory, get_memories],
        system_prompt=(
            "You are a concise music assistant with a long-term memory. "
            "At the start of a conversation call get_memories. "
            "When the user shares a lasting preference, call save_memory. "
            "Follow the remembered preferences in your answers."
        ),
        checkpointer=InMemorySaver(),  # short-term: this conversation
        store=store,  # long-term: all conversations
        context_schema=Context,
    )
    return (agent_long_term,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Session 1 (Monday): the user shares a preference
    """)
    return


@app.cell
def _(Context, agent_long_term):
    result_6 = agent_long_term.invoke(
        {"messages": [{"role": "user", "content": "I love metal. Please keep your answers to two sentences."}]},
        {"configurable": {"thread_id": "anne-monday"}},
        context=Context(user_id="anne"),
    )

    for _message in result_6["messages"]:
        for _call in getattr(_message, "tool_calls", []):
            print("tool call:", _call["name"], _call["args"])
    print("AGENT:", result_6["messages"][-1].text)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### What is in the store now?

    It is just JSON documents under a namespace:
    """)
    return


@app.cell
def _(store):
    for _item in store.search(("users", "anne")):
        print(_item.namespace, _item.key[:8], _item.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Session 2 (Friday): a new thread, the same user

    A **new `thread_id`**: the checkpointer knows nothing about Monday. Only the store does.
    """)
    return


@app.cell
def _(Context, agent_long_term):
    result_7 = agent_long_term.invoke(
        {"messages": [{"role": "user", "content": "Recommend me one album to listen to tonight."}]},
        {"configurable": {"thread_id": "anne-friday"}},
        context=Context(user_id="anne"),
    )

    for _message in result_7["messages"]:
        for _call in getattr(_message, "tool_calls", []):
            print("tool call:", _call["name"], _call["args"])
    print("AGENT:", result_7["messages"][-1].text)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The agent called `get_memories`, found "black metal" and "two sentences", and used both. The conversation itself was new.

    ### Session 3: a different user

    Same agent, same store, but another `user_id`, so another namespace.
    """)
    return


@app.cell
def _(Context, agent_long_term):
    result_8 = agent_long_term.invoke(
        {"messages": [{"role": "user", "content": "Recommend me one album to listen to tonight."}]},
        {"configurable": {"thread_id": "ingrid-1"}},
        context=Context(user_id="ingrid"),
    )

    for _message in result_8["messages"]:
        for _call in getattr(_message, "tool_calls", []):
            print("tool call:", _call["name"], _call["args"])
    print("AGENT:", result_8["messages"][-1].text)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Ingrid has no memories, so she gets a generic answer. **The namespace is the privacy boundary.**

    ### Where could this go next?

    - **`PostgresStore`** so the memories survive a restart.
    - A store with an **embedding model** and `store.search(namespace, query="...")` to find memories by meaning when there are hundreds of them.
    - Memories the user can **see and delete**, and a rule for what is *not* worth saving.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Memory: summary

    - An LLM is **stateless**: "memory" means storing the state and sending it again.
    - **Checkpointer** = short-term memory of **one conversation** (`thread_id`). `InMemorySaver` for demos, `PostgresSaver` for production.
    - Reusing the same `thread_id` continues a conversation, a new one starts clean.
    - Long histories need **trimming or summarizing** (middleware).
    - **Store** = long-term memory **across threads and users**: namespace + key + JSON, with optional semantic search.
    - Tools reach the store through `runtime.store`.

    **Next:** RAG: giving the agent knowledge from our own documents.
    """)
    return


if __name__ == "__main__":
    app.run()

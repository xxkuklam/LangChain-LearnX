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
    # 4. Chaining (LCEL)

    ## `prompt | model | parser`: building blocks joined with a pipe
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The problem

    Almost every LLM call repeats the same three steps:

    1. **Prompt:** put the user's data into a prompt template.
    2. **Model:** send it to the LLM.
    3. **Parser:** take the answer out (plain text, or an object).

    We could write these steps by hand every time. **LCEL** (LangChain Expression Language) lets us join them into one object with the `|` operator, like pipes in a Unix shell:

    ```text
    cat file.txt | grep error | wc -l          →          prompt | model | parser
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.mermaid("""
    flowchart LR
        IN["Input<br/>{'language': 'English', 'question': '...'}"] --> P["Prompt template<br/>fills the placeholders"]
        P --> M["Chat model<br/>calls the LLM"]
        M --> O["Output parser<br/>AIMessage → str"]
        O --> OUT["Output<br/>'Hold the red button...'"]
    """)
    return


@app.cell
def _():
    from dotenv import find_dotenv, load_dotenv
    from langchain.chat_models import init_chat_model
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate

    load_dotenv(find_dotenv(usecwd=True))  # load API keys from .env

    MODEL = "openai:gpt-5.4-mini"
    model = init_chat_model(MODEL)
    return ChatPromptTemplate, StrOutputParser, model


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 1: the three steps by hand

    First without any chain, so we can see what the pipe will replace.
    A **`ChatPromptTemplate`** is a list of messages with `{placeholders}`.
    """)
    return


@app.cell
def _(ChatPromptTemplate, StrOutputParser, model):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a support agent for ACME Corp. Answer in {language}, in max 2 sentences."),
        ("human", "{question}"),
    ])

    # 1. Prompt: fill the placeholders
    prompt_value = prompt.invoke({
        "language": "English", 
        "question": "My anti-gravity boots took me to the ceiling. How do I get down?"
    })
    print("PROMPT:", prompt_value.to_messages())
    print()

    # 2. Model: call the LLM
    response = model.invoke(prompt_value)
    print("MODEL returned:", type(response).__name__)
    print()

    # 3. Parser: take the text out of the message
    answer = StrOutputParser().invoke(response)
    print("PARSER returned a string:", isinstance(answer, str))
    print(answer)
    return (prompt,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 2: the same with a pipe

    `prompt | model | parser` creates **one object**: a chain.
    Every element is a **Runnable**: it takes an input, returns an output, and the output of one is the input of the next.
    """)
    return


@app.cell
def _(StrOutputParser, model, prompt):
    parser = StrOutputParser()
    chain = prompt | model | parser  # the only new line

    print(type(chain).__name__)  # RunnableSequence: a list of steps

    answer_chain = chain.invoke({"language": "English", "question": "My anti-gravity boots took me to the ceiling. How do I get down?"})
    print(answer_chain)
    return chain, parser


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## One interface for everything

    Prompts, models, parsers and whole chains are all **Runnables**, so a chain has the same methods as a model:

    | Method | What it does |
    |---|---|
    | `invoke(input)` | One input, one output |
    | `batch([inputs])` | Many inputs **in parallel** |
    | `stream(input)` | Output piece by piece (tokens) |
    | `ainvoke` / `abatch` / `astream` | The same, `async` |

    Write the chain once, use it in any mode.
    """)
    return


@app.cell
def _(chain):
    _questions = [
        ("English", "My order is 3 days late. What should I do?"),
        ("Polish", "How do I reset my password?"),
        ("Norwegian", "Can I change the delivery address?"),
    ]
    inputs = [{"language": language, "question": question} for language, question in _questions]

    # batch: three calls in parallel
    for _answer in chain.batch(inputs):
        print("-", _answer)
    print()

    # stream: print tokens as they arrive
    for _chunk in chain.stream(inputs[0]):
        print(_chunk, end="", flush=True)
    print()
    return (inputs,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 3: a structured result at the end

    The last step does not have to be a text parser.
    `model.with_structured_output(...)` (previous notebook) is also a Runnable, so it fits at the end of a chain.
    """)
    return


@app.cell
def _(ChatPromptTemplate, model):
    from typing import Literal

    from pydantic import BaseModel, Field


    class Triage(BaseModel):
        topic: Literal["billing", "technical", "safety", "other"] = Field(
            description="'safety' = injuries or dangerous behaviour of a product"
        )
        urgent: bool = Field(description="True if someone is hurt or blocked")


    triage_prompt = ChatPromptTemplate.from_template("Classify this customer message: {message}")
    triage_chain = triage_prompt | model.with_structured_output(Triage)

    triage = triage_chain.invoke({"message": "My boots launched me through the ceiling and my ankle hurts badly!"})
    print(type(triage).__name__)
    print(triage)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 4: chain after chain

    A chain is a Runnable, so it can be a **step of a bigger chain**.
    A `dict` in front of the pipe means: "run these chains on the same input and collect the results under these keys". It is the way to feed the next prompt.
    """)
    return


@app.cell
def _(ChatPromptTemplate, chain, inputs, model, parser):
    translate_prompt = ChatPromptTemplate.from_template("Translate to Norwegian, return only the translation:\n\n{text}")
    translate_chain = translate_prompt | model | parser

    # {"text": chain} runs `chain` and passes its answer to the next step as {"text": ...}
    reply_in_norwegian = {"text": chain} | translate_chain

    print(reply_in_norwegian.invoke(inputs[0]))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 5: parallel branches and plain Python in a chain

    - **`RunnableParallel`** runs several chains on the **same input** at the same time and returns a `dict`.
    - **`RunnableLambda`** turns any Python function into a step.
    - Every chain can draw itself: `chain.get_graph()`. This is the same drawing method we will use for LangGraph.
    """)
    return


@app.cell
def _(ChatPromptTemplate, mo, model, parser):
    from langchain_core.runnables import RunnableLambda, RunnableParallel

    summary_chain = ChatPromptTemplate.from_template("Summarize in max 6 words:\n\n{text}") | model | parser
    sentiment_chain = ChatPromptTemplate.from_template("Sentiment of this text (positive, neutral or negative), one word:\n\n{text}") | model | parser

    analysis_chain = RunnableParallel(
        summary=summary_chain,
        sentiment=sentiment_chain,
        words=RunnableLambda(lambda inputs: len(inputs["text"].split())),  # plain Python, no LLM
    )

    analysis = analysis_chain.invoke({"text": "I bought the GraviStop Turbo boots. They are amazing, but the manual does not mention ceilings. My cat is very confused."})
    print(analysis)

    mo.mermaid(analysis_chain.get_graph().draw_mermaid())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What a chain cannot do

    A chain is **one straight pass** (with parallel branches), from the input to the output.

    - No **loop** ("repeat until the answer is good").
    - No **decision** ("if urgent, go this way, otherwise that way").
    - No **state** that lives between steps, no pause for a human.

    Those are the jobs for **LangGraph** (section 11). Chains remain the best tool for short, linear flows.

    | Need | Tool |
    |---|---|
    | Fixed sequence of steps, one pass | **LCEL chain** (`\|`) |
    | The model decides which tools to call | **`create_agent`** |
    | Branches, loops, state, approvals | **LangGraph** |

    ⚠️ Deprecated: `LLMChain`, `SequentialChain`, `ConversationChain`, `RetrievalQA` → LCEL chains, `create_agent` or a LangGraph graph.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Summary

    - **LCEL:** join steps with `|`: `prompt | model | parser`. The result is one **Runnable**.
    - Every part has the same interface: `invoke`, `batch`, `stream` and `async` versions.
    - The last step can be a text parser or `with_structured_output(...)`.
    - A `dict` or `RunnableParallel` runs branches on the same input; `RunnableLambda` adds plain Python.
    - Linear only. For loops, decisions and state use **LangGraph**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Output parsers: the last step of the chain

    A parser takes the model's **`AIMessage`** and returns a Python value. Pick the one that matches the shape you need.

    1. **`StrOutputParser`**: takes the text.
       - In: `AIMessage(content="Hello")`
       - Out: `"Hello"` (a `str`)
       - Use: plain answers, summaries, translations. The default last step of most chains.

    2. **`JsonOutputParser`**: takes JSON, also when it is wrapped in a Markdown code block.
       - In: `AIMessage(content='```json\n{"topic": "billing", "urgent": true}\n```')`
       - Out: `{"topic": "billing", "urgent": True}` (a `dict`)
       - Use: quick structured output without a fixed schema. Prefer `with_structured_output` when you know the schema.

    3. **`PydanticOutputParser(pydantic_object=Ticket)`**: takes JSON and validates it against a Pydantic class.
       - In: `AIMessage(content='{"topic": "billing", "urgent": true}')`
       - Out: `Ticket(topic='billing', urgent=True)` (a validated object)
       - Use: the same idea as `with_structured_output`, but for models without tool calling. It also adds format instructions to the prompt (`get_format_instructions()`).

    4. **`PydanticToolsParser(tools=[Ticket])`**: takes **tool calls** and returns Pydantic objects.
       - In: `AIMessage(content="\", tool_calls=[{"name": "Ticket", "args": {"topic": "billing", "urgent": True}, "id": "1"}])`
       - Out: `[Ticket(topic='billing', urgent=True)]` (a list)
       - Use: when the model answers through tool calling (e.g. `bind_tools`) and you want typed objects instead of raw dicts.

    5. **`CommaSeparatedListOutputParser`**: takes a comma-separated line.
       - In: `AIMessage(content="boots, cap, paint")`
       - Out: `["boots", "cap", "paint"]` (a `list[str]`)
       - Use: keywords, tags, short lists, quick brainstorming.

    6. **`MarkdownListOutputParser`**: takes a Markdown bullet list.
       - In: `AIMessage(content="- boots\n- cap\n- paint")`
       - Out: `["boots", "cap", "paint"]` (a `list[str]`)
       - Use: lists the model writes in bullets, e.g. steps, options, action items.

    `XMLOutputParser` also exists, but it needs the extra package `defusedxml`. We skip it here.

    Rule of thumb: **plain text → `StrOutputParser`; data you will use in code → a Pydantic class** (through `with_structured_output`, `PydanticOutputParser` or `PydanticToolsParser`).
    """)
    return


if __name__ == "__main__":
    app.run()

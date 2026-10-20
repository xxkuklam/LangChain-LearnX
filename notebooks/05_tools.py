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
    # 5. Tools

    ## Creating custom tools
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What is a tool?

    A tool is a **normal Python function** that we give to the model.

    The model never sees the code. It only sees three things:

    | Part | Where it comes from | What the model uses it for |
    |---|---|---|
    | **name** | function name | to say *which* tool to call |
    | **description** | docstring | to decide *when* to call it |
    | **arguments schema** | type hints (or a Pydantic class) | to know *how* to call it |

    So writing a tool = writing a function **and** explaining it well.

    ### Our running example: customer support

    Three tools for a support assistant:

    - `get_order_status`: look up an order (**read only**, safe)
    - `get_bank_payments`: list the bank records for an invoice (**read only**, safe)
    - `issue_refund`: pay money back (**changes something**, risky)

    **Business rule:** if the bank shows **two payments, each equal to the invoice total**, the invoice was paid twice and the customer should get a refund.
    """)
    return


@app.cell
def _():
    # Fake data (in memory). Invoice number = order ID. Later in the talk this can become a real SQL table.
    ORDERS = {
        "4821": {"customer": "Anne Hansen", "status": "delivered", "total": 1200.0},
        "4822": {"customer": "Anne Hansen", "status": "shipped", "total": 89.9},
        "4823": {"customer": "Ingrid Solberg", "status": "delivered", "total": 1200.0},
        "5010": {"customer": "Lars Berg", "status": "cancelled", "total": 450.0},
    }

    # Records from the bank, keyed by invoice number
    BANK_PAYMENTS = {
        "4821": [  # paid twice: two records, each equal to the invoice total
            {"date": "2026-10-02", "amount": 1200.0, "reference": "Invoice 4821"},
            {"date": "2026-10-03", "amount": 1200.0, "reference": "Invoice 4821"},
        ],
        "4822": [{"date": "2026-10-05", "amount": 89.9, "reference": "Invoice 4822"}],
        "4823": [  # two instalments of 600: NOT a duplicate (together they equal the total)
            {"date": "2026-10-01", "amount": 600.0, "reference": "Invoice 4823"},
            {"date": "2026-10-08", "amount": 600.0, "reference": "Invoice 4823"},
        ],
        "5010": [{"date": "2026-09-20", "amount": 450.0, "reference": "Invoice 5010"}],
    }
    return BANK_PAYMENTS, ORDERS


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The simplest tool: `@tool`

    ```python
    from langchain.tools import tool
    ```

    - **Docstring** = description for the model (write it for the model, not for developers).
    - **Type hints are required**: they define the arguments.
    - Use `snake_case` names (some providers reject spaces and special characters).
    """)
    return


@app.cell
def _(BANK_PAYMENTS, ORDERS):
    from langchain.tools import tool


    @tool
    def get_order_status(order_id: str) -> str:
        """Look up an order by its ID and return the customer, status and invoice total in NOK."""
        order = ORDERS.get(order_id)
        if order is None:
            return f"Order {order_id} not found."
        return (
            f"Order {order_id} for {order['customer']}: status={order['status']}, "
            f"invoice total={order['total']} NOK"
        )


    @tool
    def get_bank_payments(invoice_number: str) -> str:
        """Return the bank records (date, amount in NOK) and the total received for an invoice number.
        Use it to check whether and how many times an invoice was paid, and how much money came in."""
        records = BANK_PAYMENTS.get(invoice_number)
        if not records:
            return f"No bank records for invoice {invoice_number}."
        lines = [f"- {r['date']}: {r['amount']} NOK ({r['reference']})" for r in records]
        total = sum(r["amount"] for r in records)
        return (
            f"{len(records)} bank record(s) for invoice {invoice_number}:\n"
            + "\n".join(lines)
            + f"\nTotal received: {total} NOK"
        )

    return get_bank_payments, get_order_status, tool


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## `@tool` returns an object, not a function

    We can call it ourselves with `.invoke(...)` and, more importantly, **inspect what the model will see**.
    """)
    return


@app.cell
def _(get_bank_payments, get_order_status):
    print(type(get_order_status).__name__)
    print("name:       ", get_order_status.name)
    print("description:", get_order_status.description)
    print("args:       ", get_order_status.args)

    # Call the tool directly (no LLM involved)
    print(get_order_status.invoke({"order_id": "4821"}))
    print(get_order_status.invoke({"order_id": "9999"}))
    print(get_bank_payments.invoke({"invoice_number": "4821"}))
    return


@app.cell(hide_code=True, expand_output=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## A tool is a `Runnable`

    `@tool` wraps our function in a `StructuredTool`. It is a `BaseTool`, which is a `Runnable`: the same building block as models and chains.
    """),
        mo.mermaid(r"""
    flowchart TB
        R["Runnable<br/>(invoke, ainvoke, batch, stream)"] --> RS["RunnableSerializable"]
        RS --> BT["BaseTool<br/>(name, description, args_schema)"]
        BT --> ST["StructuredTool<br/>(what @tool creates)"]
        RS --> M["BaseChatModel<br/>(chat models)"]
    """),
        mo.md(r"""
    | How to run it | Example | Use it for |
    |---|---|---|
    | `.invoke(dict)` | `issue_refund.invoke({"order_id": "4821", "amount": 1200.0, "reason": "duplicate payment"})` | Normal way, arguments are validated |
    | `.ainvoke(dict)` | `await issue_refund.ainvoke({...})` | Async code |
    | `.func(...)` | `issue_refund.func("4821", 1200.0, "duplicate payment")` | The original Python function, e.g. in unit tests (no validation) |
    | `issue_refund(...)` | | **Does not work**: `TypeError: 'StructuredTool' object is not callable` |

    Because it is a `Runnable`, a tool also works in `batch`, `stream` and in chains (`|`). Agents simply call `.invoke` with the arguments the model returns.
    """),
    ])
    return


@app.cell
def _(get_order_status):
    # A tool is not a plain function
    try:
        get_order_status("4821")
    except TypeError as e:
        print("TypeError:", e)

    # The original function is still available
    print(get_order_status.func("4821"))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Better arguments: `args_schema` (Pydantic)

    Type hints give the model argument **names and types**. To explain **what each argument means** and add rules, pass a Pydantic class (same idea as structured output in section 3).

    - `Field(description=...)` tells the model how to fill the argument.
    - `Field(gt=0)` etc. are validated before our code runs.
    """)
    return


@app.cell
def _(ORDERS, tool):
    from pydantic import BaseModel, Field


    class RefundInput(BaseModel):
        order_id: str = Field(description="ID of the order to refund, e.g. '4821'")
        amount: float = Field(gt=0, description="Amount to refund in NOK. Must not exceed the order total.")
        reason: str = Field(description="Short reason for the refund, e.g. 'duplicate payment'")


    @tool(args_schema=RefundInput)
    def issue_refund(order_id: str, amount: float, reason: str) -> str:
        """Refund money to the customer for an order. This moves real money, use it only when the refund is justified."""
        order = ORDERS.get(order_id)
        if order is None:
            return f"Refund failed: order {order_id} not found."
        if amount > order["total"]:
            return f"Refund failed: {amount} NOK is more than the order total ({order['total']} NOK)."
        return f"Refunded {amount} NOK for order {order_id} ({reason})."

    return (issue_refund,)


@app.cell
def _(issue_refund):
    print("name:       ", issue_refund.name)
    print("description:", issue_refund.description)
    print("args:       ", issue_refund.args)
    print("----------")
    print(issue_refund.invoke({"order_id": "4821", "amount": 1200.0, "reason": "duplicate payment"}))
    print(issue_refund.invoke({"order_id": "4821", "amount": 5000.0, "reason": "too much"}))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Tips for writing good tools

    - **One tool = one clear job.** Prefer `get_order_status` over a vague `do_support_stuff`.
    - **Describe it for the model:** when to use it, what it returns, any risk.
    - **Return text (or simple data)** the model can read. Errors too: return a message such as `"Order not found."` so the model can react, instead of crashing.
    - **Validate inputs** (`Field(gt=0)`, `Literal[...]`) and business rules (refund ≤ total).
    - **Do not name arguments `config` or `runtime`**: these names are reserved by LangChain.
    - Customize if needed: `@tool("custom_name", description="...")`.
    """)
    return


@app.cell(hide_code=True, expand_output=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## Tool calling

    **The model does not run tools. It only asks for them.**

    - The model returns a *request*: "please call `get_order_status` with `order_id='4821'`".
    - **Our code** runs the tool and sends the result back.
    - Then the model reads the result and answers (or asks for another tool).
    """),
        mo.mermaid(r"""
    sequenceDiagram
        participant Y as Our code
        participant M as Model
        participant T as Tool (Python function)
        Y->>M: messages + tool definitions
        M-->>Y: AIMessage(tool_calls=[get_order_status(4821)])
        Note over M,T: The model cannot run the tool
        Y->>T: .invoke(tool_call)
        T-->>Y: ToolMessage("Order 4821 ...")
        Y->>M: messages + AIMessage + ToolMessage
        M-->>Y: final answer (or another tool_call)
    """),
    ])
    return


@app.cell
def _():
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv(usecwd=True))  # load API keys from .env
    return


@app.cell
def _(get_bank_payments, get_order_status, issue_refund):
    from langchain.chat_models import init_chat_model

    MODEL = "openai:gpt-5.4-mini"

    tools = [get_order_status, get_bank_payments, issue_refund]
    tools_by_name = {t.name: t for t in tools}

    model = init_chat_model(MODEL)
    model_with_tools = model.bind_tools(tools)  # sends the tool definitions with every request
    return model_with_tools, tools_by_name


@app.cell
def _():
    from langchain.messages import HumanMessage, SystemMessage

    SYSTEM_PROMPT = (
        "You are a customer support assistant. Check the facts with the tools before acting. "
        "An invoice was paid twice only if the bank shows two payments and each equals the invoice total. "
        "In that case refund one payment. Otherwise do not refund."
    )
    USER_MESSAGE = "Anne Hansen reports that her invoice #4821 for 1200 NOK was charged twice. Please sort it out."

    messages = [SystemMessage(SYSTEM_PROMPT), HumanMessage(USER_MESSAGE)]
    return (messages,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 1: ask the model

    Look at `tool_calls`: the model **asks** for tools (here two at once, they are independent). Nothing has been executed yet, so nothing has been checked.
    """)
    return


@app.cell
def _(messages, model_with_tools):
    ai_message_1 = model_with_tools.invoke(messages)

    print("content:   ", repr(ai_message_1))  # text usually empty: the model wants a tool, not to talk
    print("tool_calls:")
    for tool_call in ai_message_1.tool_calls:
        print("--- tool_call ---")
        print("  ", tool_call)
    return (ai_message_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 2: **our code** runs the tool

    The tool call is a dict with `name`, `args` and `id`. Passing it to `.invoke` returns a `ToolMessage` linked to the call by `tool_call_id`.
    """)
    return


@app.cell
def _(ai_message_1, tools_by_name):
    tool_messages_1 = []
    for call_1 in ai_message_1.tool_calls:
        print(call_1)
        tool_messages_1.append(tools_by_name[call_1["name"]].invoke(call_1))

    print('----------')
    for t_m in tool_messages_1:
        print(t_m)
        print('----------')

    for tool_message in tool_messages_1:
        print(type(tool_message).__name__, "->", tool_message.content)
    return (tool_messages_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 3: send the result back

    We append the model's request (`AIMessage`) and the result (`ToolMessage`) to the history and ask again.
    """)
    return


@app.cell
def _(ai_message_1, messages, model_with_tools, tool_messages_1):
    messages_2 = [*messages, ai_message_1, *tool_messages_1]
    ai_message_2 = model_with_tools.invoke(messages_2)

    print("content:   ", repr(ai_message_2.text))
    print("tool_calls:", ai_message_2.tool_calls)
    return ai_message_2, messages_2


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 4: **our code** runs the refund

    The model decided that the invoice was paid twice and asked for `issue_refund`. Again, nothing happens until **we** run it.
    """)
    return


@app.cell
def _(ai_message_2, tools_by_name):
    tool_messages_2 = []
    for call_2 in ai_message_2.tool_calls:
        tool_messages_2.append(tools_by_name[call_2["name"]].invoke(call_2))

    for tool_message_2 in tool_messages_2:
        print(type(tool_message_2).__name__, "->", tool_message_2.content)
    return (tool_messages_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 5: final answer

    We send the refund result back. This time the model has everything it needs and answers with text (`tool_calls` is empty).
    """)
    return


@app.cell
def _(ai_message_2, messages_2, model_with_tools, tool_messages_2):
    messages_3 = [*messages_2, ai_message_2, *tool_messages_2]
    ai_message_3 = model_with_tools.invoke(messages_3)

    print("tool_calls:", ai_message_3.tool_calls)
    print("content:\n", ai_message_3.text)
    return ai_message_3, messages_3


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 6: the whole conversation (our "logs")
    """)
    return


@app.cell
def _(ai_message_3, messages_3):
    for message in [*messages_3, ai_message_3]:
        message.pretty_print()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Takeaways

    - The model **requests** tools (`AIMessage.tool_calls`); **our code executes** them (`ToolMessage`).
    - Every result goes back into the message history, then we ask the model again.
    - The model may ask for **several tools at once** or for another one after seeing a result.
    - Repeating "ask → run tools → ask again" until there are no more `tool_calls` is exactly what an **agent** does.

    **Next:** ReAct and `create_agent`, the loop done for us.
    """)
    return


if __name__ == "__main__":
    app.run()

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
    # 3. Structured output

    ## Pydantic: LLM response → Python class
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The problem

    An LLM answers with **text**. Our code needs **data**: fields, types, allowed values.

    ```text
    "Anna Kowalska reports that her invoice #4821 for 1200 PLN was charged twice. She is very upset."
                                         ↓
    SupportTicket(customer="Anna Kowalska", topic="billing", amount=1200.0, urgent=True)
    ```

    Parsing free text with regex or "please answer in JSON" is fragile. Better: describe the shape once as a **Pydantic class** and let LangChain enforce it.
    """)
    return


@app.cell
def _():
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv(usecwd=True))  # load API keys from .env
    return


@app.cell
def _():
    from typing import Literal

    from pydantic import BaseModel, Field


    class SupportTicket(BaseModel):
        """A customer support ticket extracted from a message."""

        customer: str = Field(description="Full name of the customer")
        topic: Literal["billing", "technical", "account", "other"] = Field(
            description="Main topic of the message"
        )
        amount: float | None = Field(default=None, description="Amount in PLN, if mentioned")
        urgent: bool = Field(description="True if the customer sounds upset or the issue blocks them")

    return (SupportTicket,)


@app.cell
def _(SupportTicket):
    from langchain.chat_models import init_chat_model

    MODEL = "openai:gpt-5.4-mini"
    MESSAGE = (
        "Anna Kowalska reports that her invoice #4821 for 1200 PLN "
        "was charged twice. She is very upset."
    )

    model = init_chat_model(MODEL)
    structured_model = model.with_structured_output(SupportTicket)  # the only new line

    ticket = structured_model.invoke(MESSAGE)

    print(type(ticket)) 
    print(type(ticket).__name__)  # a real SupportTicket object, not text
    print(ticket)
    print(ticket.topic, "|", ticket.amount, "|", ticket.urgent)
    print(ticket.model_dump())  # plain dict, ready for JSON / database
    return MESSAGE, init_chat_model, ticket


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What just happened

    - The Pydantic class (field names, types, `description`s, `Literal` values) is sent to the model as a **schema**.
    - The model fills the schema, LangChain **validates** the result and returns a Python object.
    - `Field(description=...)` is part of the prompt: good descriptions = better extraction.
    - `Literal[...]` limits the answer to allowed values, no more "Billing" vs "billing" surprises.
    """)
    return


@app.cell
def _(MESSAGE, SupportTicket, init_chat_model):
    # Same class, another provider: nothing else changes
    claude_ticket = init_chat_model("anthropic:claude-haiku-5-5").with_structured_output(SupportTicket).invoke(MESSAGE)

    print(claude_ticket)
    return


@app.cell
def _(SupportTicket, ticket):
    # Validation: Pydantic rejects data that does not match the schema
    from pydantic import ValidationError

    try:
        SupportTicket(customer="Bob", topic="shipping", urgent=False)  # "shipping" is not allowed
    except ValidationError as e:
        print(e.errors()[0]["msg"])

    # The result is a normal object: use it in code
    if ticket.urgent:
        print(f"Escalate ticket for {ticket.customer}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Summary

    - **`with_structured_output(MyClass)`** turns an LLM response into a validated Python object.
    - Describe the shape with **Pydantic**: types, `Field(description=...)`, `Literal` for fixed choices.
    - Works the same for every provider that supports it (local models: test first).
    - Typical uses: **data extraction, classification, routing decisions, tool arguments**.
    """)
    return


if __name__ == "__main__":
    app.run()

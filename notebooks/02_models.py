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
    # 2. Models: one interface, any provider

    ## `init_chat_model`: switching OpenAI → Claude at runtime
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The problem

    Every provider has its own SDK, its own classes and its own message format.
    Switching from OpenAI to Anthropic usually means **rewriting code**.

    ## The LangChain answer

    One function, one string `"provider:model"`:

    ```python
    from langchain.chat_models import init_chat_model

    model = init_chat_model("openai:<model-id>")
    model = init_chat_model("anthropic:<model-id>")   # the rest of the code stays the same

    response = model.invoke("Hello!")
    ```

    The rest of the application (`invoke`, `stream`, tools, agents) does not care which provider is behind it.
    """)
    return


@app.cell
def _():
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv(usecwd=True))  # load API keys from .env
    return


@app.cell
def _():
    import os
    from functools import partial

    import anthropic
    import openai

    LIMIT = 10  # how many models to print per provider

    # OpenRouter exposes an OpenAI-compatible API, so we reuse the openai client with a different base_url
    openrouter = partial(
        openai.OpenAI, base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY")
    )

    for provider, client in [
        ("anthropic", anthropic.Anthropic),
        ("openai", openai.OpenAI),
        ("openrouter", openrouter),
    ]:
        try:
            ids = sorted(m.id for m in client().models.list())
            print(f"{provider}: {len(ids)} models, e.g. (first {LIMIT}):")
            for model_id in ids[:LIMIT]:
                print(f"  {provider}:{model_id}")
        except Exception as e:
            print(f"{provider}: error: {e}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Model names change often, so we should not hardcode them in the logic.
    The console above lists models fetched live from each provider: copy a value in the `provider:model` format.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Switching the provider while the app is running

    Same code, same question. Only the `"provider:model"` string changes.
    """)
    return


@app.cell
def _():
    from langchain.chat_models import init_chat_model

    # Model names in one place (pick them from the list above)
    MODELS = [
        "openai:gpt-5.4-mini",
        "anthropic:claude-haiku-5-5",
        "openrouter:anthropic/claude-haiku-5.5",
    ]
    QUESTION = "Explain in two sentences what an AI agent is."

    for name in MODELS:
        try:
            model = init_chat_model(name)  # the only provider-specific line
            response = model.invoke(QUESTION)
            print(f"--- {name} -> {type(model).__name__}")
            print(response.text)
            print("tokens:", response.usage_metadata["total_tokens"])
        except Exception as e:
            print(f"--- {name} -> error: {e}")
    return (QUESTION,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Provider classes in code

    `init_chat_model` is great for switching. When you need **provider-specific features**, use the class directly:

    | Provider | Class | Package |
    |---|---|---|
    | OpenAI | `ChatOpenAI` | `langchain-openai` |
    | Anthropic | `ChatAnthropic` | `langchain-anthropic` |
    | OpenRouter | `ChatOpenRouter` | `langchain-openrouter` |

    All of them are the same kind of object (`BaseChatModel`): `invoke`, `stream`, tools, agents work identically.
    """)
    return


@app.cell
def _(QUESTION):
    from langchain_openai import ChatOpenAI

    openai_model = ChatOpenAI(
        model="gpt-5.4-mini",
        timeout=30,
        max_retries=2,
    )

    openai_response = openai_model.invoke(QUESTION)
    print("ChatOpenAI:", openai_response.text)
    return


@app.cell
def _(QUESTION):
    from langchain_anthropic import ChatAnthropic

    anthropic_model = ChatAnthropic(
        model="claude-haiku-5-5",
        max_tokens=1024,
        timeout=30,
        max_retries=2,
    )

    anthropic_response = anthropic_model.invoke(QUESTION)
    print("ChatAnthropic:", anthropic_response.text)
    return


@app.cell
def _(QUESTION):
    from langchain_openrouter import ChatOpenRouter

    # Model id is vendor/model (no "openrouter:" prefix here)
    openrouter_model = ChatOpenRouter(
        model="anthropic/claude-haiku-5.5",
        max_tokens=1024,
        max_retries=2,
    )

    openrouter_response = openrouter_model.invoke(QUESTION)
    print("ChatOpenRouter:", openrouter_response.text)
    return


if __name__ == "__main__":
    app.run()

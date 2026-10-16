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
    return QUESTION, init_chat_model


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
        # model="anthropic/claude-haiku-5.5",
        model="anthropic/claude-sonnet-5.5",
        max_tokens=1024,
        max_retries=2,
    )

    openrouter_response = openrouter_model.invoke(QUESTION)
    print("ChatOpenRouter:", openrouter_response.text)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Local models with Ollama: setup

    Ollama runs open models on your machine. No API key, no internet needed after the download.

    ### 1. Check how Ollama is installed

    ```bash
    which ollama                  # /usr/local/bin/ollama = desktop app, /opt/homebrew/bin/ollama = brew
    brew list | grep -i ollama    # empty = not installed with brew
    ```

    ### 2. Uninstall

    **Installed with brew:**

    ```bash
    brew services stop ollama     # skip if it was not started as a service
    brew uninstall ollama         # for the desktop app cask: brew uninstall --cask ollama

    # To start ollama now and restart at login:
    brew services start ollama
    # Or, if you don't want/need a background service you can just run:
    OLLAMA_FLASH_ATTENTION="1" OLLAMA_KV_CACHE_TYPE="q8_0" /opt/homebrew/opt/ollama/bin/ollama serve

    ```

    **Installed as the desktop app (Ollama.app):**

    ```bash
    osascript -e 'quit app "Ollama"'
    rm -rf /Applications/Ollama.app
    ```

    **Optional cleanup:** downloaded models live in `~/.ollama` (can be many GB).

    ```bash
    du -sh ~/.ollama              # check the size first
    rm -rf ~/.ollama              # removes ALL downloaded models
    ```

    ### 3. Install with brew

    ```bash
    brew install ollama           # CLI + server
    brew services start ollama    # run the server in the background (or: ollama serve)
    ollama --version
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Local models with Ollama: find, download, chat

    ### 4. Find a model

    There is no search command in the CLI. Browse **https://ollama.com/search** and pick:

    - a **small** model (roughly 1B-8B parameters, a few GB) so it runs on a laptop,
    - the **tools** tag if you want tool calling later in this talk.

    A model name looks like `name:tag`, e.g. `<model>:<size>`. The tag is usually the parameter count.

    ### 5. Download it

    ```bash
    ollama pull <model>:<tag>
    ollama list                   # installed models and their size
    ollama show <model>:<tag>     # parameters, context length, capabilities
    ```

    ### 6. Chat in the terminal

    ```bash
    ollama run <model>:<tag>
    ```

    Type a question and press Enter. Useful commands inside the chat: `/?` (help), `/bye` (exit).

    ### 7. Prove that it works offline

    Turn Wi-Fi off, then run `ollama run <model>:<tag>` again. It still answers: the model runs entirely on your machine.

    ### Handy commands

    | Command | What it does |
    |---|---|
    | `ollama ps` | Models currently loaded in memory |
    | `ollama stop <model>:<tag>` | Unload a model |
    | `ollama rm <model>:<tag>` | Delete a model from disk |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Local model in code: `ChatOllama`

    Same interface as the cloud models. Differences: no API key, and the server must be running (`ollama serve` / `brew services start ollama`).

    Package: `langchain-ollama`. Model name = exactly what `ollama list` shows.
    """)
    return


@app.cell
def _(QUESTION, init_chat_model):
    OLLAMA_MODEL = "qwen3.5:latest"

    # Option 1: init_chat_model with the "ollama:" prefix
    ollama_model_1 = init_chat_model(f"ollama:{OLLAMA_MODEL}", reasoning=False)

    ollama_response_1 = ollama_model_1.invoke(QUESTION)
    print(type(ollama_model_1).__name__, "->", ollama_response_1.text)
    return (OLLAMA_MODEL,)


@app.cell
def _(OLLAMA_MODEL, QUESTION):
    from langchain_ollama import ChatOllama

    # Option 2: the dedicated class (provider-specific parameters, e.g. num_ctx, keep_alive)
    ollama_model_2 = ChatOllama(
        model=OLLAMA_MODEL,
        reasoning=False,  # qwen3.5 is a "thinking" model: skip the hidden reasoning to answer faster
        num_ctx=4096,
        temperature=0,
    )

    ollama_response_2 = ollama_model_2.invoke(QUESTION)
    print("ChatOllama ->", ollama_response_2.text)
    print(ollama_response_2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cloud vs. local: trade-offs

    | | **Cloud** (OpenAI, Anthropic, OpenRouter) | **Local** (Ollama) |
    |---|---|---|
    | **Quality** | Best available models | Smaller open models, usually weaker |
    | **Speed** | Fast, independent of your hardware | Depends on your CPU/GPU and RAM |
    | **Cost** | Pay per token | Free to run, you pay with hardware |
    | **Privacy** | Data leaves your machine | Data stays on your machine |
    | **Offline** | No | Yes |
    | **Setup** | API key | Install, download model (GBs), run server |
    | **Tool calling / structured output** | Reliable | Varies by model, test it |
    | **Scaling** | Handled by the provider | Your problem |

    **Rule of thumb:**

    - **Cloud** for quality and production workloads.
    - **Local** for sensitive data, offline use, experiments and cheap development.
    - **OpenRouter** when you want many providers behind one key.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Summary

    - **`init_chat_model("provider:model")`** gives one interface for every provider: switching is a string change.
    - **Provider classes** (`ChatOpenAI`, `ChatAnthropic`, `ChatOpenRouter`, `ChatOllama`) are the same kind of object, use them for provider-specific parameters.
    - **Model names change often**: keep them in one constant or list them from the provider API.
    - **OpenRouter** = many cloud providers behind one API key.
    - **Ollama** = local, private, offline models with the same code.
    - **Everything else stays the same**: `invoke`, `stream`, tools and agents do not care which model is behind them.
    """)
    return


if __name__ == "__main__":
    app.run()

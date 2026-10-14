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
    # 8. RAG: Retrieval-Augmented Generation

    ## Give the model knowledge it was never trained on
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The problem: the model does not know our data

    An LLM knows what was in its training data. It does **not** know:

    - our **internal documents** (policies, contracts, manuals, wiki),
    - **fresh** information (yesterday's price list),
    - **private** data we must not send to a public training set.

    And we cannot paste everything into the prompt: the **context window is limited** and every token costs money.

    | Option | Idea | Problem |
    |---|---|---|
    | **Paste all documents** into the prompt | Simple | Too big, expensive, slow |
    | **Fine-tune** the model | Teach it our data | Costly, hard to update, can still hallucinate |
    | **RAG** | **Find** the relevant pieces and give only them to the model | Needs a search step |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The idea: an open-book exam

    **RAG = Retrieval-Augmented Generation.**

    A student in an **open-book exam** does not memorise the whole book. They **look up the right page**, read it, and then write the answer.

    1. **Retrieval**: find the pieces of our documents that are relevant to the question.
    2. **Augmented**: add those pieces to the prompt.
    3. **Generation**: the LLM writes the answer **based on them**.

    **Business value:** answers grounded in **our** data, with **sources**, and the knowledge base can be updated **without retraining** anything.
    """)
    return


@app.cell(hide_code=True, expand_output=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## The RAG flow

    Two phases. **Indexing** is done once (and again when documents change). **Querying** happens on every question.
    """),
        mo.mermaid(
            """
            flowchart TB
                subgraph IDX["1. Indexing (offline, once)"]
                    direction LR
                    D1["Source files<br/>PDF, web, DB, wiki"] --> D2["Document Loader"]
                    D2 --> D3["Documents<br/>text + metadata"]
                    D3 --> D4["Text Splitter"]
                    D4 --> D5["Chunks"]
                    D5 --> D6["Embedding model"]
                    D6 --> D7["Vectors"]
                end

                VS[("Vector store")]
                D7 -->|"store chunks + vectors"| VS

                subgraph QRY["2. Querying (online, every question)"]
                    direction LR
                    Q1["User question"] --> Q2["Embedding model<br/>(the same one)"]
                    Q2 --> Q3["Question vector"]
                    Q4["Top-k similar chunks"] --> Q5["Prompt<br/>question + chunks"]
                    Q5 --> Q6["LLM"]
                    Q6 --> Q7["Answer"]
                end

                Q3 -->|"similarity search"| VS
                VS -->|"most similar chunks"| Q4
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The flow in 8 steps

    **Indexing**

    1. **Load** the source files into `Document` objects.
    2. **Split** long documents into small chunks.
    3. **Embed** every chunk: turn the text into a vector of numbers.
    4. **Store** chunks and vectors in a vector store.

    **Querying**

    5. **Embed the question** with the **same** embedding model.
    6. **Search** the vector store for the chunks closest to the question vector.
    7. **Build the prompt**: the question plus the retrieved chunks.
    8. **Ask the LLM** and return the answer (ideally with the sources).

    Now the six building blocks, one by one.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Document

    The basic unit of data in LangChain: **a piece of text plus information about where it came from**.

    ```python
    from langchain_core.documents import Document

    doc = Document(
        page_content="Refunds are possible within 30 days of delivery.",
        metadata={"source": "return-policy.pdf", "page": 3},
    )
    ```

    | Field | Meaning |
    |---|---|
    | `page_content` | The text itself |
    | `metadata` | A dict: file name, page, URL, author, date... |
    | `id` | Optional identifier |

    **Why metadata matters:** it lets us show the **source** of an answer and **filter** the search (e.g. only documents from 2026).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Document Loader

    A **loader reads a source and returns a list of `Document` objects**. It hides the format.

    | Source | Examples |
    |---|---|
    | Files | PDF, Word, Markdown, CSV, plain text |
    | Web | A web page, a sitemap |
    | Services | Confluence, Notion, Google Drive, Slack, SharePoint |
    | Databases | SQL queries, data warehouses |

    ```python
    docs = loader.load()        # -> list[Document]
    ```

    - Loaders come from **integration packages** (`langchain-community` and partner packages). There are hundreds.
    - Loading is the **least glamorous and most important** step: bad text extraction (broken tables, scanned PDFs) means bad answers later.
    - You can also create `Document` objects yourself from any data (a database row, an API response).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Text Splitter

    A whole document is too large to be a good search result. We cut it into **chunks**.

    **Why split?**

    - A chunk must **fit** the prompt together with other chunks.
    - A small chunk about **one topic** matches a question better than a 50-page file.
    - Fewer, more relevant tokens: **cheaper and more accurate** answers.

    ```python
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)     # list[Document] -> list[Document]
    ```

    | Parameter | Meaning |
    |---|---|
    | `chunk_size` | Maximum size of a chunk (in characters) |
    | `chunk_overlap` | How much neighbouring chunks share, so a sentence cut in the middle is not lost |

    `RecursiveCharacterTextSplitter` tries to cut at **paragraphs, then sentences, then words**. Metadata is copied to every chunk.

    **Trade-off:** too small = lost context. Too big = noisy results. Start with 500-1000 characters and **test with real questions**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Text Splitter: what is a chunk?

    A **chunk is a `Document` cut out of a longer `Document`**. There is no separate `Chunk` class: "chunk" is a *role*, not a type.

    ```python
    doc = Document(page_content="<5000 characters of a policy>", metadata={"source": "policy.pdf", "page": 3})

    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents([doc])

    # chunks[0] -> Document(page_content="<the first ~1000 characters>",            metadata={"source": "policy.pdf", "page": 3})
    # chunks[1] -> Document(page_content="<the next ~1000, overlapping with [0]>",  metadata={"source": "policy.pdf", "page": 3})
    ```

    - **Text**: a part of the original text.
    - **Metadata**: copied from the original, so after finding a chunk we still know its **file and page**.
    - `add_start_index=True` also stores the chunk's **position** in the original (`metadata["start_index"]`).
    - **Overlap**: neighbouring chunks share some text, so the same phrase can appear in two chunks.
    - The vector store holds **chunks**, not whole documents: that is why search returns small, precise pieces.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Embedding

    An **embedding** turns text into a **vector**: a list of numbers (hundreds or thousands) that represents its **meaning**.

    - Texts with a **similar meaning** get vectors that are **close** to each other.
    - So we can search by **meaning**, not only by exact words.

    | Text | Close to |
    |---|---|
    | "How do I get my money back?" | "Refunds are possible within 30 days" |
    | "What is the weather in Bergen?" | (nothing in our policy documents) |

    ```python
    from langchain_openai import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings(model="<embedding-model>")
    vector = embeddings.embed_query("How do I get my money back?")     # list[float]
    ```

    - Embeddings come from a **separate embedding model** (not the chat model). Providers: OpenAI, Ollama (local), Hugging Face...
    - **Documents and questions must use the same model**, or the numbers are not comparable.
    - Changing the embedding model means **re-indexing everything**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Vector Store

    A **vector store is a database that keeps chunks together with their vectors and finds the closest ones fast**.

    ```python
    from langchain_core.vectorstores import InMemoryVectorStore

    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(chunks)                                  # embeds and stores
    results = vector_store.similarity_search("refund after 30 days?", k=3)   # -> list[Document]
    ```

    | Store | Type | Use it for |
    |---|---|---|
    | `InMemoryVectorStore` | In memory, built in | Demos, tests |
    | **FAISS** | Local library, files | Fast local search, prototypes |
    | **Chroma** | Local, persistent | Small apps |
    | **pgvector** | A **PostgreSQL** extension | You already run Postgres |
    | Qdrant, Pinecone, others | Dedicated / cloud services | Large scale |

    - `similarity_search_with_score(...)` also returns a **score** (for many stores a **distance**: lower = more similar).
    - Same interface for all stores: switching is a small code change.
    - A vector store is **not** a Runnable: that is the next block's job.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Retriever

    A **retriever is the standard interface "question in, relevant documents out"**.

    ```python
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    docs = retriever.invoke("Can I return a product after 30 days?")     # -> list[Document]
    ```

    | | **Vector store** | **Retriever** |
    |---|---|---|
    | What it is | A database with a search method | An interface: `str -> list[Document]` |
    | Is a Runnable | No | **Yes**: `invoke`, `batch`, `ainvoke`... |
    | Backed by | Vectors | Anything: a vector store, keyword search (BM25), a web search, an API |

    - `search_type`: `"similarity"` (closest), `"mmr"` (closest **and diverse**, avoids 3 near-identical chunks), `"similarity_score_threshold"` (only good-enough matches).
    - `k` = how many chunks to return. More chunks = more context, more tokens, more noise.
    - Because it is a Runnable, a retriever plugs into chains and graphs, and can be wrapped as an **agent tool** (later in this section).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## RAG: building blocks in one table

    | Step | Block | LangChain | Question it answers |
    |---|---|---|---|
    | Data unit | **Document** | `langchain_core.documents.Document` | What is one piece of data? |
    | 1 | **Document Loader** | `...Loader().load()` | How do I read the source? |
    | 2 | **Text Splitter** | `RecursiveCharacterTextSplitter` | How do I cut it into searchable pieces? |
    | 3 | **Embedding** | `OpenAIEmbeddings`, `OllamaEmbeddings` | How do I turn text into meaning-numbers? |
    | 4 | **Vector Store** | `InMemoryVectorStore`, FAISS, pgvector | Where do I keep and search the vectors? |
    | 5 | **Retriever** | `vector_store.as_retriever()` | How does the app ask for relevant pieces? |
    | 6 | **LLM** | `init_chat_model` | Who writes the answer from the pieces? |

    **Next:** the whole pipeline in code, with a small set of real documents.
    """)
    return


if __name__ == "__main__":
    app.run()

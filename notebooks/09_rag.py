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

    - Loaders come from **integration packages** (partner and standalone packages). There are hundreds.
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

    **Next:** the whole pipeline in code, step by step, with the product sheets of a fictional company.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Demo: RAG pipeline step by step

    **Our data:** product sheets of the fictional company **ACME Corp**
    (invisible cap, anti-gravity boots, pocket hole, tunnel paint, instant boulder), one Markdown file per product.

    **Goal:** an assistant that answers questions about these products, **using only these sheets**.

    We build it in small, linear steps. Each step uses the result of the previous one.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 1: load the documents

    A loader reads a source and returns `Document` objects. For plain files the whole job is two lines: **read the text, wrap it in a `Document`**.

    **Why Markdown and not PDF?** These sheets started as PDFs. A PDF is a poor source for RAG: the text has no structure
    and tables and columns get mangled. The usual approach is to **convert the PDF to Markdown first**, e.g. with
    [**Docling**](https://github.com/docling-project/docling) (`langchain-docling` has a ready-made `DoclingLoader`).
    Markdown keeps headings and lists, which makes better chunks. We start from already converted files.

    ⚠️ `PyPDFLoader` and the other loaders from `langchain-community` may be **deprecated soon** (the package is being sunset),
    so we do not use them. New loaders live in standalone packages, see the integrations page.
    """)
    return


@app.cell
def _():
    from pathlib import Path

    from langchain_core.documents import Document

    DATA_DIR = Path(__file__).parent / "static" / "acme-corp-dataset" / "products"
    return DATA_DIR, Document


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### One file first
    """)
    return


@app.cell
def _(DATA_DIR, Document):
    text_cap = (DATA_DIR / "invisible-cap.md").read_text()

    doc_cap = Document(page_content=text_cap, metadata={"source": "invisible-cap.md"})

    print("-------------------------------------------")
    print("page_content (first 300 characters):")
    print(doc_cap.page_content[:300])
    print("-------------------------------------------")

    print("metadata:", doc_cap.metadata)
    print("characters:", len(doc_cap.page_content))
    return (doc_cap,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The `metadata` is ours: we decide what to store. The `source` will let us show **where an answer came from**.

    #### Four files from disk

    The same two lines, repeated for every product sheet.
    """)
    return


@app.cell
def _(DATA_DIR, Document, doc_cap):
    text_boots = (DATA_DIR / "anti-gravity-boots.md").read_text()
    doc_boots = Document(page_content=text_boots, metadata={"source": "anti-gravity-boots.md"})

    text_hole = (DATA_DIR / "pocket-hole.md").read_text()
    doc_hole = Document(page_content=text_hole, metadata={"source": "pocket-hole.md"})

    text_paint = (DATA_DIR / "tunnel-paint.md").read_text()
    doc_paint = Document(page_content=text_paint, metadata={"source": "tunnel-paint.md"})

    documents_disk = [doc_cap, doc_boots, doc_hole, doc_paint]

    print("Documents from disk:", len(documents_disk))
    for _document in documents_disk:
        print(f"- {_document.metadata['source']:<24} {len(_document.page_content)} characters")
    return (documents_disk,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### The fifth file: from Google Docs

    A loader does not care **where** the text comes from. The last sheet lives in a Google Doc shared with "anyone with the link".
    Google can export a Doc as Markdown, so we only need an HTTP request.
    """)
    return


@app.cell
def _(Document, documents_disk):
    import httpx

    GOOGLE_DOC_ID = "1-2Q8V0t3HiN0okKPEc6kXOx3-O7KD_kuk9OgWPutY5M"
    EXPORT_URL = f"https://docs.google.com/document/d/{GOOGLE_DOC_ID}/export?format=md"

    response_boulder = httpx.get(EXPORT_URL, follow_redirects=True)
    response_boulder.raise_for_status()

    doc_boulder = Document(
        page_content=response_boulder.text,
        metadata={"source": "Google Docs: desert-boulder", "url": EXPORT_URL},
    )

    # If Google Docs is unavailable, comment out the lines above and uncomment these (same sheet from disk):
    # text_boulder = (DATA_DIR / "desert-boulder.md").read_text()
    # doc_boulder = Document(page_content=text_boulder, metadata={"source": "desert-boulder.md"})

    documents = documents_disk + [doc_boulder]

    print("Documents in total:", len(documents))
    for _document in documents:
        print(f"- {_document.metadata['source']:<32} {len(_document.page_content)} characters")
    return (documents,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We now have **5 `Document` objects** in the list `documents`: four read from disk, one downloaded from Google Docs.

    **Next step:** split them into chunks.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 2: split the documents into chunks

    Our sheets are short (about 1100-1400 characters), but a real manual has hundreds of pages. The splitter does not care: same code.

    Two parameters decide how the text is cut.

    #### `chunk_size`: how big is one chunk

    The **maximum length** of a chunk. By default it is counted in **characters** (not words, not tokens).
    A chunk can be shorter, never longer (unless a single word is longer than the limit).

    #### `chunk_overlap`: how much neighbouring chunks share

    The **last part of chunk N is repeated at the start of chunk N+1**.

    ```text
    chunk_size = 60, chunk_overlap = 20

    chunk 1:  "Refunds are possible within 30 days of delivery. The product"
    chunk 2:  "The product must be unused and in the original packaging."     <- starts with the end of chunk 1
    chunk 3:  "original packaging. Shipping costs are not refunded."         <- starts with the end of chunk 2
    ```

    **Why overlap?** A sentence or an idea cut exactly on the border would be split between two chunks and **neither would contain it whole**.
    The overlap gives both chunks the context around the cut.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### How to choose `chunk_size` and `chunk_overlap`

    There is no universal value. These rules give a good **starting point**, then you **measure**.

    | Rule | Why |
    |---|---|
    | **One chunk = one idea** (a paragraph or a short section) | The vector represents the *meaning* of the chunk. A chunk mixing five topics matches none of them well |
    | **Start with 500-1000 characters** | Typical for prose, FAQs, policies. Code and tables may need more |
    | **Overlap = 10-20% of `chunk_size`** | Enough to keep a cut sentence, not so much that every chunk repeats the previous one |
    | **Stay far below the embedding model input limit** | Longer text is truncated or rejected |
    | **`k` x `chunk_size` must fit the prompt** | We send `k` chunks to the LLM: 5 chunks of 1000 characters is ~5000 characters of context |
    | **Match the question type** | Precise facts ("what is the price?") like **small** chunks. Summaries and reasoning ("explain the warranty") like **bigger** ones |
    | **Respect the structure** | Markdown with headings can be split **by headings** (`MarkdownHeaderTextSplitter`) so a section is never cut in half |

    **Symptoms**

    | Problem | Probably |
    |---|---|
    | Answers are vague, miss details | Chunks too big (noise, diluted meaning) |
    | Answers lack context, "he", "it" without the subject | Chunks too small |
    | The same sentence appears in many results | Overlap too large |
    | A fact is cut in half at the border | Overlap too small |

    **The real rule:** prepare 10-20 realistic questions, try 2-3 settings, look at **which chunks come back**. Tuning is empirical.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Split with `chunk_size=500` and `chunk_overlap=100`

    Our sheets have 1100-1400 characters, so we use a small `chunk_size` to get a few chunks per sheet and see the effect.

    `add_start_index=True` stores the position of the chunk in the original text.
    """)
    return


@app.cell
def _(documents):
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        add_start_index=True,
    )

    chunks = splitter.split_documents(documents)

    print("Documents before splitting:", len(documents))
    print("Chunks after splitting:", len(chunks))
    return RecursiveCharacterTextSplitter, chunks


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Look at the chunks of one sheet
    """)
    return


@app.cell
def _(chunks):
    chunks_cap = [c for c in chunks if c.metadata["source"] == "invisible-cap.md"]

    for i, chunk in enumerate(chunks_cap):
        print(f"--- chunk {i} | {len(chunk.page_content)} characters | start_index={chunk.metadata['start_index']} | source={chunk.metadata['source']}")
        print(chunk.page_content)
        print()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    - Every chunk is a `Document` with the **metadata copied** from the original, plus `start_index`.
    - `RecursiveCharacterTextSplitter` cuts at paragraph and line breaks first, so chunks start and end at a natural place.
    - Here each section of the sheet fitted in one chunk, so **no overlap was needed** (chunk 1 does not repeat the end of chunk 0).
      The overlap appears only when the splitter has to cut **inside** a long passage.

    #### Overlap in action

    One long paragraph without breaks, cut with `chunk_overlap=0` and with `chunk_overlap=20`:
    """)
    return


@app.cell
def _(RecursiveCharacterTextSplitter):
    text_policy = (
        "Refunds are possible within 30 days of delivery. "
        "The product must be unused and in the original packaging. "
        "Shipping costs are not refunded."
    )

    splitter_no_overlap = RecursiveCharacterTextSplitter(chunk_size=60, chunk_overlap=0)
    splitter_overlap = RecursiveCharacterTextSplitter(chunk_size=60, chunk_overlap=20)

    print("chunk_overlap=0:")
    for _text in splitter_no_overlap.split_text(text_policy):
        print("  ", repr(_text))

    print()
    print("chunk_overlap=20:")
    for _text in splitter_overlap.split_text(text_policy):
        print("  ", repr(_text))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    With overlap, "The product" and "original packaging." appear in **two** chunks.
    Without it, the sentence "The product must be unused..." is torn in half: a question about it could miss both chunks.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Experiment: the same documents, different `chunk_size`

    Three splitters, the same code, only the numbers change (overlap is always 20% of the size).
    """)
    return


@app.cell
def _(RecursiveCharacterTextSplitter, documents):
    splitter_small = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=40)
    splitter_medium = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    splitter_large = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    chunks_small = splitter_small.split_documents(documents)
    chunks_medium = splitter_medium.split_documents(documents)
    chunks_large = splitter_large.split_documents(documents)

    print(f"chunk_size=200  -> {len(chunks_small)} chunks, average {sum(len(c.page_content) for c in chunks_small) // len(chunks_small)} characters")
    print(f"chunk_size=500  -> {len(chunks_medium)} chunks, average {sum(len(c.page_content) for c in chunks_medium) // len(chunks_medium)} characters")
    print(f"chunk_size=1000 -> {len(chunks_large)} chunks, average {sum(len(c.page_content) for c in chunks_large) // len(chunks_large)} characters")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    - **Small chunks**: many, precise, but each one has little context.
    - **Large chunks**: few, rich in context, but each one mixes several topics.
    - We continue with the **500 / 100** chunks.

    **Next step:** turn every chunk into a vector (embedding).
    """)
    return


if __name__ == "__main__":
    app.run()

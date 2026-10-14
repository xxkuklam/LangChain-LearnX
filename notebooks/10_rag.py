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
    mo.vstack([
        mo.md(r"""
    ## Demo: RAG pipeline step by step

    **Our data:** product sheets of the fictional company **ACME Corp**
    (invisible cap, anti-gravity boots, pocket hole, tunnel paint, instant boulder), one Markdown file per product.
    """),
        mo.image(
            src=mo.notebook_dir() / "static" / "acme_rr_coyote.jpeg",
            width=400,
            rounded=True,
            style={"display": "block", "margin": "0 auto"},
        ),
        mo.md(r"""
    **Goal:** an assistant that answers questions about these products, **using only these sheets**.

    We build it in small, linear steps. Each step uses the result of the previous one.
    """),
    ])
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
    return DATA_DIR, Document, Path


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
    chunk_size = 150, chunk_overlap = 30      (the overview of the InvisiCap sheet)

    chunk 1:  "The InvisiCap 3000 is the flagship achievement of ACME Corp's Quantum Physics Division. Visually styled as a classic bowler hat, its lining conceals"
    chunk 2:  "hat, its lining conceals integrated photon-bending micro-emitters. It allows the user to completely disappear from both visible light and infrared"
    chunk 3:  "visible light and infrared spectrums."
    ```

    Chunk 2 **starts with the end of chunk 1**, chunk 3 with the end of chunk 2.

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
    - Overlap is counted in the pieces produced by the separators (paragraphs, lines, words), so with Markdown sections it rarely shows up.

    #### Overlap in action

    One long paragraph (the overview of the InvisiCap sheet) cut with `chunk_overlap=0` and with `chunk_overlap=30`:
    """)
    return


@app.cell
def _(RecursiveCharacterTextSplitter):
    text_overview = (
        "The InvisiCap 3000 is the flagship achievement of ACME Corp\u2019s Quantum Physics Division. "
        "Visually styled as a classic bowler hat, its lining conceals integrated photon-bending micro-emitters. "
        "It allows the user to completely disappear from both visible light and infrared spectrums."
    )

    splitter_no_overlap = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=0)
    splitter_overlap = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=30)

    print("chunk_overlap=0:")
    for _text in splitter_no_overlap.split_text(text_overview):
        print("  ", repr(_text))

    print()
    print("chunk_overlap=30:")
    for _text in splitter_overlap.split_text(text_overview):
        print("  ", repr(_text))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Without overlap the sentence about the lining is **torn in half**: "...its lining conceals" ends one chunk, "integrated photon-bending micro-emitters" starts the next.
    A question about what the lining conceals could miss both chunks.

    With overlap, "hat, its lining conceals" and "visible light and infrared" appear in **two** chunks, so the sentence stays whole in at least one of them.
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 3: embed the chunks

    An **embedding model** reads a text and returns a **vector**: a long list of numbers that encodes its meaning.

    - `embed_documents([...])`: many texts at once, returns one vector per text. We use it for the **chunks**.
    - `embed_query("...")`: one text, returns one vector. We use it for the **question**.
    - Both calls must use **the same model**, otherwise the vectors cannot be compared.
    - It is a **separate model** from the chat model, and it is cheap (we pay per token, but chunks are small).

    Cloud models (OpenAI) and local ones (Ollama, Hugging Face) are used with the same two methods.
    """)
    return


@app.cell
def _():
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv(usecwd=True))  # OPENAI_API_KEY from .env
    return


@app.cell
def _():
    from langchain_openai import OpenAIEmbeddings

    EMBEDDING_MODEL = "text-embedding-3-small"

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    return OpenAIEmbeddings, embeddings


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### What does a vector look like?
    """)
    return


@app.cell
def _(embeddings):
    vector_example = embeddings.embed_query("Can I use the invisible cap in the rain?")

    print("type:", type(vector_example).__name__, "of", type(vector_example[0]).__name__)
    print("length (dimensions):", len(vector_example))
    print("first 50 numbers:", [round(x, 4) for x in vector_example[:50]])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A list of **1536 numbers**. Single numbers mean nothing to us: only the **distance between vectors** is meaningful.

    #### Embed all chunks

    One call, one vector for every chunk.
    """)
    return


@app.cell
def _(chunks, embeddings):
    chunk_texts = [chunk.page_content for chunk in chunks]

    chunk_vectors = embeddings.embed_documents(chunk_texts)

    print("chunks:", len(chunk_texts))
    print("vectors:", len(chunk_vectors), "x", len(chunk_vectors[0]), "numbers")
    return (chunk_vectors,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Search by meaning: by hand

    Next step, a **vector store** will do this for us. Now we do it manually to see there is no magic:

    1. Embed the **question** (with the same model).
    2. Compare its vector with the vector of **every chunk**. OpenAI vectors have length 1, so the
       **dot product is the cosine similarity**: 1.0 = the same meaning, close to 0 = unrelated.
    3. Show the chunks with the highest scores.
    """)
    return


@app.cell
def _(chunk_vectors, chunks, embeddings):
    question_1 = "Can I use the invisible cap in the rain?"

    question_vector_1 = embeddings.embed_query(question_1)

    scores_1 = [sum(q * c for q, c in zip(question_vector_1, vector)) for vector in chunk_vectors]

    ranking_1 = sorted(zip(scores_1, chunks), key=lambda pair: pair[0], reverse=True)

    print("QUESTION:", question_1)
    print()
    for _score, _chunk in ranking_1[:3]:
        print(f"{_score:.3f} | {_chunk.metadata['source']} | {_chunk.page_content[:70]!r}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    All three best chunks come from the **invisible cap** sheet, not from the other four products: the search understood what the question is about.

    Look closer: the chunk that actually answers ("DOES NOT work during heavy rain", in **Safety Instructions**) is only **third**, with 0.415.
    The first one is the start of the sheet (title and overview). That is normal: retrieval is approximate, and this is why we take the **top k** chunks (not just one) and let the LLM read them all.

    #### Another question: a different product
    """)
    return


@app.cell
def _(chunk_vectors, chunks, embeddings):
    question_2 = "How high can I jump with the boots?"

    question_vector_2 = embeddings.embed_query(question_2)

    scores_2 = [sum(q * c for q, c in zip(question_vector_2, vector)) for vector in chunk_vectors]

    ranking_2 = sorted(zip(scores_2, chunks), key=lambda pair: pair[0], reverse=True)

    print("QUESTION:", question_2)
    print()
    for _score, _chunk in ranking_2[:3]:
        print(f"{_score:.3f} | {_chunk.metadata['source']} | {_chunk.page_content[:70]!r}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Bonus: the question in Polish

    The embedding model is multilingual: a question in another language lands near the chunks of the same product.
    """)
    return


@app.cell
def _(chunk_vectors, chunks, embeddings):
    question_3 = "Czy czapka niewidka działa podczas deszczu?"

    question_vector_3 = embeddings.embed_query(question_3)

    scores_3 = [sum(q * c for q, c in zip(question_vector_3, vector)) for vector in chunk_vectors]

    ranking_3 = sorted(zip(scores_3, chunks), key=lambda pair: pair[0], reverse=True)

    print("QUESTION:", question_3)
    print()
    for _score, _chunk in ranking_3[:3]:
        print(f"{_score:.3f} | {_chunk.metadata['source']} | {_chunk.page_content[:70]!r}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    - An embedding is the **meaning of a text as numbers**; similar meaning = vectors close to each other.
    - Searching = embed the question, find the **nearest chunk vectors**.
    - Going through all vectors one by one is fine for 16 chunks. For millions we need an index: that is what a **vector store** is for.

    **Next step:** store the chunks and their vectors in a vector store.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 4: store the chunks in a vector store

    Doing the search by hand (embed, compare with every vector, sort) is exactly what a **vector store** does for us.

    - `add_documents(chunks)`: embeds every chunk with the embedding model and stores text, metadata and vector.
    - `similarity_search(question, k=3)`: embeds the question and returns the `k` nearest chunks as `Document` objects.

    We use `InMemoryVectorStore`: no installation, no server, data lives in memory. Other stores (FAISS, Chroma, pgvector...) have the **same methods**.
    """)
    return


@app.cell
def _(chunks, embeddings):
    from langchain_core.vectorstores import InMemoryVectorStore

    vector_store = InMemoryVectorStore(embeddings)

    chunk_ids = vector_store.add_documents(chunks)

    print("Chunks stored:", len(chunk_ids))
    print("First id:", chunk_ids[0])
    return InMemoryVectorStore, vector_store


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `add_documents` called the embedding model again (it does not know about the vectors we computed by hand). It is cheap here: 16 small chunks.

    #### Search

    The same question as before. Compare with the manual ranking.
    """)
    return


@app.cell
def _(vector_store):
    question_4 = "Can I use the invisible cap in the rain?"

    results_4 = vector_store.similarity_search(question_4, k=3)

    print("QUESTION:", question_4)
    print()
    for _result in results_4:
        print(f"{_result.metadata['source']} | {_result.page_content[:70]!r}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The result is a plain `list[Document]`: the same top 3 chunks as in our manual ranking.

    #### Search with scores
    """)
    return


@app.cell
def _(vector_store):
    results_5 = vector_store.similarity_search_with_score("Can I use the invisible cap in the rain?", k=3)

    for _result, _score in results_5:
        print(f"{_score:.3f} | {_result.metadata['source']} | {_result.page_content[:70]!r}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For this store the score is the **cosine similarity** (higher = closer), the same numbers as our manual dot product.
    In other stores the score may be a **distance** (lower = closer): always check the documentation.

    #### Search with a metadata filter

    The `metadata` we set while loading now pays off: search **only in one product sheet**.
    """)
    return


@app.cell
def _(vector_store):
    results_6 = vector_store.similarity_search(
        "What is the price?",
        k=2,
        filter=lambda document: document.metadata["source"] == "pocket-hole.md",
    )

    for _result in results_6:
        print(f"{_result.metadata['source']} | {_result.page_content[:70]!r}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Look inside the vector store

    `InMemoryVectorStore` can save its content to a JSON file. Open the file in your editor to see **how the data looks in the store**.
    """)
    return


@app.cell
def _(Path, vector_store):
    import json

    DUMP_FILE = Path(__file__).parent / "vector_store.json"

    vector_store.dump(str(DUMP_FILE))

    with open(DUMP_FILE) as file:
        dump = json.load(file)

    print("File:", DUMP_FILE.name, f"({DUMP_FILE.stat().st_size // 1024} KB)")
    print("Entries:", len(dump))
    return (dump,)


@app.cell
def _(dump):
    entry = list(dump.values())[0]

    print("keys:    ", list(entry.keys()))
    print("id:      ", entry["id"])
    print("text:    ", entry["text"][:60].replace("\n", " "), "...")
    print("metadata:", entry["metadata"])
    print("vector:  ", len(entry["vector"]), "numbers, first 5:", [round(x, 4) for x in entry["vector"][:5]])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Each entry is one chunk: an **id**, the **text**, the **metadata** and the **vector** (1536 numbers).
    That is all a vector store keeps. Real databases add an **index** so the search is fast for millions of entries.

    **Next step:** a retriever, and the LLM that writes the answer.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 5: wrap the vector store in a retriever

    A vector store has its own methods (`similarity_search`, `add_documents`...). A **retriever** hides them behind one simple interface:
    **a question (string) in, a list of `Document` out**.

    ```python
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    ```

    Why bother? A retriever is a **Runnable**: it has `invoke`, `batch`, `ainvoke`... like the models and tools we already know.
    That is the shape that chains, graphs and agent tools expect.
    """)
    return


@app.cell
def _(vector_store):
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},
    )

    print("type:", type(retriever).__name__)
    return (retriever,)


@app.cell
def _(retriever):
    docs_1 = retriever.invoke("Can I use the invisible cap in the rain?")

    print("Retrieved:", len(docs_1), "documents")
    for _doc in docs_1:
        print(f"- {_doc.metadata['source']} | {_doc.page_content[:70]!r}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Same three chunks as `similarity_search`: the retriever only wraps it.

    #### It is a Runnable: `batch`

    Several questions in one call, one list of documents per question.
    """)
    return


@app.cell
def _(vector_store):
    retriever_k1 = vector_store.as_retriever(search_kwargs={"k": 1})

    batch_results = retriever_k1.batch([
        "What is the price of the boots?",
        "What are the dangers of the pocket hole?",
        "How long does the tunnel paint need to dry?",
    ])

    for _docs in batch_results:
        print(f"- {_docs[0].metadata['source']} | {_docs[0].page_content[:60]!r}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Search types: `similarity` vs `mmr`

    - **`similarity`**: the `k` closest chunks. They can be near-duplicates of each other.
    - **`mmr`** (maximal marginal relevance): the closest chunk first, then chunks that are close **and different** from those already chosen. `fetch_k` = how many candidates to consider.
    - **`similarity_score_threshold`**: only chunks above a minimum score. **Not every store supports it** (`InMemoryVectorStore` does not).
    """)
    return


@app.cell
def _(vector_store):
    retriever_mmr = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 3, "fetch_k": 10},
    )

    docs_2 = retriever_mmr.invoke("Can I use the invisible cap in the rain?")

    for _doc in docs_2:
        print(f"- {_doc.metadata['source']} | {_doc.page_content[:70]!r}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    MMR replaced the FAQ chunk (too similar to the first one) with a chunk from **another product**.
    With a tiny knowledge base this makes the result worse, with thousands of overlapping chunks it avoids repeating the same fact.
    **We stay with `similarity`.**

    **Next step:** give the retrieved chunks to the LLM and get the answer.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 6: give the chunks to the LLM

    The last two steps of the flow, written as plain, linear code:

    1. **Retrieve** the chunks for the question (the retriever).
    2. **Build the prompt**: instructions + the chunks as *context* + the question.
    3. **Ask the LLM** and print the answer.

    The most important part is the **instruction**: answer *only* from the context, say "I don't know" otherwise, name the source.
    """)
    return


@app.cell
def _():
    from langchain.chat_models import init_chat_model

    MODEL = "openai:gpt-5.4-mini"

    model = init_chat_model(MODEL)

    SYSTEM_PROMPT = (
        "You are a helpful assistant of ACME Corp. "
        "Answer the question using ONLY the context below. "
        "Keep the answer short and name the product sheet (source) you used. "
        "If the answer is not in the context, reply only: I don't know based on the product sheets. "
        "(do not name any source in that case)."
    )
    return MODEL, SYSTEM_PROMPT, model


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Without RAG: the model alone

    The same question, no context.
    """)
    return


@app.cell
def _(model):
    question_7 = "Can I use the invisible cap in the rain?"

    answer_7 = model.invoke(question_7)

    print("QUESTION:", question_7)
    print("ANSWER (no RAG):", answer_7.text)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The model knows nothing about our product: it guesses, or says it cannot know.

    #### With RAG: retrieve, build the prompt, ask
    """)
    return


@app.cell
def _(SYSTEM_PROMPT, model, retriever):
    question_8 = "Can I use the invisible cap in the rain?"

    # 1. Retrieve
    docs_8 = retriever.invoke(question_8)

    # 2. Build the prompt: every chunk with its source, then the question
    context_8 = "\n\n".join(f"[source: {_doc.metadata['source']}]\n{_doc.page_content}" for _doc in docs_8)
    user_message_8 = f"Context:\n{context_8}\n\nQuestion: {question_8}"

    # 3. Ask the LLM
    answer_8 = model.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message_8},
    ])

    print("QUESTION:", question_8)
    print("ANSWER (RAG):", answer_8.text)
    return (user_message_8,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The answer comes from the **Safety Instructions** chunk and names the source.

    ⚠️ **When a RAG answer is wrong, first look at the retrieved chunks.** The model can only use what the retriever found.
    Ask "Can I use the *ACME InvisiCap 3000* in the rain?" and the Safety chunk falls to 5th place: with `k=3` the answer becomes "I don't know".
    Fixes: a bigger `k`, better chunks, better wording of the question.

    #### What did the LLM actually receive?

    No magic: the retrieved chunks are just **text pasted into the prompt**.
    """)
    return


@app.cell
def _(user_message_8):
    print(user_message_8)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### Another product, the same code

    The three steps again, only the question changes.
    """)
    return


@app.cell
def _(SYSTEM_PROMPT, model, retriever):
    question_9 = "How high can I jump with the GraviStop boots and how long do they take to charge?"

    docs_9 = retriever.invoke(question_9)

    context_9 = "\n\n".join(f"[source: {_doc.metadata['source']}]\n{_doc.page_content}" for _doc in docs_9)
    user_message_9 = f"Context:\n{context_9}\n\nQuestion: {question_9}"

    answer_9 = model.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message_9},
    ])

    print("QUESTION:", question_9)
    print("ANSWER (RAG):", answer_9.text)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### A question that is NOT in the documents

    This is where the instruction "answer ONLY from the context" matters.
    """)
    return


@app.cell
def _(SYSTEM_PROMPT, model, retriever):
    question_10 = "What is the price of the ACME Rocket Skates?"

    docs_10 = retriever.invoke(question_10)

    context_10 = "\n\n".join(f"[source: {_doc.metadata['source']}]\n{_doc.page_content}" for _doc in docs_10)
    user_message_10 = f"Context:\n{context_10}\n\nQuestion: {question_10}"

    answer_10 = model.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message_10},
    ])

    print("QUESTION:", question_10)
    print("ANSWER (RAG):", answer_10.text)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The retriever **always** returns the k nearest chunks, even when none is relevant. It is the **prompt** that makes the model admit
    "I don't know" instead of inventing a price. That is the difference between a trustworthy assistant and a confident liar.

    ### RAG pipeline: recap

    | Step | Code |
    |---|---|
    | 1. Load | `Document(page_content=..., metadata=...)` |
    | 2. Split | `RecursiveCharacterTextSplitter(...).split_documents(documents)` |
    | 3. Embed | `OpenAIEmbeddings(model=...)` |
    | 4. Store | `InMemoryVectorStore(embeddings).add_documents(chunks)` |
    | 5. Retrieve | `vector_store.as_retriever(search_kwargs={"k": 3}).invoke(question)` |
    | 6. Generate | prompt = instructions + chunks + question, then `model.invoke(...)` |

    **Next:** the retriever as a **tool** of an agent, so the agent decides *when* to look something up.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Can a better embedding model help?

    The retriever is only as good as the embeddings. Which models are there?

    | Provider | Models | Notes |
    |---|---|---|
    | **OpenAI** | `text-embedding-3-small`, `text-embedding-3-large` | Large = better quality, more dimensions (3072), higher price |
    | **Voyage AI** | `voyage-4-lite`, `voyage-4`, `voyage-4-large`, domain models (code, law, finance) | The provider **recommended by Anthropic**, needs its own API key |
    | **Local** | Ollama, Hugging Face (`OllamaEmbeddings`, `HuggingFaceEmbeddings`) | Free, private, quality depends on the model |

    ⚠️ **Anthropic has no embedding model of its own.** With Claude as the chat model you still need an embedding provider (Anthropic's documentation points to Voyage AI).
    Chat model and embedding model are independent: you can mix them freely.

    #### Test: the question that failed before

    "Can I use the ACME InvisiCap 3000 in the rain?" put the *Safety Instructions* chunk only on the 5th place with `text-embedding-3-small`.
    Same chunks, same question, a bigger embedding model:
    """)
    return


@app.cell
def _(InMemoryVectorStore, OpenAIEmbeddings, chunks, vector_store):
    embeddings_large = OpenAIEmbeddings(model="text-embedding-3-large")

    vector_store_large = InMemoryVectorStore(embeddings_large)
    vector_store_large.add_documents(chunks)

    question_11 = "Can I use the ACME InvisiCap 3000 in the rain?"

    print("QUESTION:", question_11)
    print()
    print("text-embedding-3-small:")
    for _doc, _score in vector_store.similarity_search_with_score(question_11, k=5):
        print(f"  {_score:.3f} | {_doc.metadata['source']} | {_doc.page_content.splitlines()[0][:45]}")

    print()
    print("text-embedding-3-large:")
    for _doc, _score in vector_store_large.similarity_search_with_score(question_11, k=5):
        print(f"  {_score:.3f} | {_doc.metadata['source']} | {_doc.page_content.splitlines()[0][:45]}")
    return (vector_store_large,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    With the larger model the *Safety Instructions* chunk moves from **5th to 3rd place**, so `k=3` is enough.
    A better embedding model helps, but it does not remove the need to **check what the retriever returns**.

    We use the `large` store for the agent below.

    ## RAG as a tool of an agent

    So far we always searched, **whatever the user asked**. Even for "hello" we would pay for an embedding and put random chunks into the prompt.

    Better: give the agent the search as a **tool** and let it decide:

    - a greeting or small talk: no search,
    - a question about a product: search,
    - a question about two products: **search twice**, once per product.

    This is sometimes called *agentic RAG*. The tool is the same kind of `@tool` as in section 4: the retriever inside is just the implementation.
    """)
    return


@app.cell
def _(vector_store_large):
    from langchain.tools import tool

    retriever_large = vector_store_large.as_retriever(search_kwargs={"k": 3})


    @tool
    def search_product_sheets(query: str) -> str:
        """Search the ACME Corp product sheets. Use it for any question about ACME products:
        features, price, specifications, safety, warranty. Query with the product name and the topic."""
        docs = retriever_large.invoke(query)
        return "\n\n".join(f"[source: {doc.metadata['source']}]\n{doc.page_content}" for doc in docs)

    return (search_product_sheets,)


@app.cell
def _(MODEL, search_product_sheets):
    from langchain.agents import create_agent

    agent_rag = create_agent(
        MODEL,
        tools=[search_product_sheets],
        system_prompt=(
            "You are a helpful assistant of ACME Corp. "
            "For questions about ACME products, search the product sheets and answer ONLY from the search results. "
            "If the sheets do not contain the answer, say you do not know. "
            "Keep answers short and name the source sheet. "
            "For greetings and small talk, answer directly without searching."
        ),
    )
    return (agent_rag,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### 1. Small talk: the agent should NOT search
    """)
    return


@app.cell
def _(agent_rag):
    result_12 = agent_rag.invoke({"messages": [{"role": "user", "content": "Hi! What can you help me with?"}]})

    _tool_calls = [call for message in result_12["messages"] for call in getattr(message, "tool_calls", [])]

    print("Number of tool calls:", len(_tool_calls))
    print("AGENT:", result_12["messages"][-1].text)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### 2. A product question: the agent searches
    """)
    return


@app.cell
def _(agent_rag):
    result_13 = agent_rag.invoke(
        {"messages": [{"role": "user", "content": "How long does the battery of the ACME InvisiCap 3000 last?"}]}
    )

    for _message in result_13["messages"]:
        for _call in getattr(_message, "tool_calls", []):
            print("tool call:", _call["name"], _call["args"])
    print("AGENT:", result_13["messages"][-1].text)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The agent **wrote the search query itself**: it did not just paste the user's text.

    ⚠️ That is also a risk. Ask the rain question here and the agent may write "InvisiCap 3000 rain waterproof weather resistance":
    the *Safety* chunk does not appear in the top 3, even with the large model, because it never mentions the product name.
    Typical fixes: put the **product name into every chunk**, a larger `k`, hybrid search (keywords + vectors) or a reranker.

    #### 3. A question about two products
    """)
    return


@app.cell
def _(agent_rag):
    result_14 = agent_rag.invoke(
        {"messages": [{"role": "user", "content": "Which is more expensive: the invisible cap or the anti-gravity boots?"}]}
    )

    for _message in result_14["messages"]:
        for _call in getattr(_message, "tool_calls", []):
            print("tool call:", _call["name"], _call["args"])
    print("AGENT:", result_14["messages"][-1].text)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    One question, **two searches** (one per product). A fixed "retrieve then answer" pipeline would search once with the whole sentence.

    ### RAG as a tool: summary

    | | **Fixed RAG pipeline** | **RAG as a tool (agentic RAG)** |
    |---|---|---|
    | Search | On **every** question | Only **when the agent decides** |
    | Query | The user's text | Written by the agent, can be several |
    | Cost | 1 search + 1 LLM call | Maybe 0 searches, maybe several, 2+ LLM calls |
    | Predictability | High | Lower, the model chooses |
    | Use it for | Simple Q&A over one knowledge base | Assistants with many tools and several knowledge bases |

    **Rule of thumb:** a fixed pipeline when every question needs the documents, a tool when RAG is *one of many* abilities of the agent.
    """)
    return


if __name__ == "__main__":
    app.run()

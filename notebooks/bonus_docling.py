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
    # Bonus: Docling

    ## From a PDF to structured Markdown
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What is Docling?

    Docling is an open-source library that turns documents into a structured form that programs and language models can use.
    It started at IBM Research and is free to use.
    It reads PDF, Word, PowerPoint, Excel, HTML and image files through one common interface.
    Instead of just extracting text, it analyses the layout of every page with AI models.
    It recognises headings, paragraphs, lists, tables, figures and formulas, and keeps their order.
    The result is one `DoclingDocument` object that you can export to Markdown, JSON or HTML.
    Tables are rebuilt as real tables, so you can read them as Markdown or as a pandas DataFrame.
    For scanned documents it can run OCR to read the text from images.
    Docling runs locally, so your documents do not have to leave your machine.
    It is a good first step whenever a language model has to read complicated PDFs.

    **Models on first use:** `DocumentConverter` downloads models (page layout, tables, OCR) from the internet, mostly from Hugging Face.
    The first run needs internet access and can take several minutes. Run it once **before** the talk.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
    ## The problem: a PDF is a picture of a page

    A PDF stores **where to draw characters**, not "this is a heading" or "this is a table".
    Simple text extraction often gives:

    - two columns **mixed into one line**,
    - tables **flattened into a stream of numbers**,
    - headers, footers and page numbers **inside the text**.

    A language model that reads such text sees broken sentences and broken tables.

    **Docling** (open source, from IBM Research) reads the **layout** of a document with AI models and returns a **structured document**: headings, paragraphs, tables, lists, figures.
    """),
        mo.mermaid(
            """
            flowchart LR
                F["PDF, DOCX, PPTX,<br/>XLSX, HTML, images"] --> L["Layout analysis<br/>(AI model)"]
                L --> T["Tables<br/>(structure model)"]
                L --> O["OCR<br/>(scans, optional)"]
                T --> D["DoclingDocument"]
                O --> D
                L --> D
                D --> M["Markdown / JSON / HTML"]
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Setup

    ```bash
    uv add docling
    ```

    - Docling runs **locally**: no document leaves your machine.
    - Our document: the paper *Attention Is All You Need* (15 pages, two columns, tables, formulas).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 1: convert the document

    `DocumentConverter().convert(source)` accepts a path or a URL and returns a result with a `DoclingDocument`.
    The paper is a digital PDF (not a scan), so we switch OCR **off**: it is faster.
    """)
    return


@app.cell
def _():
    import time
    from pathlib import Path

    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    PDF = Path(__file__).parent / "static" / "attention_is_all_you_need.pdf"

    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=PdfPipelineOptions(do_ocr=False))}
    )

    start = time.perf_counter()
    conversion = converter.convert(PDF)
    print(f"Converted in {time.perf_counter() - start:.1f} s, status: {conversion.status.name}")

    doc = conversion.document
    print(type(doc).__name__)
    print("pages:   ", len(doc.pages))
    print("tables:  ", len(doc.tables))
    print("pictures:", len(doc.pictures))
    return (doc,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 2: what is inside the document

    Every element has a **label** (`section_header`, `text`, `table`, `formula`, ...). This is what plain text extraction throws away.
    """)
    return


@app.cell
def _(doc):
    for _index, (_item, _level) in enumerate(doc.iterate_items()):
        if _index >= 12:
            break
        print(f"{_item.label.value:15} | {_item.text[:70]!r}" if hasattr(_item, "text") else f"{_item.label.value:15} |")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 3: export to Markdown

    `export_to_markdown()` turns the document into Markdown: `##` headings, paragraphs, tables as Markdown tables.
    This is the format an LLM reads best.
    """)
    return


@app.cell
def _(doc):
    markdown = doc.export_to_markdown()

    print("characters:", len(markdown))
    print()
    print(markdown[:1200])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Step 4: tables are real tables

    Each table is an object. We can print it as Markdown or get a **pandas DataFrame** (rows and columns, not a stream of numbers).
    """)
    return


@app.cell
def _(doc):
    table = doc.tables[0]

    print(table.export_to_markdown(doc))
    print()
    print(table.export_to_dataframe(doc))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Good to know

    - **Cache the result.** Conversion is the slow part. Save it once and reload it later:
      `doc.save_as_json("doc.json")` and `DoclingDocument.load_from_json("doc.json")` (from `docling_core.types.doc`).
    - **Scans:** keep OCR on (the default). It reads text from images, but is slower.
    - **Other formats:** the same `convert()` works for DOCX, PPTX, XLSX, HTML and images.

    ## Summary

    - Docling **understands the layout**: headings, tables, lists, formulas, not just text.
    - Output: **Markdown**, JSON or a structured document, with tables as real tables.
    """)
    return


if __name__ == "__main__":
    app.run()

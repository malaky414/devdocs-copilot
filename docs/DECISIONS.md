# Design Decisions

## D1-03 Markdown Loader

- The corpus is stored as Markdown files from the FastAPI documentation source.
- The loader keeps the relative source path as metadata.
- Heading hierarchy is extracted from Markdown headings.
- Explicit heading anchors such as `{ #section-name }` are removed from heading titles.
- Headings inside fenced code blocks are ignored.
# Decisions

## 2026-10-07 — Corpus

### Decision

Use the FastAPI documentation as the initial RAG corpus, with Markdown files only.

### Why

* The corpus is technical documentation with real API concepts and many code examples.
* Markdown preserves headings and fenced code blocks, which are useful for structure-aware chunking.
* The corpus is large enough to expose realistic retrieval and chunking problems.
* Keeping the corpus focused on one documentation source makes retrieval evaluation easier to interpret.

### Current corpus

The corpus is stored under:

`data/raw/fastapi/`

Only `.md` files are ingested by the current loader.

---

## 2026-10-07 — Chunking Strategy

### Decision

Use heading-aware, block-based chunking with a target of 1000 tokens and a target overlap of 200 tokens.

### Rules

1. Markdown is first parsed into logical blocks.
2. Headings create hard section boundaries.
3. Section hierarchy is preserved in `section_path` metadata.
4. Fenced code blocks are treated as atomic blocks and are never split.
5. Chunks are built from complete blocks until the target size is reached.
6. Overlap is taken only from recent blocks in the same section.
7. Token counts are measured with `tiktoken` using `cl100k_base`.

### Why

* Heading boundaries keep related documentation content together.
* Preserving section hierarchy gives the retriever useful structural metadata.
* Keeping code blocks intact prevents incomplete or syntactically broken examples.
* A 1000-token target provides enough context for technical explanations without making chunks unnecessarily large.
* Limited same-section overlap helps preserve context across chunk boundaries without mixing unrelated sections.

### Known trade-off

A single code block larger than the target chunk size is intentionally kept as one chunk rather than split. This can create oversize chunks, but preserves code integrity.

### Evaluation

Chunking quality is measured by:

`docs/chunk_quality_report.md`

The report includes chunk counts, token-size distribution, largest chunks, per-file statistics, and sample inspection.

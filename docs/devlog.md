# Devlog

## Day 1 - D1-03

Implemented the Markdown loader for the FastAPI documentation corpus.

### Result

* Loaded 156 Markdown documents.
* Preserved relative source paths.
* Extracted heading hierarchy and line numbers.
* Ignored headings inside fenced code blocks.
* Removed explicit Markdown heading anchors from titles.

\# Development Log



\## 2026-10-07 — Day 1: Foundation and Ingestion



Completed the Day 1 foundation for DevDocs Copilot.



\### Completed



\* Added Markdown corpus loader for FastAPI documentation.

\* Preserved source file paths and heading hierarchy as metadata.

\* Implemented heading-aware block parsing.

\* Implemented chunk generation with:



&#x20; \* 1000-token target size

&#x20; \* 200-token target overlap

&#x20; \* hard heading boundaries

&#x20; \* atomic fenced code blocks

&#x20; \* section metadata

\* Added chunk quality report generation.

\* Generated `docs/chunk\_quality\_report.md`.

\* Created the initial 30-question golden evaluation set in `evals/golden\_set.json`.

\* Added the first architecture decisions to `docs/DECISIONS.md`.



\### Validation



\* Golden set JSON validation: passed.

\* Pytest: `2 passed`.



\### Notes



Running the report script directly initially failed because Python did not resolve the project root as an import path. The script was updated to add the repository root to `sys.path` before importing project modules.



\### Next



Day 2 focuses on retrieval:



\* embeddings

\* Qdrant

\* dense retrieval

\* metadata filtering

\* BM25

\* hybrid retrieval

\* reranking



## 2026-10-08 — Day 2: Retrieval

Completed the retrieval layer for DevDocs Copilot.

### Completed

* Added Qdrant as the local vector database.
* Embedded and indexed 1,901 document chunks.
* Implemented dense retrieval with metadata filtering.
* Implemented BM25 lexical retrieval.
* Implemented Reciprocal Rank Fusion (RRF).
* Implemented Cross-Encoder reranking.
* Added retrieval unit tests.
* Evaluated Dense, BM25, Hybrid RRF, and Hybrid + Rerank on the 30-question golden set.

### Evaluation

| System          | Hit@1 | Hit@3 | Hit@5 |   MRR |
| --------------- | ----: | ----: | ----: | ----: |
| Dense           | 0.333 | 0.600 | 0.667 | 0.483 |
| BM25            | 0.300 | 0.533 | 0.667 | 0.432 |
| Hybrid RRF      | 0.467 | 0.700 | 0.800 | 0.592 |
| Hybrid + Rerank | 0.600 | 0.800 | 0.933 | 0.715 |

### Result

Hybrid + Rerank is currently the best-performing retrieval pipeline.

It retrieved an expected source within the top 5 for 28 of 30 golden questions.

### Validation

Pytest: `12 passed`

Evaluation artifacts:

* `evals/retrieval_metrics.json`
* `docs/retrieval_evaluation.md`

### Next

Day 3 focuses on generation, citations, RAG evaluation, and serving.

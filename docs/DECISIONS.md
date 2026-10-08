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
## 2026-10-08 — Retrieval Strategy

### Decision

Use a hybrid retrieval pipeline consisting of:

1. Dense retrieval using Sentence Transformers embeddings and Qdrant.
2. BM25 lexical retrieval over the same chunks.
3. Reciprocal Rank Fusion (RRF) to combine the two ranked lists.
4. Cross-Encoder reranking of the top-20 fused candidates to produce the final top-5 results.

### Why

Dense retrieval is good at semantic similarity but can miss exact technical identifiers such as class names, function names, and error codes.

BM25 provides lexical matching and complements dense retrieval, but semantic queries can still be ranked poorly when exact terms are missing or phrased differently.

RRF combines both retrieval signals using rank rather than raw scores, avoiding the problem of incompatible score scales.

The Cross-Encoder provides a more detailed query-document relevance score and is applied only to the top-20 candidates to keep the expensive second-stage model limited to a small candidate set.

### Evaluation Evidence

The strategy was evaluated on the 30-question golden set.

| System          | Hit@1 | Hit@3 | Hit@5 |   MRR |
| --------------- | ----: | ----: | ----: | ----: |
| Dense           | 0.333 | 0.600 | 0.667 | 0.483 |
| BM25            | 0.300 | 0.533 | 0.667 | 0.432 |
| Hybrid RRF      | 0.467 | 0.700 | 0.800 | 0.592 |
| Hybrid + Rerank | 0.600 | 0.800 | 0.933 | 0.715 |

Hybrid RRF improved Hit@5 from 0.667 to 0.800 compared with Dense retrieval.

Adding the Cross-Encoder improved Hit@5 further to 0.933 and increased MRR to 0.715.

### Conclusion

The benchmark supports using Hybrid + Rerank as the retrieval pipeline for DevDocs Copilot.

This decision should be revisited if the corpus, embedding model, chunking strategy, or golden evaluation set changes significantly.

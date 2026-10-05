\# DevDocs Copilot



Production-style RAG system over technical documentation.



\## Goal



Build a documentation assistant that can retrieve relevant technical

documentation and answer questions with source citations.



\## Planned Features



\- Markdown document ingestion

\- Metadata-aware chunking

\- Dense retrieval

\- BM25 keyword search

\- Hybrid retrieval with RRF

\- Cross-encoder reranking

\- Answer generation with citations

\- Retrieval and answer evaluation

\- FastAPI service

\- Dockerized deployment



\## Project Structure



```text

src/

├── loaders/

├── chunking/

├── retrieval/

└── generation/



data/

└── raw/



docs/

├── DECISIONS.md

└── devlog.md



evals/

tests/


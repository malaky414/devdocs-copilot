from __future__ import annotations

import os
from pathlib import Path

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

from src.chunking.heading_chunker import build_chunks, parse_markdown_blocks
from src.loaders.markdown_loader import load_markdown_corpus


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAW_ROOT = PROJECT_ROOT / "data" / "raw"
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def ingest_corpus(
    raw_root: str | Path | None = None,
    qdrant_url: str | None = None,
    collection_name: str | None = None,
    model_name: str | None = None,
    batch_size: int = 32,
) -> dict:
    """Rebuild the Qdrant collection from the local Markdown corpus.

    Existing collection data is replaced only after documents have been
    loaded and all embeddings have been computed successfully.
    """
    root = Path(raw_root) if raw_root is not None else DEFAULT_RAW_ROOT
    url = qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333")
    collection = collection_name or os.getenv("QDRANT_COLLECTION_NAME", "fastapi_docs")
    embedding_model = model_name or os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)

    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Markdown corpus directory does not exist: {root}")

    documents = load_markdown_corpus(str(root))
    if not documents:
        raise ValueError(f"No Markdown documents found under: {root}")

    chunk_records: list[dict] = []
    for document in documents:
        blocks = parse_markdown_blocks(document.content)
        chunks = build_chunks(blocks, chunk_size=1000, overlap_tokens=200)
        for chunk_index, chunk in enumerate(chunks):
            metadata = chunk["metadata"]
            chunk_records.append(
                {
                    "content": chunk["content"],
                    "source_path": document.metadata["source_path"],
                    "file_name": document.metadata["file_name"],
                    "section_path": metadata.get("section_path", []),
                    "start_section": metadata.get("start_section"),
                    "chunk_index": chunk_index,
                    "token_count": metadata.get("token_count", 0),
                }
            )

    if not chunk_records:
        raise ValueError("Markdown files were found, but no indexable chunks were produced.")

    model = SentenceTransformer(embedding_model)
    texts = [record["content"] for record in chunk_records]
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        batch_size=batch_size,
        show_progress_bar=False,
    )
    vector_size = int(model.get_sentence_embedding_dimension())

    client = QdrantClient(url=url, timeout=120)
    existing_names = {item.name for item in client.get_collections().collections}

    # Only replace the index once the new content and vectors are ready.
    if collection in existing_names:
        client.delete_collection(collection_name=collection)

    client.create_collection(
        collection_name=collection,
        vectors_config=models.VectorParams(
            size=vector_size,
            distance=models.Distance.COSINE,
        ),
    )

    points = [
        models.PointStruct(id=index + 1, vector=vector.tolist(), payload=record)
        for index, (record, vector) in enumerate(zip(chunk_records, vectors, strict=True))
    ]
    for offset in range(0, len(points), 64):
        client.upsert(
            collection_name=collection,
            points=points[offset : offset + 64],
            wait=True,
        )

    return {
        "status": "completed",
        "collection_name": collection,
        "document_count": len(documents),
        "chunk_count": len(chunk_records),
        "embedding_model": embedding_model,
        "vector_size": vector_size,
        "corpus_path": str(root),
    }

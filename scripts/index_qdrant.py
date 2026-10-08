import sys
import uuid
from pathlib import Path

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.chunking.heading_chunker import build_chunks, parse_markdown_blocks
from src.loaders.markdown_loader import load_markdown_corpus


RAW_ROOT = PROJECT_ROOT / "data" / "raw"
COLLECTION_NAME = "fastapi_docs"
QDRANT_URL = "http://localhost:6333"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 1000
OVERLAP_TOKENS = 200
BATCH_SIZE = 32


def load_chunks() -> list[dict]:
    documents = load_markdown_corpus(str(RAW_ROOT))

    all_chunks = []

    for document in documents:
        blocks = parse_markdown_blocks(document.content)

        chunks = build_chunks(
            blocks,
            chunk_size=CHUNK_SIZE,
            overlap_tokens=OVERLAP_TOKENS,
        )

        for index, chunk in enumerate(chunks):
            chunk["metadata"]["source_path"] = document.metadata[
                "source_path"
            ]
            chunk["metadata"]["chunk_index"] = index

        all_chunks.extend(chunks)

    return all_chunks


def make_point_id(source_path: str, chunk_index: int) -> str:
    value = f"{source_path}:{chunk_index}"

    return str(uuid.uuid5(uuid.NAMESPACE_URL, value))


def main() -> None:
    print("Loading chunks...")
    chunks = load_chunks()

    if not chunks:
        raise RuntimeError("No chunks found.")

    print(f"Loaded {len(chunks)} chunks.")

    print(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    vector_size = model.get_embedding_dimension()
    if vector_size is None:
        raise RuntimeError("Could not determine embedding dimension.")

    print(f"Embedding dimension: {vector_size}")

    client = QdrantClient(
    url=QDRANT_URL,
    timeout=60,
    )

    if client.collection_exists(COLLECTION_NAME):
        print(f"Deleting existing collection: {COLLECTION_NAME}")
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]

        texts = [
            chunk["content"]
            for chunk in batch
        ]

        embeddings = model.encode(
            texts,
            batch_size=BATCH_SIZE,
            show_progress_bar=False,
            normalize_embeddings=True,
        )

        embeddings = np.asarray(embeddings)

        points = []

        for chunk, embedding in zip(batch, embeddings):
            metadata = chunk["metadata"]

            payload = {
                "content": chunk["content"],
                "source_path": metadata["source_path"],
                "section_path": metadata["section_path"],
                "start_section": metadata["start_section"],
                "token_count": metadata["token_count"],
                "chunk_index": metadata["chunk_index"],
            }

            points.append(
                PointStruct(
                    id=make_point_id(
                        metadata["source_path"],
                        metadata["chunk_index"],
                    ),
                    vector=embedding.tolist(),
                    payload=payload,
                )
            )

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

        print(
            f"Indexed {min(start + BATCH_SIZE, len(chunks))}"
            f"/{len(chunks)} chunks"
        )

    info = client.get_collection(COLLECTION_NAME)

    print()
    print("Indexing complete.")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Vectors: {info.points_count}")


if __name__ == "__main__":
    main()
import os
from pathlib import Path
import sys

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class DenseRetriever:
    def __init__(
        self,
        qdrant_url: str | None = None,
        collection_name: str | None = None,
        model_name: str | None = None,
    ) -> None:
        self.client = QdrantClient(
            url=qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333"),
            timeout=60,
        )
        self.collection_name = collection_name or os.getenv(
            "QDRANT_COLLECTION_NAME", "fastapi_docs"
        )
        self.model = SentenceTransformer(
            model_name
            or os.getenv(
                "EMBEDDING_MODEL",
                "sentence-transformers/all-MiniLM-L6-v2",
            )
        )

    def search(
        self,
        query: str,
        limit: int = 5,
        source_path: str | None = None,
        start_section: str | None = None,
    ) -> list[dict]:
        query_vector = self.model.encode(
            query,
            normalize_embeddings=True,
        ).tolist()

        conditions = []
        if source_path is not None:
            conditions.append(
                models.FieldCondition(
                    key="source_path",
                    match=models.MatchValue(value=source_path),
                )
            )
        if start_section is not None:
            conditions.append(
                models.FieldCondition(
                    key="start_section",
                    match=models.MatchValue(value=start_section),
                )
            )

        query_filter = models.Filter(must=conditions) if conditions else None
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        ).points

        return [
            {
                "score": point.score,
                "content": point.payload.get("content", ""),
                "source_path": point.payload.get("source_path"),
                "file_name": point.payload.get("file_name"),
                "section_path": point.payload.get("section_path", []),
                "start_section": point.payload.get("start_section"),
                "chunk_index": point.payload.get("chunk_index"),
                "token_count": point.payload.get("token_count"),
            }
            for point in results
        ]

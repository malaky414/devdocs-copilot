import re
import sys
from pathlib import Path

from rank_bm25 import BM25Okapi

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.chunking.heading_chunker import build_chunks, parse_markdown_blocks
from src.loaders.markdown_loader import load_markdown_corpus


RAW_ROOT = PROJECT_ROOT / "data" / "raw"

CHUNK_SIZE = 1000
OVERLAP_TOKENS = 200


def tokenize(text: str) -> list[str]:
    """
    Lightweight lexical tokenizer.

    Keeps letters, digits, and underscores together so identifiers
    such as HTTPException and function_name remain searchable.
    """
    return re.findall(r"[A-Za-z0-9_]+", text.lower())


class BM25Retriever:
    def __init__(
        self,
        raw_root: Path = RAW_ROOT,
    ) -> None:
        self.chunks = self._load_chunks(raw_root)

        corpus = [
            tokenize(chunk["content"])
            for chunk in self.chunks
        ]

        self.bm25 = BM25Okapi(corpus)

    def _load_chunks(self, raw_root: Path) -> list[dict]:
        documents = load_markdown_corpus(str(raw_root))

        all_chunks = []

        for document in documents:
            blocks = parse_markdown_blocks(document.content)

            chunks = build_chunks(
                blocks,
                chunk_size=CHUNK_SIZE,
                overlap_tokens=OVERLAP_TOKENS,
            )

            for index, chunk in enumerate(chunks):
                chunk["metadata"]["source_path"] = (
                    document.metadata["source_path"]
                )
                chunk["metadata"]["chunk_index"] = index

            all_chunks.extend(chunks)

        return all_chunks

    def search(
        self,
        query: str,
        limit: int = 5,
        source_path: str | None = None,
    ) -> list[dict]:
        query_tokens = tokenize(query)

        if not query_tokens:
            return []

        scores = self.bm25.get_scores(query_tokens)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )

        results = []

        for index in ranked_indices:
            chunk = self.chunks[index]
            metadata = chunk["metadata"]

            if (
                source_path is not None
                and metadata["source_path"] != source_path
            ):
                continue

            results.append(
                {
                    "score": float(scores[index]),
                    "content": chunk["content"],
                    "source_path": metadata["source_path"],
                    "section_path": metadata["section_path"],
                    "start_section": metadata["start_section"],
                    "chunk_index": metadata["chunk_index"],
                    "token_count": metadata["token_count"],
                }
            )

            if len(results) >= limit:
                break

        return results
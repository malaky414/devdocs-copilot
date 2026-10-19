
from __future__ import annotations

from typing import Any


class MultiQueryRetriever:
    """Merge hybrid retrieval results across multiple query variations."""

    def __init__(
        self,
        retriever: Any,
        rrf_k: int = 60,
    ) -> None:
        if rrf_k < 1:
            raise ValueError("rrf_k must be positive")

        self.retriever = retriever
        self.rrf_k = rrf_k

    def search(
        self,
        queries: list[str],
        limit: int = 20,
        per_query_limit: int = 50,
        source_path: str | None = None,
    ) -> list[dict]:
        if limit < 1 or per_query_limit < 1:
            raise ValueError("Retrieval limits must be positive")

        # Remove duplicate queries without changing their order.
        unique_queries = []
        seen_queries = set()

        for query in queries:
            normalized = " ".join(query.split())
            key = normalized.casefold()

            if normalized and key not in seen_queries:
                unique_queries.append(normalized)
                seen_queries.add(key)

        fused: dict[tuple[str, int], dict] = {}

        for query in unique_queries:
            results = self.retriever.search(
                query=query,
                limit=per_query_limit,
                candidate_limit=per_query_limit,
                source_path=source_path,
            )

            for rank, result in enumerate(results, start=1):
                key = (
                    result["source_path"],
                    result["chunk_index"],
                )

                entry = fused.setdefault(
                    key,
                    {
                        "result": dict(result),
                        "multi_query_rrf_score": 0.0,
                        "query_ranks": [],
                    },
                )

                entry["multi_query_rrf_score"] += (
                    1.0 / (self.rrf_k + rank)
                )

                entry["query_ranks"].append(
                    {
                        "query": query,
                        "rank": rank,
                        "hybrid_rrf_score": result.get("rrf_score"),
                    }
                )

        ranked_entries = sorted(
            fused.values(),
            key=lambda entry: entry["multi_query_rrf_score"],
            reverse=True,
        )

        merged_results = []

        for entry in ranked_entries[:limit]:
            item = dict(entry["result"])
            item["multi_query_rrf_score"] = (
                entry["multi_query_rrf_score"]
            )
            item["query_ranks"] = entry["query_ranks"]
            item["matched_query_count"] = len(entry["query_ranks"])

            merged_results.append(item)

        return merged_results

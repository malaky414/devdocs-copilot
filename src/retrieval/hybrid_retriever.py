from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.dense_retriever import DenseRetriever


class HybridRetriever:
    def __init__(
        self,
        dense_retriever: DenseRetriever | None = None,
        bm25_retriever: BM25Retriever | None = None,
        rrf_k: int = 60,
    ) -> None:
        self.dense = dense_retriever or DenseRetriever()
        self.bm25 = bm25_retriever or BM25Retriever()
        self.rrf_k = rrf_k

    @staticmethod
    def _key(result: dict) -> tuple[str, int]:
        return (
            result["source_path"],
            result["chunk_index"],
        )

    def fuse(
        self,
        dense_results: list[dict],
        bm25_results: list[dict],
        limit: int = 5,
    ) -> list[dict]:
        fused = {}
        result_data = {}

        for rank, result in enumerate(dense_results, start=1):
            key = self._key(result)

            fused.setdefault(
                key,
                {
                    "rrf_score": 0.0,
                    "dense_rank": None,
                    "bm25_rank": None,
                },
            )

            fused[key]["rrf_score"] += (
                1.0 / (self.rrf_k + rank)
            )
            fused[key]["dense_rank"] = rank
            result_data[key] = result

        for rank, result in enumerate(bm25_results, start=1):
            key = self._key(result)

            fused.setdefault(
                key,
                {
                    "rrf_score": 0.0,
                    "dense_rank": None,
                    "bm25_rank": None,
                },
            )

            fused[key]["rrf_score"] += (
                1.0 / (self.rrf_k + rank)
            )
            fused[key]["bm25_rank"] = rank
            result_data[key] = result

        ranked_keys = sorted(
            fused,
            key=lambda key: fused[key]["rrf_score"],
            reverse=True,
        )

        results = []

        for key in ranked_keys[:limit]:
            result = dict(result_data[key])
            fusion_data = fused[key]

            result["rrf_score"] = fusion_data["rrf_score"]
            result["dense_rank"] = fusion_data["dense_rank"]
            result["bm25_rank"] = fusion_data["bm25_rank"]

            results.append(result)

        return results

    def search(
        self,
        query: str,
        limit: int = 5,
        candidate_limit: int = 20,
        source_path: str | None = None,
    ) -> list[dict]:
        dense_results = self.dense.search(
            query=query,
            limit=candidate_limit,
            source_path=source_path,
        )

        bm25_results = self.bm25.search(
            query=query,
            limit=candidate_limit,
            source_path=source_path,
        )

        return self.fuse(
            dense_results=dense_results,
            bm25_results=bm25_results,
            limit=limit,
        )
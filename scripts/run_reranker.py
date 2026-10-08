import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.reranker import CrossEncoderReranker


def print_results(
    title: str,
    results: list[dict],
) -> None:
    print(f"\n=== {title} ===")

    for index, result in enumerate(results, start=1):
        section = " > ".join(result["section_path"])

        print(
            f"\n{index}. "
            f"reranker={result.get('reranker_score', 0):.4f} "
            f"rrf={result.get('rrf_score', 0):.5f}\n"
            f"   file={result['source_path']}\n"
            f"   section={section or '(root)'}\n"
            f"   text={result['content'][:250].replace(chr(10), ' ')}..."
        )


def main() -> None:
    hybrid = HybridRetriever()

    reranker = CrossEncoderReranker()

    query = "How do I define a path parameter in FastAPI?"

    candidates = hybrid.search(
        query=query,
        limit=20,
        candidate_limit=20,
    )

    print_results(
        "Hybrid Top-20",
        candidates[:5],
    )

    reranked = reranker.rerank(
        query=query,
        candidates=candidates,
        limit=5,
    )

    print_results(
        "Reranked Top-5",
        reranked,
    )


if __name__ == "__main__":
    main()
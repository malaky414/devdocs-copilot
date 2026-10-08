import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.retrieval.bm25_retriever import BM25Retriever


def print_results(title: str, results: list[dict]) -> None:
    print(f"\n=== {title} ===")

    for index, result in enumerate(results, start=1):
        section = " > ".join(result["section_path"])

        print(
            f"\n{index}. score={result['score']:.4f}\n"
            f"   file={result['source_path']}\n"
            f"   section={section or '(root)'}\n"
            f"   text={result['content'][:250].replace(chr(10), ' ')}..."
        )


def main() -> None:
    retriever = BM25Retriever()

    query = "How do I define a path parameter in FastAPI?"

    results = retriever.search(
        query=query,
        limit=5,
    )

    print_results(
        "BM25 Search",
        results,
    )

    exact_query = "HTTPException"

    exact_results = retriever.search(
        query=exact_query,
        limit=5,
    )

    print_results(
        "BM25 Exact-Term Search",
        exact_results,
    )


if __name__ == "__main__":
    main()
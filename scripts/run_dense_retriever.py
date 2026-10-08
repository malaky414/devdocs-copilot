import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.retrieval.dense_retriever import DenseRetriever


def print_results(title: str, results: list[dict]) -> None:
    print(f"\n=== {title} ===")

    for index, result in enumerate(results, start=1):
        section = " > ".join(result["section_path"])

        print(
            f"\n{index}. score={result['score']:.4f}\n"
            f"   file={result['source_path']}\n"
            f"   section={section or '(root)'}\n"
            f"   tokens={result['token_count']}\n"
            f"   text={result['content'][:250].replace(chr(10), ' ')}..."
        )


def main() -> None:
    retriever = DenseRetriever()

    query = "How do I define a path parameter in FastAPI?"

    results = retriever.search(
        query=query,
        limit=5,
    )

    print_results("Dense Search", results)

    filtered_results = retriever.search(
        query=query,
        limit=5,
        source_path="fastapi/tutorial/path-params.md",
    )

    print_results(
        "Dense Search + source_path filter",
        filtered_results,
    )


if __name__ == "__main__":
    main()
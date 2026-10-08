import json
import sys
from pathlib import Path
from statistics import mean

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluation.metrics import hit_at_k, reciprocal_rank
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.dense_retriever import DenseRetriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.reranker import CrossEncoderReranker


GOLDEN_SET_PATH = PROJECT_ROOT / "evals" / "golden_set.json"
JSON_OUTPUT_PATH = PROJECT_ROOT / "evals" / "retrieval_metrics.json"
MD_OUTPUT_PATH = PROJECT_ROOT / "docs" / "retrieval_evaluation.md"

CANDIDATE_LIMIT = 20
FINAL_LIMIT = 5


def load_golden_set() -> list[dict]:
    with GOLDEN_SET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def evaluate_system(
    all_results: dict[str, list[list[dict]]],
    golden_set: list[dict],
) -> dict:
    metrics = {}

    for system_name, system_results in all_results.items():
        metrics[system_name] = {}

        for k in [1, 3, 5]:
            hits = [
                hit_at_k(
                    results,
                    item["expected_source_files"],
                    k,
                )
                for results, item in zip(system_results, golden_set)
            ]

            metrics[system_name][f"hit@{k}"] = mean(hits)

        reciprocal_ranks = [
            reciprocal_rank(
                results,
                item["expected_source_files"],
            )
            for results, item in zip(system_results, golden_set)
        ]

        metrics[system_name]["mrr"] = mean(reciprocal_ranks)

    return metrics


def main() -> None:
    golden_set = load_golden_set()

    print(f"Loaded {len(golden_set)} golden questions.")

    dense = DenseRetriever()
    bm25 = BM25Retriever()

    hybrid = HybridRetriever(
        dense_retriever=dense,
        bm25_retriever=bm25,
    )

    reranker = CrossEncoderReranker()

    dense_all = []
    bm25_all = []
    hybrid_all = []
    reranked_all = []

    for index, item in enumerate(golden_set, start=1):
        query = item["question"]

        print(
            f"\n[{index}/{len(golden_set)}] {query}"
        )

        dense_results = dense.search(
            query=query,
            limit=CANDIDATE_LIMIT,
        )

        bm25_results = bm25.search(
            query=query,
            limit=CANDIDATE_LIMIT,
        )

        hybrid_results = hybrid.fuse(
            dense_results=dense_results,
            bm25_results=bm25_results,
            limit=CANDIDATE_LIMIT,
        )

        reranked_results = reranker.rerank(
            query=query,
            candidates=hybrid_results,
            limit=FINAL_LIMIT,
        )

        dense_all.append(dense_results[:FINAL_LIMIT])
        bm25_all.append(bm25_results[:FINAL_LIMIT])
        hybrid_all.append(hybrid_results[:FINAL_LIMIT])
        reranked_all.append(reranked_results)

    all_results = {
        "Dense": dense_all,
        "BM25": bm25_all,
        "Hybrid RRF": hybrid_all,
        "Hybrid + Rerank": reranked_all,
    }

    metrics = evaluate_system(
        all_results,
        golden_set,
    )

    JSON_OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    JSON_OUTPUT_PATH.write_text(
        json.dumps(
            {
                "golden_questions": len(golden_set),
                "candidate_limit": CANDIDATE_LIMIT,
                "final_limit": FINAL_LIMIT,
                "metrics": metrics,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    lines = [
        "# Retrieval Evaluation",
        "",
        f"- Golden questions: **{len(golden_set)}**",
        f"- Candidate limit: **{CANDIDATE_LIMIT}**",
        f"- Final limit: **{FINAL_LIMIT}**",
        "",
        "## Results",
        "",
        "| System | Hit@1 | Hit@3 | Hit@5 | MRR |",
        "|---|---:|---:|---:|---:|",
    ]

    for system_name, system_metrics in metrics.items():
        lines.append(
            f"| {system_name} | "
            f"{system_metrics['hit@1']:.3f} | "
            f"{system_metrics['hit@3']:.3f} | "
            f"{system_metrics['hit@5']:.3f} | "
            f"{system_metrics['mrr']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Metric Definitions",
            "",
            "- **Hit@k**: fraction of questions where an expected source file appears within the top-k results.",
            "- **MRR**: mean reciprocal rank of the first result whose source file is expected.",
            "",
            "## Retrieval Pipeline",
            "",
            "```text",
            "Dense Top-20 ─────┐",
            "                  ├──> RRF Top-20 ──> Cross-Encoder ──> Top-5",
            "BM25 Top-20 ──────┘",
            "```",
            "",
        ]
    )

    MD_OUTPUT_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print()
    print("Evaluation complete.")
    print(f"JSON: {JSON_OUTPUT_PATH}")
    print(f"Markdown: {MD_OUTPUT_PATH}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from statistics import mean
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from src.evaluation.metrics import hit_at_k, reciprocal_rank
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.dense_retriever import DenseRetriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.multi_query_retriever import MultiQueryRetriever
from src.retrieval.query_expander import QueryExpander
from src.retrieval.reranker import CrossEncoderReranker


GOLDEN_SET_PATH = PROJECT_ROOT / "evals" / "golden_set.json"
CACHE_PATH = PROJECT_ROOT / "evals" / "query_expansion_cache.json"

JSON_OUTPUT_PATH = (
    PROJECT_ROOT / "evals" / "retrieval_metrics_multi_query.json"
)
MD_OUTPUT_PATH = (
    PROJECT_ROOT / "docs" / "retrieval_evaluation_multi_query.md"
)

CACHE_VERSION = 1
CANDIDATE_LIMIT = 20
PER_QUERY_LIMIT = 50
FINAL_LIMIT = 5


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def load_expansion_cache() -> dict:
    if not CACHE_PATH.exists():
        return {
            "version": CACHE_VERSION,
            "expansions": {},
        }

    try:
        cache = load_json(CACHE_PATH)
    except (OSError, json.JSONDecodeError):
        print("Warning: expansion cache is unreadable; starting fresh.")
        return {
            "version": CACHE_VERSION,
            "expansions": {},
        }

    if (
        not isinstance(cache, dict)
        or cache.get("version") != CACHE_VERSION
        or not isinstance(cache.get("expansions"), dict)
    ):
        print("Warning: expansion cache version mismatch; starting fresh.")
        return {
            "version": CACHE_VERSION,
            "expansions": {},
        }

    return cache


def create_query_expander() -> QueryExpander:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing from .env")

    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        temperature=0,
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    return QueryExpander(llm=llm, max_variants=3)


def get_expansions(
    question: str,
    cache: dict,
    expander: QueryExpander | None,
) -> tuple[list[str], QueryExpander | None]:
    cached = cache["expansions"].get(question)

    if (
        isinstance(cached, list)
        and cached
        and all(isinstance(item, str) and item.strip() for item in cached)
    ):
        return cached, expander

    if expander is None:
        expander = create_query_expander()

    queries = expander.expand(question)

    if not queries:
        queries = [question]

    cache["expansions"][question] = queries

    # Save immediately so an interruption does not lose prior work.
    save_json(CACHE_PATH, cache)

    return queries, expander


def evaluate_system(
    all_results: dict[str, list[list[dict]]],
    golden_set: list[dict],
) -> dict:
    metrics = {}

    for system_name, system_results in all_results.items():
        metrics[system_name] = {}

        for k in (1, 3, 5):
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


def source_paths(results: list[dict]) -> list[str]:
    return [item.get("source_path", "unknown") for item in results]


def main() -> None:
    golden_set = load_json(GOLDEN_SET_PATH)
    cache = load_expansion_cache()

    missing = [
        item["question"]
        for item in golden_set
        if item["question"] not in cache["expansions"]
    ]

    print(f"Golden questions: {len(golden_set)}")
    print(f"Cached expansions: {len(golden_set) - len(missing)}")
    print(f"Questions needing expansion: {len(missing)}")

    # Preserve previous evaluation files; this run writes new output paths.
    save_json(CACHE_PATH, cache)

    dense = DenseRetriever()
    bm25 = BM25Retriever()

    hybrid = HybridRetriever(
        dense_retriever=dense,
        bm25_retriever=bm25,
    )

    multi_query = MultiQueryRetriever(retriever=hybrid)
    reranker = CrossEncoderReranker()

    expander = None

    all_results: dict[str, list[list[dict]]] = {
        "Dense": [],
        "BM25": [],
        "Hybrid RRF": [],
        "Hybrid + Rerank": [],
        "Multi-Query Hybrid + Rerank": [],
    }

    per_question = []

    for index, item in enumerate(golden_set, start=1):
        question = item["question"]

        print(f"\n[{index}/{len(golden_set)}] {question}")

        queries, expander = get_expansions(
            question,
            cache,
            expander,
        )

        # Original-query baselines.
        dense_results = dense.search(
            query=question,
            limit=CANDIDATE_LIMIT,
        )

        bm25_results = bm25.search(
            query=question,
            limit=CANDIDATE_LIMIT,
        )

        hybrid_results = hybrid.fuse(
            dense_results=dense_results,
            bm25_results=bm25_results,
            limit=CANDIDATE_LIMIT,
        )

        baseline_reranked = reranker.rerank(
            query=question,
            candidates=hybrid_results,
            limit=FINAL_LIMIT,
        )

        # New pipeline: expand, retrieve per query, fuse, then rerank.
        multi_query_candidates = multi_query.search(
            queries=queries,
            limit=CANDIDATE_LIMIT,
            per_query_limit=PER_QUERY_LIMIT,
        )

        multi_query_reranked = reranker.rerank(
            query=question,
            candidates=multi_query_candidates,
            limit=FINAL_LIMIT,
        )

        all_results["Dense"].append(dense_results[:FINAL_LIMIT])
        all_results["BM25"].append(bm25_results[:FINAL_LIMIT])
        all_results["Hybrid RRF"].append(hybrid_results[:FINAL_LIMIT])
        all_results["Hybrid + Rerank"].append(baseline_reranked)
        all_results["Multi-Query Hybrid + Rerank"].append(
            multi_query_reranked
        )

        expected = item["expected_source_files"]

        per_question.append(
            {
                "id": item.get("id", f"q{index:02d}"),
                "question": question,
                "expected_source_files": expected,
                "queries_used": queries,
                "baseline_top5": source_paths(baseline_reranked),
                "multi_query_top5": source_paths(multi_query_reranked),
                "baseline_hit_at_5": hit_at_k(
                    baseline_reranked,
                    expected,
                    5,
                ),
                "multi_query_hit_at_5": hit_at_k(
                    multi_query_reranked,
                    expected,
                    5,
                ),
            }
        )

        print("Queries used:", len(queries))
        print(
            "Baseline Hit@5:",
            per_question[-1]["baseline_hit_at_5"],
        )
        print(
            "Multi-Query Hit@5:",
            per_question[-1]["multi_query_hit_at_5"],
        )

    metrics = evaluate_system(all_results, golden_set)

    output = {
        "golden_questions": len(golden_set),
        "candidate_limit": CANDIDATE_LIMIT,
        "per_query_candidate_limit": PER_QUERY_LIMIT,
        "final_limit": FINAL_LIMIT,
        "cache_version": CACHE_VERSION,
        "metrics": metrics,
        "per_question": per_question,
    }

    save_json(JSON_OUTPUT_PATH, output)

    lines = [
        "# Retrieval Evaluation: Multi-Query",
        "",
        f"- Golden questions: **{len(golden_set)}**",
        f"- Hybrid candidate limit: **{CANDIDATE_LIMIT}**",
        f"- Per-query candidate limit: **{PER_QUERY_LIMIT}**",
        f"- Final limit: **{FINAL_LIMIT}**",
        f"- Cached question expansions: **{len(cache['expansions'])}**",
        "",
        "## Results",
        "",
        "| System | Hit@1 | Hit@3 | Hit@5 | MRR |",
        "|---|---:|---:|---:|---:|",
    ]

    for system_name, values in metrics.items():
        lines.append(
            f"| {system_name} | "
            f"{values['hit@1']:.3f} | "
            f"{values['hit@3']:.3f} | "
            f"{values['hit@5']:.3f} | "
            f"{values['mrr']:.3f} |"
        )

    baseline = metrics["Hybrid + Rerank"]
    expanded = metrics["Multi-Query Hybrid + Rerank"]

    lines.extend(
        [
            "",
            "## Change vs. Hybrid + Rerank",
            "",
            "| Metric | Baseline | Multi-Query | Delta |",
            "|---|---:|---:|---:|",
        ]
    )

    for key in ("hit@1", "hit@3", "hit@5", "mrr"):
        delta = expanded[key] - baseline[key]
        lines.append(
            f"| {key} | {baseline[key]:.3f} | "
            f"{expanded[key]:.3f} | {delta:+.3f} |"
        )

    lines.extend(
        [
            "",
            "## Metric Definitions",
            "",
            "- **Hit@k**: fraction of questions with an expected source file in the top-k.",
            "- **MRR**: mean reciprocal rank of the first expected source file.",
            "",
            "This is retrieval evaluation, not a direct measure of answer "
            "faithfulness or factual correctness.",
            "",
        ]
    )

    MD_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    MD_OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print("\nEvaluation complete.")
    print(f"JSON: {JSON_OUTPUT_PATH}")
    print(f"Markdown: {MD_OUTPUT_PATH}")
    print(f"Expansion cache: {CACHE_PATH}")


if __name__ == "__main__":
    main()

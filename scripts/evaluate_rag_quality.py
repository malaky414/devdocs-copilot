from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import instructor
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from openai import AsyncOpenAI, RateLimitError
from ragas.llms.base import InstructorLLM
from ragas.metrics.collections import Faithfulness

from src.generation.answer_service import DevDocsAnswerService

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

GOLDEN_SET_PATH = PROJECT_ROOT / "evals" / "golden_set.json"
CACHE_PATH = PROJECT_ROOT / "evals" / "rag_quality_cache.json"
OUTPUT_PATH = PROJECT_ROOT / "evals" / "rag_quality_metrics.json"

# Bump this when cache record semantics change so stale scores aren't reused.
CACHE_VERSION = 2
REFUSAL_ANSWER = (
    "I don't have a reliable answer based on the available documentation."
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def create_groq_chat() -> ChatOpenAI:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing from the local .env file.")

    return ChatOpenAI(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        temperature=0,
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )


def load_cache() -> dict[str, Any]:
    if CACHE_PATH.exists():
        try:
            cache = load_json(CACHE_PATH)
            if (
                isinstance(cache, dict)
                and cache.get("version") == CACHE_VERSION
                and isinstance(cache.get("samples"), dict)
            ):
                return cache
        except (OSError, json.JSONDecodeError):
            print("Cache unreadable; creating a new one.")

    return {"version": CACHE_VERSION, "samples": {}}


def is_refusal(answer: str) -> bool:
    normalized = " ".join(answer.casefold().split())
    refusal = " ".join(REFUSAL_ANSWER.casefold().split())
    return normalized == refusal or refusal in normalized


def build_output(results: list[dict[str, Any]], model_name: str) -> dict[str, Any]:
    scores = [
        record["faithfulness"]
        for record in results
        if isinstance(record.get("faithfulness"), (int, float))
        and not isinstance(record.get("faithfulness"), bool)
    ]
    return {
        "metric": "faithfulness",
        "model": model_name,
        "questions_evaluated": len(results),
        "scored_questions": len(scores),
        "abstained_questions": sum(
            record.get("evaluation_status") == "abstained" for record in results
        ),
        "mean_faithfulness": sum(scores) / len(scores) if scores else None,
        "results": results,
    }


def make_record(
    question_id: str,
    question: str,
    answer: str,
    score: float | None,
    evaluation_status: str,
    evaluation_error: str | None,
    response: dict[str, Any],
    contexts: list[str],
) -> dict[str, Any]:
    return {
        "id": question_id,
        "question": question,
        "answer": answer,
        "faithfulness": score,
        "evaluation_status": evaluation_status,
        "evaluation_error": evaluation_error,
        "sources": [
            {
                "id": source.get("id"),
                "file_name": source.get("file_name"),
                "source_path": source.get("source_path"),
                "headings": source.get("headings", []),
            }
            for source in response.get("sources", [])
        ],
        # Preserve the actual evidence so a failed scoring attempt can be retried
        # without another generation call.
        "retrieved_contexts": contexts,
        "retrieval_metadata": response.get("retrieval_metadata", {}),
        "citation_validation": response.get("citation_validation", {}),
    }


def evaluate_faithfulness(
    metric: Faithfulness,
    question: str,
    answer: str,
    contexts: list[str],
) -> tuple[float | None, str, str | None]:
    if is_refusal(answer):
        return None, "abstained", None

    try:
        result = metric.score(
            user_input=question,
            response=answer,
            retrieved_contexts=contexts,
        )
        return float(result.value), "complete", None
    except RateLimitError as exc:
        return None, "skipped_rate_limit", str(exc)
    except Exception as exc:
        # Keep a generated answer even if Ragas can't parse/score the response.
        return None, "evaluation_failed", f"{type(exc).__name__}: {exc}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate DevDocs Copilot answer faithfulness with Ragas."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1,
        help="Number of golden questions to evaluate (default: 1)",
    )
    parser.add_argument(
    "--start",
    type=int,
    default=0,
    help="Zero-based index of the first golden question to evaluate",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Regenerate answers instead of reusing the cache",
    )
    args = parser.parse_args()
    if args.limit < 1:
        raise ValueError("--limit must be at least 1")
    if args.start < 0:
        raise ValueError("--start must be non-negative")
    golden_set = load_json(GOLDEN_SET_PATH)

    if args.start >= len(golden_set):
        raise ValueError(
            f"--start must be less than the number of questions ({len(golden_set)})"
        )

    selected_questions = golden_set[args.start : args.start + args.limit]
    model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    generator_llm = create_groq_chat()
    service = DevDocsAnswerService(llm=generator_llm)

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing from the local .env file.")

    evaluator_client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )
    structured_client = instructor.from_openai(
        evaluator_client,
        mode=instructor.Mode.MD_JSON,
    )
    evaluator_llm = InstructorLLM(
        client=structured_client,
        model=model_name,
        provider="openai",
        max_tokens=4096,
    )
    faithfulness_metric = Faithfulness(llm=evaluator_llm)

    cache = load_cache()
    results: list[dict[str, Any]] = []

    for index, item in enumerate(
    selected_questions,
    start=args.start + 1,
    ):
        question_id = str(item.get("id", f"q{index:02d}"))
        question = item["question"]
        cache_key = f"{model_name}:{question_id}"
        cached = cache["samples"].get(cache_key)

        print(f"\n[{index}/{len(selected_questions)}] {question}")

        if cached and not args.refresh:
            cached_status = cached.get("evaluation_status")
            cached_contexts = cached.get("retrieved_contexts", [])
            cached_answer = cached.get("answer")

            if cached_status in {"complete", "abstained"}:
                print("Using cached answer and evaluation status.")
                results.append(cached)
                continue

            # Retry scoring a saved answer/context before spending tokens on
            # another generation call.
            if cached_answer and cached_contexts:
                answer = cached_answer
                contexts = cached_contexts
                response = {
                    "answer": answer,
                    "sources": cached.get("sources", []),
                    "retrieval_metadata": cached.get("retrieval_metadata", {}),
                    "citation_validation": cached.get("citation_validation", {}),
                }
                print("Reusing cached answer/context; retrying evaluation only.")
            else:
                response = None
        else:
            response = None

        if response is None:
            try:
                response = service.ask(question)
            except RateLimitError as exc:
                print("Groq rate limit reached during answer generation.")
                print("Stopping this run without replacing previous cached results.")
                failure_record = {
                    "id": question_id,
                    "question": question,
                    "answer": None,
                    "faithfulness": None,
                    "evaluation_status": "generation_rate_limited",
                    "evaluation_error": str(exc),
                    "sources": [],
                    "retrieved_contexts": [],
                    "retrieval_metadata": {},
                    "citation_validation": {},
                }
                results.append(failure_record)
                save_json(OUTPUT_PATH, build_output(results, model_name))
                break
            answer = response.get("answer", "")
            contexts = [
                source.get("excerpt", "")
                for source in response.get("sources", [])
                if source.get("excerpt", "").strip()
            ]
        else:
            answer = response.get("answer", "")

        contexts = [context for context in contexts if isinstance(context, str) and context.strip()]
        if not contexts:
            record = make_record(
                question_id,
                question,
                answer,
                None,
                "no_usable_context",
                "No non-empty retrieved source excerpts were available.",
                response,
                [],
            )
        else:
            score, status, error = evaluate_faithfulness(
                faithfulness_metric,
                question,
                answer,
                contexts,
            )
            record = make_record(
                question_id,
                question,
                answer,
                score,
                status,
                error,
                response,
                contexts,
            )

        cache["samples"][cache_key] = record
        save_json(CACHE_PATH, cache)
        results.append(record)

        if record["evaluation_status"] == "complete":
            print(f"Faithfulness: {record['faithfulness']:.3f}")
        elif record["evaluation_status"] == "abstained":
            print("Faithfulness: not scored (answer abstained).")
        elif record["evaluation_status"] == "skipped_rate_limit":
            print("Faithfulness: not scored (Groq rate limit).")
        else:
            print(f"Faithfulness: not scored ({record['evaluation_status']}).")
            if record.get("evaluation_error"):
                print("Evaluation detail:", record["evaluation_error"][:500])

        print(f"Sources used: {len(contexts)}")
        print("Answer:", answer)

        # Keep output up to date after each question in case a later request fails.
        save_json(OUTPUT_PATH, build_output(results, model_name))

    output = build_output(results, model_name)
    save_json(OUTPUT_PATH, output)

    print("\nEvaluation run finished.")
    mean = output["mean_faithfulness"]
    if mean is None:
        print("Mean Faithfulness: not available (no scored answers).")
    else:
        print(f"Mean Faithfulness: {mean:.3f}")
    print(f"\n[{index}/{len(golden_set)}] {question}")
    print(f"Scored questions: {output['scored_questions']}/{len(results)}")
    print(f"Cache: {CACHE_PATH}")
    print(f"Results: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

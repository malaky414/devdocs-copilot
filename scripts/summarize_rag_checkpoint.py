from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

GOLDEN_PATH = ROOT / "evals" / "golden_set.json"
CACHE_PATH = ROOT / "evals" / "rag_quality_cache.json"
OUTPUT_PATH = ROOT / "evals" / "rag_quality_checkpoint.json"
DOC_PATH = ROOT / "docs" / "rag_quality_checkpoint.md"

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


golden = read_json(GOLDEN_PATH)
cache = read_json(CACHE_PATH)
samples = cache.get("samples", {})

results = []

for index, item in enumerate(golden, start=1):
    question_id = str(item.get("id", f"q{index:02d}"))
    question = item["question"]
    record = samples.get(f"{MODEL}:{question_id}")

    if record is None:
        results.append({
            "id": question_id,
            "question": question,
            "evaluation_status": "not_run",
            "faithfulness": None,
            "source_count": 0,
            "answer_saved": False,
            "evaluation_error": None,
        })
        continue

    results.append({
        "id": question_id,
        "question": question,
        "evaluation_status": record.get(
            "evaluation_status", "unknown"
        ),
        "faithfulness": record.get("faithfulness"),
        "source_count": len(record.get("sources", [])),
        "answer_saved": bool(record.get("answer")),
        "evaluation_error": record.get("evaluation_error"),
    })

scores = [
    r["faithfulness"]
    for r in results
    if isinstance(r["faithfulness"], (int, float))
    and not isinstance(r["faithfulness"], bool)
]

status_counts = dict(
    sorted(Counter(
        r["evaluation_status"] for r in results
    ).items())
)

report = {
    "metric": "faithfulness",
    "model": MODEL,
    "checkpoint_created_at": datetime.now().astimezone().isoformat(),
    "completion_state": "partial_paused",
    "total_golden_questions": len(golden),
    "cached_questions": sum(
        r["evaluation_status"] != "not_run" for r in results
    ),
    "scored_questions": len(scores),
    "mean_faithfulness": (
        sum(scores) / len(scores) if scores else None
    ),
    "status_counts": status_counts,
    "results": results,
}

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH.write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

lines = [
    "# DevDocs Copilot — RAG Evaluation Checkpoint",
    "",
    f"- Created: {report['checkpoint_created_at']}",
    "- State: **PARTIAL / PAUSED**",
    "- This is not a completed 30-question evaluation.",
    f"- Golden questions: {report['total_golden_questions']}",
    f"- Questions with cached records: {report['cached_questions']}",
    f"- Scored questions: {report['scored_questions']}",
    f"- Mean Faithfulness of scored questions: "
    f"{report['mean_faithfulness']:.4f}"
    if scores else "- Mean Faithfulness: unavailable",
    "",
    "## Evaluation status counts",
    "",
]

for status, count in status_counts.items():
    lines.append(f"- `{status}`: {count}")

lines.extend([
    "",
    "## Per-question checkpoint",
    "",
    "| ID | Question | Status | Faithfulness | Sources |",
    "|---|---|---|---:|---:|",
])

for r in results:
    score = (
        f"{r['faithfulness']:.3f}"
        if isinstance(r["faithfulness"], (int, float))
        and not isinstance(r["faithfulness"], bool)
        else "—"
    )
    question = r["question"].replace("|", "\\|").replace("\n", " ")
    lines.append(
        f"| {r['id']} | {question} | "
        f"{r['evaluation_status']} | {score} | "
        f"{r['source_count']} |"
    )

lines.extend([
    "",
    "## Notes",
    "",
    "- The checkpoint was created from local files; it makes no model/API calls.",
    "- Q8 previously abstained and should be reviewed.",
    "- Q14 had a low Faithfulness score and should be reviewed.",
    "- Q16 generation succeeded, but evaluation failed while parsing malformed JSON.",
    "- Questions without cached records remain unevaluated.",
    "- The full Golden Set evaluation must not be reported as complete.",
    "",
])

DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
DOC_PATH.write_text("\n".join(lines), encoding="utf-8")

print(f"Checkpoint JSON: {OUTPUT_PATH}")
print(f"Checkpoint Markdown: {DOC_PATH}")
print(f"Scored: {len(scores)}/{len(golden)}")
print(f"Mean Faithfulness: {report['mean_faithfulness']}")
print(f"Statuses: {status_counts}")
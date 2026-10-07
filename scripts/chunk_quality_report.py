import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from pathlib import Path
from statistics import mean, median
from src.loaders.markdown_loader import load_markdown_corpus
from src.chunking.heading_chunker import parse_markdown_blocks, build_chunks


RAW_ROOT = Path("data/raw")
REPORT_PATH = Path("docs/chunk_quality_report.md")

CHUNK_SIZE = 1000
OVERLAP_TOKENS = 200


def percentile(values: list[int], p: float) -> float:
    if not values:
        return 0.0

    values = sorted(values)

    if len(values) == 1:
        return float(values[0])

    rank = (len(values) - 1) * p
    lower = int(rank)
    upper = min(lower + 1, len(values) - 1)

    weight = rank - lower

    return values[lower] + (values[upper] - values[lower]) * weight


def truncate(text: str, max_chars: int = 400) -> str:
    text = text.strip().replace("\n", " ")

    if len(text) <= max_chars:
        return text

    return text[: max_chars - 3] + "..."


def build_report() -> str:
    documents = load_markdown_corpus(str(RAW_ROOT))

    all_chunks = []
    file_stats = []

    for document in documents:
        blocks = parse_markdown_blocks(document.content)
        chunks = build_chunks(
            blocks,
            chunk_size=CHUNK_SIZE,
            overlap_tokens=OVERLAP_TOKENS,
        )

        for chunk in chunks:
            chunk["metadata"]["source_path"] = document.metadata["source_path"]

        all_chunks.extend(chunks)

        file_stats.append(
            {
                "source_path": document.metadata["source_path"],
                "blocks": len(blocks),
                "chunks": len(chunks),
            }
        )

    token_sizes = [
        chunk["metadata"]["token_count"]
        for chunk in all_chunks
    ]

    total_chunks = len(all_chunks)

    if not token_sizes:
        raise RuntimeError("No chunks were generated from the corpus.")

    oversize_chunks = [
        chunk
        for chunk in all_chunks
        if chunk["metadata"]["token_count"] > CHUNK_SIZE
    ]

    largest_chunks = sorted(
        all_chunks,
        key=lambda chunk: chunk["metadata"]["token_count"],
        reverse=True,
    )

    sample_indexes = sorted(
        set(
            [
                0,
                total_chunks // 2,
                total_chunks - 1,
            ]
        )
    )

    samples = [all_chunks[index] for index in sample_indexes]

    lines = []

    lines.append("# Chunk Quality Report")
    lines.append("")
    lines.append("## Configuration")
    lines.append("")
    lines.append(f"- Target chunk size: `{CHUNK_SIZE}` tokens")
    lines.append(f"- Overlap target: `{OVERLAP_TOKENS}` tokens")
    lines.append(f"- Corpus root: `{RAW_ROOT}`")
    lines.append("")

    lines.append("## Corpus Summary")
    lines.append("")
    lines.append(f"- Markdown files: **{len(documents)}**")
    lines.append(f"- Total chunks: **{total_chunks}**")
    lines.append(f"- Total oversize chunks: **{len(oversize_chunks)}**")
    lines.append("")

    lines.append("## Chunk Size Distribution")
    lines.append("")
    lines.append("| Metric | Tokens |")
    lines.append("|---|---:|")
    lines.append(f"| Minimum | {min(token_sizes)} |")
    lines.append(f"| Average | {mean(token_sizes):.1f} |")
    lines.append(f"| Median | {median(token_sizes):.1f} |")
    lines.append(f"| P75 | {percentile(token_sizes, 0.75):.1f} |")
    lines.append(f"| P90 | {percentile(token_sizes, 0.90):.1f} |")
    lines.append(f"| P95 | {percentile(token_sizes, 0.95):.1f} |")
    lines.append(f"| Maximum | {max(token_sizes)} |")
    lines.append("")

    buckets = [
        ("< 250", lambda value: value < 250),
        ("250-499", lambda value: 250 <= value < 500),
        ("500-999", lambda value: 500 <= value < 1000),
        ("1000-1499", lambda value: 1000 <= value < 1500),
        ("1500+", lambda value: value >= 1500),
    ]

    lines.append("### Distribution Buckets")
    lines.append("")
    lines.append("| Range | Count | Percentage |")
    lines.append("|---|---:|---:|")

    for label, condition in buckets:
        count = sum(condition(value) for value in token_sizes)
        percentage = (count / total_chunks) * 100

        lines.append(
            f"| {label} | {count} | {percentage:.1f}% |"
        )

    lines.append("")

    lines.append("## Per-File Summary")
    lines.append("")
    lines.append("| File | Blocks | Chunks |")
    lines.append("|---|---:|---:|")

    for item in file_stats:
        lines.append(
            f"| `{item['source_path']}` | "
            f"{item['blocks']} | "
            f"{item['chunks']} |"
        )

    lines.append("")

    lines.append("## Largest Chunks")
    lines.append("")
    lines.append("| Size | File | Section |")
    lines.append("|---:|---|---|")

    for chunk in largest_chunks[:10]:
        metadata = chunk["metadata"]
        section_path = " > ".join(metadata["section_path"])

        lines.append(
            f"| {metadata['token_count']} | "
            f"`{metadata['source_path']}` | "
            f"{section_path or '(root)'} |"
        )

    lines.append("")

    lines.append("## Sample Inspection")
    lines.append("")

    for number, chunk in enumerate(samples, start=1):
        metadata = chunk["metadata"]
        section_path = " > ".join(metadata["section_path"])

        lines.append(f"### Sample {number}")
        lines.append("")
        lines.append(f"- File: `{metadata['source_path']}`")
        lines.append(f"- Section: `{section_path or '(root)'}`")
        lines.append(f"- Token count: `{metadata['token_count']}`")
        lines.append("")
        lines.append("```text")
        lines.append(truncate(chunk["content"]))
        lines.append("```")
        lines.append("")

    lines.append("## Notes")
    lines.append("")

    if oversize_chunks:
        lines.append(
            f"- **{len(oversize_chunks)}** chunks exceed the "
            f"`{CHUNK_SIZE}`-token target."
        )
        lines.append(
            "- Oversize chunks may be intentional when a fenced code block "
            "is larger than the target size because code blocks are kept atomic."
        )
    else:
        lines.append(
            "- No chunks exceed the configured target size."
        )

    lines.append(
        "- Section titles are preserved in metadata through `section_path`."
    )
    lines.append(
        "- Code blocks are treated as atomic units and are never split."
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    report = build_report()
    REPORT_PATH.write_text(report, encoding="utf-8")

    print(f"Report written to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class MarkdownDocument:
    content: str
    metadata: dict


def extract_headings(markdown: str) -> list[dict]:
    headings = []
    hierarchy = []
    in_code_block = False

    for line_number, line in enumerate(markdown.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)

        if not match:
            continue

        level = len(match.group(1))
        title = match.group(2).strip()
        title = re.sub(r"\s*\{\s*#[^}]+\}\s*$", "", title)
        hierarchy = hierarchy[: level - 1]
        hierarchy.append(title)

        headings.append(
            {
                "level": level,
                "title": title,
                "path": hierarchy.copy(),
                "line": line_number,
            }
        )

    return headings


def load_markdown_file(path: Path, root: Path) -> MarkdownDocument:
    content = path.read_text(encoding="utf-8")

    relative_path = path.relative_to(root).as_posix()

    metadata = {
        "source_path": relative_path,
        "file_name": path.name,
        "headings": extract_headings(content),
    }

    return MarkdownDocument(
        content=content,
        metadata=metadata,
    )


def load_markdown_corpus(root: str) -> list[MarkdownDocument]:
    root_path = Path(root)

    documents = []

    for path in sorted(root_path.rglob("*.md")):
        documents.append(load_markdown_file(path, root_path))

    return documents
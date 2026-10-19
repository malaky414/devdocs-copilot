from dataclasses import dataclass
from os import path
from importlib.resources import path
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
EMBEDDED_PYTHON_PATTERN = re.compile(
    r"\{\*\s*(?P<path>[^*\s]+\.py)"
    r"(?:\s+hl\[[^\]]*\])?\s*\*\}"
)

def expand_python_examples(
    markdown: str,
    markdown_path: Path,
    root: Path,
) -> str:
    """Replace embedded docs_src references with their Python code."""

    def replace_example(match: re.Match) -> str:
        relative_example_path = match.group("path")

        # First, try resolving the original relative path.
        candidates = [
            (markdown_path.parent / relative_example_path).resolve()
        ]

        # The Markdown tree may have been moved from its upstream layout.
        # Fall back to data/raw/docs_src using the path after "docs_src/".
        parts = relative_example_path.replace("\\", "/").split("/")

        if "docs_src" in parts:
            docs_src_index = parts.index("docs_src")
            example_parts = parts[docs_src_index + 1 :]

            if example_parts:
                candidates.append(
                    (root / "docs_src" / Path(*example_parts)).resolve()
                )

        example_path = next(
            (candidate for candidate in candidates if candidate.is_file()),
            None,
        )

        # Keep the original reference if the example is unavailable.
        if example_path is None:
            return match.group(0)

        code = example_path.read_text(encoding="utf-8").rstrip()
        return f"\n```python\n{code}\n```\n"

    return EMBEDDED_PYTHON_PATTERN.sub(replace_example, markdown)

def load_markdown_file(path: Path, root: Path) -> MarkdownDocument:
    content = path.read_text(encoding="utf-8")
    content = expand_python_examples(content, path, root)

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
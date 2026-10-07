from dataclasses import dataclass
import tiktoken
ENCODING = tiktoken.get_encoding("cl100k_base")
@dataclass
class MarkdownBlock:
    block_type: str
    content: str
    section_path: list[str]

def count_tokens(text: str) -> int:
    return len(ENCODING.encode(text))
def build_chunks(
    blocks: list[MarkdownBlock],
    chunk_size: int = 1000,
    overlap_tokens: int = 200,
) -> list[dict]:
    chunks = []

    current_blocks: list[MarkdownBlock] = []
    current_tokens = 0

    for block in blocks:
        # A heading starts a new section.
        # We treat it as a hard chunk boundary.
        if block.block_type == "heading":
            if current_blocks:
                chunks.append(_create_chunk(current_blocks))
                current_blocks = []
                current_tokens = 0

            continue

        block_tokens = count_tokens(block.content)

        # A code block is atomic: never split it.
        if block.block_type == "code" and block_tokens > chunk_size:
            if current_blocks:
                chunks.append(_create_chunk(current_blocks))
                current_blocks = []
                current_tokens = 0

            chunks.append(_create_chunk([block]))
            continue

        # If adding this block would exceed the target,
        # finalize the current chunk first.
        if current_blocks and current_tokens + block_tokens > chunk_size:
            chunks.append(_create_chunk(current_blocks))

            # Keep recent blocks for overlap,
            # but only from the same section.
            overlap_blocks = []
            overlap_count = 0
            current_section = current_blocks[0].section_path

            for previous in reversed(current_blocks):
                if previous.section_path != current_section:
                    break

                previous_tokens = count_tokens(previous.content)

                if overlap_count + previous_tokens > overlap_tokens:
                    break

                overlap_blocks.insert(0, previous)
                overlap_count += previous_tokens

            current_blocks = overlap_blocks
            current_tokens = overlap_count

        current_blocks.append(block)
        current_tokens += block_tokens

    if current_blocks:
        chunks.append(_create_chunk(current_blocks))

    return chunks

def _create_chunk(blocks: list[MarkdownBlock]) -> dict:
    content = "\n\n".join(block.content for block in blocks)

    return {
        "content": content,
        "metadata": {
            "section_path": blocks[0].section_path,
            "start_section": blocks[0].section_path[-1]
            if blocks[0].section_path
            else None,
            "token_count": count_tokens(content),
        },
    }
def parse_markdown_blocks(
    markdown: str,
    initial_section_path: list[str] | None = None,
) -> list[MarkdownBlock]:
    blocks: list[MarkdownBlock] = []

    section_path = list(initial_section_path or [])

    paragraph_lines: list[str] = []
    code_lines: list[str] = []

    in_code_block = False
    code_fence = None

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return

        content = "\n".join(paragraph_lines).strip()

        if content:
            blocks.append(
                MarkdownBlock(
                    block_type="paragraph",
                    content=content,
                    section_path=section_path.copy(),
                )
            )

        paragraph_lines.clear()

    def flush_code() -> None:
        nonlocal code_lines

        if not code_lines:
            return

        content = "\n".join(code_lines).strip()

        blocks.append(
            MarkdownBlock(
                block_type="code",
                content=content,
                section_path=section_path.copy(),
            )
        )

        code_lines = []

    for line in markdown.splitlines():
        stripped = line.strip()

        # Handle fenced code blocks
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fence = stripped[:3]

            if not in_code_block:
                flush_paragraph()
                in_code_block = True
                code_fence = fence
                code_lines.append(line)
            elif fence == code_fence:
                code_lines.append(line)
                flush_code()
                in_code_block = False
                code_fence = None
            else:
                code_lines.append(line)

            continue

        # Everything inside a code block stays together
        if in_code_block:
            code_lines.append(line)
            continue

        # Markdown heading
        if stripped.startswith("#"):
            flush_paragraph()

            heading_level = len(stripped) - len(stripped.lstrip("#"))

            if heading_level <= 0 or heading_level > 6:
                paragraph_lines.append(line)
                continue

            title = stripped[heading_level:].strip()

            section_path = section_path[: heading_level - 1]
            section_path.append(title)

            blocks.append(
                MarkdownBlock(
                    block_type="heading",
                    content=title,
                    section_path=section_path.copy(),
                )
            )

            continue

        # Blank line = paragraph boundary
        if not stripped:
            flush_paragraph()
            continue

        paragraph_lines.append(line)

    # Flush anything left at EOF
    if in_code_block:
        flush_code()
    else:
        flush_paragraph()

    return blocks
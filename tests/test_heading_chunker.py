from src.chunking.heading_chunker import (
    build_chunks,
    parse_markdown_blocks,
)


def test_code_block_stays_atomic():
    sample = "\n".join(
        [
            "# FastAPI",
            "",
            "FastAPI is a framework.",
            "",
            "## Path Parameters",
            "",
            "Path parameters allow you to declare values.",
            "",
            "```python",
            '@app.get("/items/{item_id}")',
            "async def read_item(item_id: int):",
            '    return {"item_id": item_id}',
            "",
            "# This is inside code",
            "```",
            "",
            "More explanation here.",
            "",
            "## Query Parameters",
            "",
            "Query parameters are values after the question mark.",
        ]
    )

    blocks = parse_markdown_blocks(sample)

    assert any(
        block.block_type == "code"
        and "# This is inside code" in block.content
        for block in blocks
    )


def test_chunks_have_section_metadata():
    sample = "\n".join(
        [
            "# FastAPI",
            "",
            "FastAPI is a framework.",
            "",
            "## Path Parameters",
            "",
            "Path parameters allow you to declare values.",
        ]
    )

    blocks = parse_markdown_blocks(sample)

    chunks = build_chunks(
        blocks,
        chunk_size=50,
        overlap_tokens=10,
    )

    assert chunks

    path_chunk = next(
        chunk
        for chunk in chunks
        if chunk["metadata"]["section_path"]
        == ["FastAPI", "Path Parameters"]
    )

    assert "Path parameters allow you to declare values." in path_chunk["content"]
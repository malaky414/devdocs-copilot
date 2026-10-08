from src.retrieval.bm25_retriever import BM25Retriever


def test_bm25_returns_results() -> None:
    retriever = BM25Retriever()

    results = retriever.search(
        query="HTTPException",
        limit=5,
    )

    assert results
    assert any(
        "httpexception" in result["content"].lower()
        for result in results
    )


def test_bm25_source_filter() -> None:
    retriever = BM25Retriever()

    results = retriever.search(
        query="path parameter",
        limit=5,
        source_path="fastapi/tutorial/path-params.md",
    )

    assert results
    assert all(
        result["source_path"]
        == "fastapi/tutorial/path-params.md"
        for result in results
    )
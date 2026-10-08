from src.retrieval.dense_retriever import DenseRetriever


def test_dense_retriever_source_filter() -> None:
    retriever = DenseRetriever()

    results = retriever.search(
        query="How do I define a path parameter?",
        limit=5,
        source_path="fastapi/tutorial/path-params.md",
    )

    assert results
    assert all(
        result["source_path"] == "fastapi/tutorial/path-params.md"
        for result in results
    )
from src.retrieval.hybrid_retriever import HybridRetriever


def test_hybrid_retriever_returns_results() -> None:
    retriever = HybridRetriever()

    results = retriever.search(
        query="How do I define a path parameter?",
        limit=5,
        candidate_limit=20,
    )

    assert results
    assert len(results) <= 5

    for result in results:
        assert "rrf_score" in result
        assert "dense_rank" in result
        assert "bm25_rank" in result


def test_hybrid_exact_term() -> None:
    retriever = HybridRetriever()

    results = retriever.search(
        query="HTTPException",
        limit=5,
        candidate_limit=20,
    )

    assert results

    assert any(
        "httpexception" in result["content"].lower()
        for result in results
    )
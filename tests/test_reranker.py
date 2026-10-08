from src.retrieval.reranker import CrossEncoderReranker


class FakeCrossEncoder:
    def predict(
        self,
        pairs: list[tuple[str, str]],
        show_progress_bar: bool = False,
    ) -> list[float]:
        return [
            0.2,
            0.9,
            0.5,
        ]


def make_candidate(text: str) -> dict:
    return {
        "content": text,
        "source_path": "test.md",
        "section_path": ["Test"],
        "chunk_index": 0,
        "token_count": 10,
    }


def test_reranker_sorts_by_score() -> None:
    reranker = CrossEncoderReranker(
        model=FakeCrossEncoder(),
    )

    candidates = [
        make_candidate("Document A"),
        make_candidate("Document B"),
        make_candidate("Document C"),
    ]

    results = reranker.rerank(
        query="test query",
        candidates=candidates,
        limit=3,
    )

    assert results[0]["content"] == "Document B"
    assert results[1]["content"] == "Document C"
    assert results[2]["content"] == "Document A"

    assert results[0]["reranker_score"] == 0.9


def test_reranker_respects_limit() -> None:
    reranker = CrossEncoderReranker(
        model=FakeCrossEncoder(),
    )

    candidates = [
        make_candidate("Document A"),
        make_candidate("Document B"),
        make_candidate("Document C"),
    ]

    results = reranker.rerank(
        query="test query",
        candidates=candidates,
        limit=2,
    )

    assert len(results) == 2
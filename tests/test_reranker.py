
from src.retrieval.reranker import CrossEncoderReranker


class FakeCrossEncoder:
    def __init__(self, scores):
        self.scores = scores
        self.received_pairs = None

    def predict(self, pairs, show_progress_bar=False):
        self.received_pairs = pairs
        return self.scores


def test_reranker_receives_document_and_section_context():
    model = FakeCrossEncoder([0.9])
    reranker = CrossEncoderReranker(model=model)

    candidates = [
        {
            "source_path": "fastapi/tutorial/path-params.md",
            "section_path": ["Path Parameters"],
            "content": "Declare a path parameter using {item_id}.",
            "chunk_index": 0,
        }
    ]

    results = reranker.rerank(
        query="How do I define a path parameter?",
        candidates=candidates,
    )

    assert len(model.received_pairs) == 1

    query, document_text = model.received_pairs[0]

    assert query == "How do I define a path parameter?"
    assert "fastapi/tutorial/path-params.md" in document_text
    assert "Path Parameters" in document_text
    assert "Declare a path parameter" in document_text
    assert results[0]["reranker_score"] == 0.9


def test_reranker_sorts_by_score_and_preserves_metadata():
    model = FakeCrossEncoder([0.2, 0.9])
    reranker = CrossEncoderReranker(model=model)

    candidates = [
        {
            "source_path": "fastapi/tutorial/background-tasks.md",
            "section_path": ["Background Tasks"],
            "content": "Background task content.",
            "chunk_index": 4,
        },
        {
            "source_path": "fastapi/tutorial/path-params.md",
            "section_path": ["Path Parameters"],
            "content": "Path parameter content.",
            "chunk_index": 0,
        },
    ]

    results = reranker.rerank(
        query="How do I define a path parameter?",
        candidates=candidates,
        limit=2,
    )

    assert results[0]["source_path"] == (
        "fastapi/tutorial/path-params.md"
    )
    assert results[0]["chunk_index"] == 0
    assert results[0]["reranker_score"] == 0.9
    assert results[1]["reranker_score"] == 0.2


def test_reranker_handles_empty_candidates():
    model = FakeCrossEncoder([])
    reranker = CrossEncoderReranker(model=model)

    assert reranker.rerank(
        query="Any question",
        candidates=[],
    ) == []

    assert model.received_pairs is None

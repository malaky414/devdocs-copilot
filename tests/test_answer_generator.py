
from src.generation.answer_generator import (
    REFUSAL_ANSWER,
    generate_answer,
)


class FakeResponse:
    def __init__(self, content: str):
        self.content = content


class FakeLLM:
    def __init__(self, answer: str):
        self.answer = answer
        self.messages = None

    def invoke(self, messages):
        self.messages = messages
        return FakeResponse(self.answer)


SAMPLE_CHUNK = {
    "text": (
        "FastAPI uses path parameters to capture values from the URL."
    ),
    "source_path": "fastapi/tutorial/path-params.md",
    "file_name": "path-params.md",
    "headings": ["Path Parameters"],
    "dense_rank": 2,
    "bm25_rank": 1,
    "rerank_score": 0.91,
}


def test_valid_citation_returns_answer_and_source():
    llm = FakeLLM(
        "FastAPI captures URL values using path parameters [1]."
    )

    result = generate_answer(
        "What are path parameters?",
        [SAMPLE_CHUNK],
        llm,
    )

    assert result["answer"].endswith("[1].")
    assert result["citation_validation"]["valid"] is True
    assert result["used_source_ids"] == [1]
    assert result["sources"][0]["file_name"] == "path-params.md"
    assert result["sources"][0]["headings"] == ["Path Parameters"]
    assert result["sources"][0]["retrieval_metadata"]["rerank_score"] == 0.91


def test_unknown_citation_is_rejected():
    llm = FakeLLM("The answer is documented here [7].")

    result = generate_answer(
        "What are path parameters?",
        [SAMPLE_CHUNK],
        llm,
    )

    assert result["answer"] == REFUSAL_ANSWER
    assert result["citation_validation"]["valid"] is False
    assert result["citation_validation"]["unknown_source_ids"] == [7]


def test_answer_without_citation_is_rejected():
    llm = FakeLLM("FastAPI uses path parameters to capture URL values.")

    result = generate_answer(
        "What are path parameters?",
        [SAMPLE_CHUNK],
        llm,
    )

    assert result["answer"] == REFUSAL_ANSWER
    assert result["citation_validation"]["error"] == "missing_citations"


def test_empty_context_does_not_call_llm():
    llm = FakeLLM("This should not be used.")

    result = generate_answer(
        "What are path parameters?",
        [],
        llm,
    )

    assert result["answer"] == REFUSAL_ANSWER
    assert result["sources"] == []
    assert llm.messages is None
def test_retries_once_when_model_initially_refuses():
    from types import SimpleNamespace
    from src.generation.answer_generator import (
        REFUSAL_ANSWER,
        generate_answer,
    )

    class SequenceLLM:
        def __init__(self):
            self.calls = 0

        def invoke(self, messages):
            self.calls += 1

            if self.calls == 1:
                return SimpleNamespace(content=REFUSAL_ANSWER)

            return SimpleNamespace(
                content=(
                    "Declare the path parameter using "
                    "`{item_id}` and receive it as a function "
                    "argument [1]."
                )
            )

    llm = SequenceLLM()

    chunks = [
        {
            "content": (
                'You can declare path variables using Python '
                'format strings. Example: @app.get("/items/{item_id}") '
                'with function argument item_id.'
            ),
            "metadata": {
                "source_path": "fastapi/tutorial/path-params.md",
                "file_name": "path-params.md",
                "section_path": ["Path Parameters"],
            },
        }
    ]

    result = generate_answer(
        question="How do I define a path parameter in FastAPI?",
        reranked_chunks=chunks,
        llm=llm,
    )

    assert llm.calls == 2
    assert result["citation_validation"]["valid"] is True
    assert result["used_source_ids"] == [1]
    assert result["answer"] != REFUSAL_ANSWER
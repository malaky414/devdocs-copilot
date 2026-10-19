
from src.retrieval.query_expander import QueryExpander


class FakeResponse:
    def __init__(self, content: str):
        self.content = content


class FakeLLM:
    def __init__(self, response: str):
        self.response = response

    def invoke(self, messages):
        return FakeResponse(self.response)


def test_expander_keeps_original_and_adds_variants():
    llm = FakeLLM(
        '["FastAPI declare path parameters using item_id", '
        '"FastAPI path variable Python format string"]'
    )

    expander = QueryExpander(llm)

    queries = expander.expand(
        "How do I define a path parameter in FastAPI?"
    )

    assert len(queries) == 3
    assert queries[0] == "How do I define a path parameter in FastAPI?"
    assert "item_id" in queries[1]


def test_expander_removes_duplicate_queries():
    llm = FakeLLM(
        '["Find path parameters", "Find path parameters"]'
    )

    queries = QueryExpander(llm).expand("Find path parameters")

    assert queries == [
        "Find path parameters",
        "Find path parameters",
    ][:1]


def test_invalid_model_output_falls_back_to_original():
    llm = FakeLLM("This is not JSON")

    queries = QueryExpander(llm).expand("What is a path parameter?")

    assert queries == ["What is a path parameter?"]


def test_empty_question_raises_error():
    expander = QueryExpander(FakeLLM("[]"))

    try:
        expander.expand("   ")
    except ValueError as exc:
        assert "question" in str(exc)
    else:
        raise AssertionError("Expected ValueError")

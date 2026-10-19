
from src.retrieval.multi_query_retriever import MultiQueryRetriever


def make_result(path, index, content, score=0.5):
    return {
        "source_path": path,
        "chunk_index": index,
        "content": content,
        "score": score,
        "rrf_score": score,
    }


class FakeRetriever:
    def __init__(self, results_by_query):
        self.results_by_query = results_by_query

    def search(
        self,
        query,
        limit=5,
        candidate_limit=20,
        source_path=None,
    ):
        results = self.results_by_query.get(query, [])

        if source_path is not None:
            results = [
                item for item in results
                if item["source_path"] == source_path
            ]

        return results[:limit]


def test_chunks_returned_by_multiple_queries_rank_higher():
    chunk_a = make_result("a.md", 0, "Chunk A")
    chunk_b = make_result("b.md", 1, "Chunk B")
    chunk_c = make_result("c.md", 0, "Chunk C")

    retriever = FakeRetriever({
        "query one": [chunk_a, chunk_b],
        "query two": [chunk_b, chunk_c],
    })

    search = MultiQueryRetriever(retriever)

    results = search.search(
        ["query one", "query two"],
        limit=3,
        per_query_limit=10,
    )

    assert [
        (item["source_path"], item["chunk_index"])
        for item in results
    ] == [("b.md", 1), ("a.md", 0), ("c.md", 0)]

    assert results[0]["matched_query_count"] == 2
    assert len(results[0]["query_ranks"]) == 2


def test_duplicate_queries_are_not_counted_twice():
    chunk = make_result("a.md", 0, "Chunk A")

    retriever = FakeRetriever({
        "query": [chunk],
    })

    search = MultiQueryRetriever(retriever)

    results = search.search(["query", " query "])

    assert len(results) == 1
    assert results[0]["matched_query_count"] == 1


def test_result_limit_is_respected():
    retriever = FakeRetriever({
        "query": [
            make_result("a.md", 0, "A"),
            make_result("b.md", 0, "B"),
            make_result("c.md", 0, "C"),
        ],
    })

    results = MultiQueryRetriever(retriever).search(
        ["query"],
        limit=2,
        per_query_limit=10,
    )

    assert len(results) == 2


def test_empty_queries_return_no_results():
    retriever = FakeRetriever({})

    results = MultiQueryRetriever(retriever).search([])

    assert results == []

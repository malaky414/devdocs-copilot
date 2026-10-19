from fastapi.testclient import TestClient

from src.api import main as api


client = TestClient(api.app)


def test_health_is_available_without_initializing_llm():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ask_calls_answer_service(monkeypatch):
    class FakeService:
        def ask(self, question, source_path=None):
            return {
                "answer": f"Answer for: {question}",
                "sources": [],
                "used_source_ids": [],
                "citation_validation": {"valid": True},
                "retrieval_metadata": {"strategy": "test"},
            }

    monkeypatch.setattr(api, "_get_answer_service", lambda: FakeService())
    response = client.post("/ask", json={"question": "  What is FastAPI?  "})
    assert response.status_code == 200
    assert response.json()["answer"] == "Answer for: What is FastAPI?"


def test_ask_rejects_blank_question():
    response = client.post("/ask", json={"question": "   "})
    assert response.status_code == 422


def test_ingest_returns_ingestion_summary(monkeypatch):
    summary = {
        "status": "completed",
        "collection_name": "fastapi_docs",
        "document_count": 12,
        "chunk_count": 45,
        "embedding_model": "test-model",
        "vector_size": 384,
        "corpus_path": "data/raw",
    }
    monkeypatch.setattr(api, "ingest_corpus", lambda: summary)
    response = client.post("/ingest")
    assert response.status_code == 200
    assert response.json() == summary

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


logger = logging.getLogger("devdocs_copilot")
app = FastAPI(
    title="DevDocs Copilot API",
    description="Grounded question answering over FastAPI documentation.",
    version="1.0.0",
)

_answer_service: Any | None = None


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    source_path: str | None = None


def _get_answer_service() -> Any:
    """Initialize retrieval and LLM dependencies only when /ask is called."""
    global _answer_service

    if _answer_service is None:
        from src.generation.answer_service import DevDocsAnswerService

        _answer_service = DevDocsAnswerService()

    return _answer_service


def ingest_corpus() -> dict:
    """Load ingestion dependencies only when /ingest is called."""
    from src.ingestion.ingest_service import ingest_corpus as run_ingestion

    return run_ingestion()


@app.get("/health", tags=["system"])
def health() -> dict:
    """Lightweight liveness check."""
    return {"status": "ok", "service": "devdocs-copilot"}


@app.post("/ingest", tags=["indexing"])
def ingest() -> dict:
    """Build the Qdrant index from the local Markdown corpus."""
    try:
        return ingest_corpus()
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Corpus ingestion failed")
        raise HTTPException(
            status_code=503,
            detail="Corpus ingestion failed. Check API logs and Qdrant availability.",
        ) from exc


@app.post("/ask", tags=["question answering"])
def ask(request: AskRequest) -> dict:
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=422, detail="question must not be blank")

    try:
        return _get_answer_service().ask(
            question=question,
            source_path=request.source_path,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Question answering failed")
        raise HTTPException(
            status_code=503,
            detail="Question answering failed. Check API logs, Qdrant, and model configuration.",
        ) from exc


from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src.generation.answer_generator import generate_answer
from src.retrieval.dense_retriever import DenseRetriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.multi_query_retriever import MultiQueryRetriever
from src.retrieval.query_expander import QueryExpander
from src.retrieval.reranker import CrossEncoderReranker


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


class DevDocsAnswerService:
    """Coordinate query expansion, retrieval, reranking, and generation."""

    def __init__(
        self,
        retriever: Any | None = None,
        reranker: Any | None = None,
        llm: Any | None = None,
        candidate_limit: int = 20,
        source_limit: int = 5,
        per_query_limit: int = 50,
    ) -> None:
        self.enable_query_expansion = (
            os.getenv("ENABLE_QUERY_EXPANSION", "false").lower()
            in {"1", "true", "yes"}
        )
        if min(candidate_limit, source_limit, per_query_limit) < 1:
            raise ValueError("Retrieval limits must be positive")

        self.candidate_limit = candidate_limit
        self.source_limit = source_limit
        self.per_query_limit = per_query_limit

        self.retriever = retriever or HybridRetriever(
            dense_retriever=DenseRetriever(
                qdrant_url=os.getenv(
                    "QDRANT_URL",
                    "http://localhost:6333",
                )
            )
        )

        self.reranker = reranker or CrossEncoderReranker()

        if llm is None:
            api_key = os.getenv("GROQ_API_KEY")

            if not api_key:
                raise RuntimeError("GROQ_API_KEY is missing from .env")

            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
                temperature=0,
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1",
            )

        self.llm = llm

        # Generate alternative queries before retrieval.
        self.query_expander = QueryExpander(
            llm=self.llm,
            max_variants=3,
        )

        # Merge results from the original and alternative queries.
        self.multi_query_retriever = MultiQueryRetriever(
            retriever=self.retriever,
        )

    def ask(
        self,
        question: str,
        source_path: str | None = None,
    ) -> dict:
        if not question or not question.strip():
            raise ValueError("question must not be empty")

        queries = [question]
        if self.enable_query_expansion:
            queries = self.query_expander.expand(question)
            candidates = self.multi_query_retriever.search(
                queries=queries,
                limit=self.candidate_limit,
                per_query_limit=self.per_query_limit,
                source_path=source_path,
            )
            retrieval_strategy = "multi_query_hybrid_rrf"
        else:
            candidates = self.retriever.search(
                query=question,
                limit=self.candidate_limit,
                candidate_limit=self.per_query_limit,
                source_path=source_path,
            )
            retrieval_strategy = "hybrid_rrf"
        reranked_chunks = self.reranker.rerank(
            query=question,
            candidates=candidates,
            limit=self.source_limit,
        )

        response = generate_answer(
            question=question,
            reranked_chunks=reranked_chunks,
            llm=self.llm,
            max_sources=self.source_limit,
        )

        response["retrieval_metadata"] = {
            "strategy": retrieval_strategy,
            "queries_used": queries,
            "query_count": len(queries),
            "per_query_candidate_limit": self.per_query_limit,
            "candidate_count": len(candidates),
            "reranked_count": len(reranked_chunks),
            "candidate_limit": self.candidate_limit,
            "source_limit": self.source_limit,
        }

        return response

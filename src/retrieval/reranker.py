from typing import Any

import torch
from sentence_transformers import CrossEncoder


DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"


class CrossEncoderReranker:

    @staticmethod
    def _candidate_text(candidate: dict) -> str:
        section_path = (
            candidate.get("section_path")
            or candidate.get("headings")
            or []
        )

        if isinstance(section_path, str):
            section_path = [section_path]

        sections = " > ".join(str(section) for section in section_path)
        source = candidate.get("source_path", "unknown")

        return (
            f"Document: {source}\n"
            f"Section: {sections}\n"
            f"Content:\n{candidate.get('content', '')}"
        )

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        model: Any | None = None,
    ) -> None:
        self.model = model or CrossEncoder(
            model_name,
            activation_fn=torch.nn.Sigmoid(),
        )

    def rerank(
        self,
        query: str,
        candidates: list[dict],
        limit: int = 5,
    ) -> list[dict]:
        if not candidates:
            return []

        pairs = [
            (query, self._candidate_text(candidate))
            for candidate in candidates
        ]

        scores = self.model.predict(
            pairs,
            show_progress_bar=False,
        )

        reranked = []

        for candidate, score in zip(candidates, scores):
            item = dict(candidate)
            item["reranker_score"] = float(score)
            reranked.append(item)

        reranked.sort(
            key=lambda item: item["reranker_score"],
            reverse=True,
        )

        return reranked[:limit]

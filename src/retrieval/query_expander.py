
from __future__ import annotations

import json
import re
from typing import Any


class QueryExpander:
    """Generate alternative search queries without answering the question."""

    def __init__(self, llm: Any, max_variants: int = 3) -> None:
        if max_variants < 1:
            raise ValueError("max_variants must be at least 1")

        self.llm = llm
        self.max_variants = max_variants

    @staticmethod
    def _content(response: Any) -> str:
        content = getattr(response, "content", response)

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            return "\n".join(
                part["text"]
                for part in content
                if isinstance(part, dict)
                and isinstance(part.get("text"), str)
            )

        return ""

    def _parse_variants(self, raw: str) -> list[str]:
        """Parse a JSON array, tolerating a surrounding Markdown code fence."""
        text = raw.strip()

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\[[\s\S]*\]", text)

            if not match:
                return []

            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError:
                return []

        if not isinstance(parsed, list):
            return []

        return [
            item.strip()
            for item in parsed
            if isinstance(item, str) and item.strip()
        ]
    @staticmethod
    def _deterministic_seed(question: str) -> str | None:
        normalized = " ".join(question.casefold().split())

        is_path_parameter_question = any(
            phrase in normalized
            for phrase in (
                "path parameter",
                "path parameters",
                "path variable",
                "path variables",
            )
        )

        if not is_path_parameter_question:
            return None

        validation_terms = (
            "validat",
            "numeric",
            "greater than",
            "positive",
            "gt=0",
            "constraint",
        )

        is_validation_question = any(
            term in normalized for term in validation_terms
        )

        if is_validation_question:
            return (
                "FastAPI Path numeric validation "
                "gt greater than zero Annotated"
            )

        return (
            "FastAPI declare path parameters variables "
            "Python format strings item_id"
        )
    def expand(self, question: str) -> list[str]:
        if not question or not question.strip():
            raise ValueError("question must not be empty")

        prompt = f"""
Generate exactly {self.max_variants} alternative search queries
for retrieving relevant technical documentation.

Original question:
{question}

Generate these three query styles:

1. KEYWORD QUERY:
   - A compact group of 3–8 technical keywords.
   - Do not write a complete sentence or a question.
   - Include the main technology, feature, and relevant implementation terms.
   - Example style:
     "FastAPI path parameters Python format strings variable declaration"

2. SYNTAX QUERY:
   - Focus on how the feature is declared, configured, or used in code.
   - Include relevant programming concepts when appropriate.

3. TERMINOLOGY QUERY:
   - Use technical synonyms and terminology likely to appear
     in official documentation.
Query expansion examples:

Question: "How do I create a new column in a pandas DataFrame?"
Good keyword query:
"pandas DataFrame assign new column Series column assignment"

Question: "How do I filter rows in SQL?"
Good keyword query:
"SQL WHERE clause predicates comparison operators"
Question: "How do I define a path parameter in FastAPI?"

Good keyword query:
"FastAPI declare path parameters variables Python format strings item_id"

Why this is good:
- It includes terminology used in technical documentation.
- It includes related programming concepts.
- It uses a compact keyword-oriented search phrase,
  not just a paraphrase of the question.

For the actual question:
- Identify implementation concepts related to the question.
- Prefer technical terms likely to appear in documentation.
- Include useful terminology even when it is not explicitly stated
  in the user's wording.
- Make the keyword query meaningfully different from a paraphrase.
Translate natural-language requirements into technical terminology
used by APIs and documentation.

Examples:
- "greater than" -> gt
- "greater than or equal to" -> ge
- "less than" -> lt
- "less than or equal to" -> le
- "minimum string length" -> min_length
- "maximum string length" -> max_length

When a question describes a constraint in natural language,
include its likely technical parameter name in the keyword query.

Example:
Question:
"How can I validate a numeric path parameter so it is greater than zero?"

Good keyword query:
"FastAPI Path numeric validation gt greater than zero Annotated Pydantic"
Distinguish these two FastAPI question types:

A. Basic path parameter declaration:
- Focus on curly braces in the URL path, such as {{item_id}}.
- Include terminology such as path-operation function, function
  argument, URL path, and Python format strings.
- At least one keyword query should resemble:
  "FastAPI path parameters curly braces URL path function argument
   Python format strings item_id"
- Do not prioritize the Path() helper, numeric constraints,
  OpenAPI support, or path converters unless the question asks
  about those topics.

B. Path parameter validation:
- Focus on FastAPI's Path helper, Annotated, and constraints
  such as gt, ge, lt, and le.
- For a greater-than-zero constraint, prefer Path(gt=0).

Choose the query terminology based on the user's actual intent.
Do not mix validation terminology into basic declaration questions.
Prefer documented parameter names over generic alternatives
such as "min_value" when the documentation uses a specific name.

Rules:
- Do not make all queries simple paraphrases of the original.
- At least one query MUST be keyword-only, without question words
  such as "how", "what", or "why".
- Prefer terms useful for both lexical search and semantic search.
- Preserve the original question's intent.
- Do not invent unsupported API names or identifiers.
- Do not answer the question.
- Return only a valid JSON array of strings.
FastAPI-specific terminology:
- For URL path parameter validation, prefer FastAPI's Path helper.
- Include exact syntax such as Path(gt=0) or
  Annotated[int, Path(gt=0)] when relevant.
- Do not use Pydantic Field as the primary helper for
  FastAPI URL path parameter validation.
- Keep queries technically accurate and preserve the
  distinction between path parameters and model fields.
"""
        try:
            response = self.llm.invoke(
                [
                    (
                        "system",
                        "You rewrite search queries for a technical "
                        "documentation retrieval system. Return JSON only.",
                    ),
                    ("human", prompt),
                ]
            )

            variants = self._parse_variants(
                self._content(response)
            )
        except Exception:
            # Search can still proceed with the original query.
            variants = []

        queries = []
        seen = set()

        candidates = [question.strip(), *variants]

        for candidate in candidates:
            normalized = " ".join(candidate.split()).casefold()

            if normalized and normalized not in seen:
                queries.append(" ".join(candidate.split()))
                seen.add(normalized)

            if len(queries) >= self.max_variants + 1:
                break

        return queries

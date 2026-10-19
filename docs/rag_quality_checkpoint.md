# DevDocs Copilot — RAG Evaluation Checkpoint

- Created: 2026-10-19T14:37:41.921609+03:00
- State: **PARTIAL / PAUSED**
- This is not a completed 30-question evaluation.
- Golden questions: 30
- Questions with cached records: 16
- Scored questions: 14
- Mean Faithfulness of scored questions: 0.8666

## Evaluation status counts

- `abstained`: 1
- `complete`: 14
- `evaluation_failed`: 1
- `not_run`: 14

## Per-question checkpoint

| ID | Question | Status | Faithfulness | Sources |
|---|---|---|---:|---:|
| q01 | How do I define a path parameter in FastAPI? | complete | 0.800 | 5 |
| q02 | How can I validate a numeric path parameter such as requiring it to be greater than zero? | complete | 1.000 | 5 |
| q03 | How do I declare query parameters in FastAPI? | complete | 0.833 | 5 |
| q04 | How can I validate a query parameter string with minimum and maximum length? | complete | 0.900 | 5 |
| q05 | How do I configure metadata and other settings for a path operation? | complete | 0.769 | 5 |
| q06 | How do I define a Pydantic model for a request body in FastAPI? | complete | 1.000 | 5 |
| q07 | How can I send multiple body parameters to one FastAPI path operation? | complete | 0.900 | 5 |
| q08 | How do I define nested Pydantic models in a FastAPI request body? | abstained | — | 5 |
| q09 | How can I partially update a request model in FastAPI? | complete | 1.000 | 5 |
| q10 | How do I specify a response model in FastAPI? | complete | 0.857 | 5 |
| q11 | How can I return a specific HTTP status code from a FastAPI endpoint? | complete | 0.923 | 5 |
| q12 | How do I use cookies as parameters in FastAPI? | complete | 1.000 | 5 |
| q13 | How do I declare HTTP headers as parameters in FastAPI? | complete | 1.000 | 5 |
| q14 | How can I receive uploaded files in a FastAPI endpoint? | complete | 0.316 | 5 |
| q15 | How do I receive both form data and uploaded files in FastAPI? | complete | 0.833 | 5 |
| q16 | How do I configure CORS middleware in FastAPI? | evaluation_failed | — | 5 |
| q17 | How do I add middleware to a FastAPI application? | not_run | — | 0 |
| q18 | How can I run background tasks after returning a response in FastAPI? | not_run | — | 0 |
| q19 | How should I structure a larger FastAPI application with multiple routers? | not_run | — | 0 |
| q20 | How do dependencies work in FastAPI? | not_run | — | 0 |
| q21 | How can I use a class as a dependency in FastAPI? | not_run | — | 0 |
| q22 | How do sub-dependencies work in FastAPI? | not_run | — | 0 |
| q23 | How can I use yield inside a FastAPI dependency for setup and cleanup? | not_run | — | 0 |
| q24 | How do I implement a simple OAuth2 password flow in FastAPI? | not_run | — | 0 |
| q25 | How can I secure a FastAPI API using OAuth2 and JWT tokens? | not_run | — | 0 |
| q26 | How do I implement HTTP Basic authentication with FastAPI? | not_run | — | 0 |
| q27 | How do WebSockets work in FastAPI? | not_run | — | 0 |
| q28 | How can I deploy a FastAPI application using Docker? | not_run | — | 0 |
| q29 | How should I test FastAPI applications? | not_run | — | 0 |
| q30 | How can I customize FastAPI's generated OpenAPI documentation? | not_run | — | 0 |

## Notes

- The checkpoint was created from local files; it makes no model/API calls.
- Q8 previously abstained and should be reviewed.
- Q14 had a low Faithfulness score and should be reviewed.
- Q16 generation succeeded, but evaluation failed while parsing malformed JSON.
- Questions without cached records remain unevaluated.
- The full Golden Set evaluation must not be reported as complete.

# Chunk Quality Report

## Configuration

- Target chunk size: `1000` tokens
- Overlap target: `200` tokens
- Corpus root: `data\raw`

## Corpus Summary

- Markdown files: **156**
- Total chunks: **1901**
- Total oversize chunks: **37**

## Chunk Size Distribution

| Metric | Tokens |
|---|---:|
| Minimum | 2 |
| Average | 196.0 |
| Median | 114.0 |
| P75 | 214.0 |
| P90 | 395.0 |
| P95 | 624.0 |
| Maximum | 7344 |

### Distribution Buckets

| Range | Count | Percentage |
|---|---:|---:|
| < 250 | 1524 | 80.2% |
| 250-499 | 231 | 12.2% |
| 500-999 | 109 | 5.7% |
| 1000-1499 | 25 | 1.3% |
| 1500+ | 12 | 0.6% |

## Per-File Summary

| File | Blocks | Chunks |
|---|---:|---:|
| `fastapi/_llm-test.md` | 151 | 16 |
| `fastapi/about/index.md` | 2 | 1 |
| `fastapi/advanced/additional-responses.md` | 60 | 6 |
| `fastapi/advanced/additional-status-codes.md` | 21 | 3 |
| `fastapi/advanced/advanced-dependencies.md` | 81 | 11 |
| `fastapi/advanced/advanced-python-types.md` | 21 | 2 |
| `fastapi/advanced/async-tests.md` | 44 | 7 |
| `fastapi/advanced/behind-a-proxy.md` | 166 | 17 |
| `fastapi/advanced/custom-response.md` | 130 | 19 |
| `fastapi/advanced/dataclasses.md` | 47 | 5 |
| `fastapi/advanced/events.md` | 80 | 11 |
| `fastapi/advanced/generate-clients.md` | 91 | 15 |
| `fastapi/advanced/index.md` | 11 | 2 |
| `fastapi/advanced/json-base64-bytes.md` | 26 | 5 |
| `fastapi/advanced/middleware.md` | 41 | 7 |
| `fastapi/advanced/openapi-callbacks.md` | 79 | 10 |
| `fastapi/advanced/openapi-webhooks.md` | 28 | 5 |
| `fastapi/advanced/opentelemetry.md` | 65 | 11 |
| `fastapi/advanced/path-operation-advanced-configuration.md` | 70 | 9 |
| `fastapi/advanced/response-change-status-code.md` | 16 | 3 |
| `fastapi/advanced/response-cookies.md` | 26 | 3 |
| `fastapi/advanced/response-directly.md` | 42 | 6 |
| `fastapi/advanced/response-headers.md` | 21 | 3 |
| `fastapi/advanced/security/http-basic-auth.md` | 47 | 8 |
| `fastapi/advanced/security/index.md` | 10 | 2 |
| `fastapi/advanced/security/oauth2-scopes.md` | 130 | 15 |
| `fastapi/advanced/settings.md` | 129 | 18 |
| `fastapi/advanced/stream-data.md` | 59 | 10 |
| `fastapi/advanced/strict-content-type.md` | 39 | 5 |
| `fastapi/advanced/sub-applications.md` | 32 | 7 |
| `fastapi/advanced/templates.md` | 52 | 8 |
| `fastapi/advanced/testing-dependencies.md` | 26 | 3 |
| `fastapi/advanced/testing-events.md` | 6 | 1 |
| `fastapi/advanced/testing-websockets.md` | 7 | 1 |
| `fastapi/advanced/using-request-directly.md` | 27 | 4 |
| `fastapi/advanced/websockets.md` | 82 | 10 |
| `fastapi/advanced/wsgi.md` | 23 | 3 |
| `fastapi/alternatives.md` | 231 | 22 |
| `fastapi/async.md` | 201 | 21 |
| `fastapi/benchmarks.md` | 10 | 2 |
| `fastapi/contributing.md` | 4 | 2 |
| `fastapi/deployment/cloud.md` | 12 | 3 |
| `fastapi/deployment/concepts.md` | 137 | 28 |
| `fastapi/deployment/docker.md` | 237 | 37 |
| `fastapi/deployment/fastapicloud.md` | 19 | 4 |
| `fastapi/deployment/https.md` | 102 | 15 |
| `fastapi/deployment/index.md` | 12 | 3 |
| `fastapi/deployment/manually.md` | 55 | 6 |
| `fastapi/deployment/server-workers.md` | 38 | 7 |
| `fastapi/deployment/versions.md` | 43 | 7 |
| `fastapi/editor-support.md` | 10 | 4 |
| `fastapi/environment-variables.md` | 6 | 2 |
| `fastapi/external-links.md` | 14 | 3 |
| `fastapi/fastapi-cli.md` | 43 | 6 |
| `fastapi/fastapi-people.md` | 84 | 13 |
| `fastapi/features.md` | 67 | 13 |
| `fastapi/help-fastapi.md` | 35 | 10 |
| `fastapi/history-design-future.md` | 40 | 7 |
| `fastapi/how-to/authentication-error-status-code.md` | 9 | 1 |
| `fastapi/how-to/conditional-openapi.md` | 22 | 3 |
| `fastapi/how-to/configure-swagger-ui.md` | 33 | 6 |
| `fastapi/how-to/custom-docs-ui-assets.md` | 76 | 15 |
| `fastapi/how-to/custom-request-and-route.md` | 54 | 7 |
| `fastapi/how-to/extending-openapi.md` | 42 | 9 |
| `fastapi/how-to/general.md` | 22 | 11 |
| `fastapi/how-to/graphql.md` | 27 | 5 |
| `fastapi/how-to/index.md` | 7 | 1 |
| `fastapi/how-to/migrate-from-pydantic-v1-to-pydantic-v2.md` | 61 | 9 |
| `fastapi/how-to/separate-openapi-schemas.md` | 46 | 10 |
| `fastapi/how-to/testing-database.md` | 4 | 1 |
| `fastapi/index.md` | 174 | 32 |
| `fastapi/learn/index.md` | 3 | 1 |
| `fastapi/management.md` | 8 | 3 |
| `fastapi/newsletter.md` | 3 | 1 |
| `fastapi/project-generation.md` | 6 | 2 |
| `fastapi/python-types.md` | 157 | 18 |
| `fastapi/reference/apirouter.md` | 5 | 1 |
| `fastapi/reference/background.md` | 5 | 1 |
| `fastapi/reference/dependencies.md` | 13 | 2 |
| `fastapi/reference/encoders.md` | 2 | 1 |
| `fastapi/reference/exceptions.md` | 9 | 1 |
| `fastapi/reference/fastapi.md` | 5 | 1 |
| `fastapi/reference/httpconnection.md` | 5 | 1 |
| `fastapi/reference/index.md` | 3 | 1 |
| `fastapi/reference/middleware.md` | 15 | 1 |
| `fastapi/reference/openapi/docs.md` | 6 | 1 |
| `fastapi/reference/openapi/index.md` | 3 | 1 |
| `fastapi/reference/openapi/models.md` | 3 | 1 |
| `fastapi/reference/parameters.md` | 14 | 1 |
| `fastapi/reference/request.md` | 9 | 1 |
| `fastapi/reference/response.md` | 7 | 1 |
| `fastapi/reference/responses.md` | 21 | 3 |
| `fastapi/reference/security/index.md` | 29 | 8 |
| `fastapi/reference/sse.md` | 8 | 1 |
| `fastapi/reference/staticfiles.md` | 6 | 1 |
| `fastapi/reference/status.md` | 12 | 2 |
| `fastapi/reference/templating.md` | 6 | 1 |
| `fastapi/reference/testclient.md` | 6 | 1 |
| `fastapi/reference/uploadfile.md` | 5 | 1 |
| `fastapi/reference/websockets.md` | 20 | 2 |
| `fastapi/release-notes.md` | 1943 | 734 |
| `fastapi/resources/index.md` | 2 | 1 |
| `fastapi/translation-banner.md` | 6 | 1 |
| `fastapi/translations.md` | 13 | 3 |
| `fastapi/tutorial/background-tasks.md` | 40 | 8 |
| `fastapi/tutorial/bigger-applications.md` | 227 | 22 |
| `fastapi/tutorial/body-fields.md` | 30 | 5 |
| `fastapi/tutorial/body-multiple-params.md` | 56 | 7 |
| `fastapi/tutorial/body-nested-models.md` | 88 | 15 |
| `fastapi/tutorial/body-updates.md` | 43 | 6 |
| `fastapi/tutorial/body.md` | 70 | 11 |
| `fastapi/tutorial/cookie-param-models.md` | 32 | 5 |
| `fastapi/tutorial/cookie-params.md` | 23 | 4 |
| `fastapi/tutorial/cors.md` | 39 | 8 |
| `fastapi/tutorial/debugging.md` | 47 | 5 |
| `fastapi/tutorial/dependencies/classes-as-dependencies.md` | 125 | 7 |
| `fastapi/tutorial/dependencies/dependencies-in-path-operation-decorators.md` | 35 | 8 |
| `fastapi/tutorial/dependencies/dependencies-with-yield.md` | 115 | 13 |
| `fastapi/tutorial/dependencies/global-dependencies.md` | 8 | 2 |
| `fastapi/tutorial/dependencies/index.md` | 99 | 14 |
| `fastapi/tutorial/dependencies/sub-dependencies.md` | 44 | 6 |
| `fastapi/tutorial/encoder.md` | 18 | 2 |
| `fastapi/tutorial/extra-data-types.md` | 14 | 3 |
| `fastapi/tutorial/extra-models.md` | 82 | 12 |
| `fastapi/tutorial/first-steps.md` | 159 | 26 |
| `fastapi/tutorial/frontend.md` | 67 | 10 |
| `fastapi/tutorial/handling-errors.md` | 96 | 13 |
| `fastapi/tutorial/header-param-models.md` | 30 | 6 |
| `fastapi/tutorial/header-params.md` | 41 | 6 |
| `fastapi/tutorial/index.md` | 49 | 5 |
| `fastapi/tutorial/metadata.md` | 52 | 10 |
| `fastapi/tutorial/middleware.md` | 42 | 5 |
| `fastapi/tutorial/path-operation-configuration.md` | 54 | 9 |
| `fastapi/tutorial/path-params-numeric-validations.md` | 74 | 10 |
| `fastapi/tutorial/path-params.md` | 112 | 20 |
| `fastapi/tutorial/query-param-models.md` | 27 | 5 |
| `fastapi/tutorial/query-params-str-validations.md` | 199 | 25 |
| `fastapi/tutorial/query-params.md` | 70 | 6 |
| `fastapi/tutorial/request-files.md` | 79 | 11 |
| `fastapi/tutorial/request-form-models.md` | 31 | 5 |
| `fastapi/tutorial/request-forms-and-files.md` | 20 | 4 |
| `fastapi/tutorial/request-forms.md` | 36 | 5 |
| `fastapi/tutorial/response-model.md` | 154 | 22 |
| `fastapi/tutorial/response-status-code.md` | 44 | 4 |
| `fastapi/tutorial/schema-extra-example.md` | 90 | 15 |
| `fastapi/tutorial/security/first-steps.md` | 92 | 10 |
| `fastapi/tutorial/security/get-current-user.md` | 53 | 8 |
| `fastapi/tutorial/security/index.md` | 45 | 8 |
| `fastapi/tutorial/security/oauth2-jwt.md` | 128 | 14 |
| `fastapi/tutorial/security/simple-oauth2.md` | 130 | 17 |
| `fastapi/tutorial/server-sent-events.md` | 57 | 10 |
| `fastapi/tutorial/sql-databases.md` | 164 | 27 |
| `fastapi/tutorial/static-files.md` | 24 | 5 |
| `fastapi/tutorial/stream-json-lines.md` | 46 | 8 |
| `fastapi/tutorial/testing.md` | 75 | 9 |
| `fastapi/virtual-environments.md` | 15 | 3 |

## Largest Chunks

| Size | File | Section |
|---:|---|---|
| 7344 | `fastapi/release-notes.md` | Release Notes > 0.110.1 (2024-04-02) > Translations |
| 5275 | `fastapi/release-notes.md` | Release Notes > 0.109.1 (2024-02-03) > Translations |
| 4373 | `fastapi/release-notes.md` | Release Notes > 0.115.5 (2024-11-12) > Docs |
| 2878 | `fastapi/release-notes.md` | Release Notes > 0.115.7 (2025-01-22) > Translations |
| 2529 | `fastapi/release-notes.md` | Release Notes > 0.111.1 (2024-07-14) > Translations |
| 2343 | `fastapi/release-notes.md` | Release Notes > 0.116.2 (2025-09-16) > Internal |
| 2023 | `fastapi/release-notes.md` | Release Notes > 0.115.13 (2025-06-17) > Internal |
| 1969 | `fastapi/release-notes.md` | Release Notes > 0.142.0 (2026-09-29) > Internal |
| 1911 | `fastapi/release-notes.md` | Release Notes > 0.64.0 (2021-05-07) > Translations |
| 1697 | `fastapi/release-notes.md` | Release Notes > 0.128.1 (2026-02-04) > Internal |

## Sample Inspection

### Sample 1

- File: `fastapi/_llm-test.md`
- Section: `LLM test file { #llm-test-file }`
- Token count: `289`

```text
This document tests if the <abbr title="Large Language Model">LLM</abbr>, which translates the documentation, understands the `general_prompt` in `scripts/translate.py` and the language specific prompt in `docs/{language code}/llm-prompt.md`. The language specific prompt is appended to `general_prompt`.  Tests added here will be seen by all designers of language specific prompts.  Use as follow...
```

### Sample 2

- File: `fastapi/release-notes.md`
- Section: `Release Notes > 0.115.3 (2024-10-22) > Internal`
- Token count: `306`

```text
* 👷 Update issue manager workflow . PR [#12457](https://github.com/fastapi/fastapi/pull/12457) by [@alejsdev](https://github.com/alejsdev). * 🔧 Update team, include YuriiMotov 🚀. PR [#12453](https://github.com/fastapi/fastapi/pull/12453) by [@tiangolo](https://github.com/tiangolo). * 👷 Refactor label-approved, make it an internal script instead of an external GitHub Action. PR [#12280](https://...
```

### Sample 3

- File: `fastapi/virtual-environments.md`
- Section: `Virtual Environments { #virtual-environments } > Learn More { #learn-more }`
- Token count: `48`

```text
Read the [Virtual Environments guide](https://tiangolo.com/guides/virtual-environments/) to learn how virtual environments work underneath, including activation and the alternative `python -m venv` and `pip` workflow.
```

## Notes

- **37** chunks exceed the `1000`-token target.
- Oversize chunks may be intentional when a fenced code block is larger than the target size because code blocks are kept atomic.
- Section titles are preserved in metadata through `section_path`.
- Code blocks are treated as atomic units and are never split.

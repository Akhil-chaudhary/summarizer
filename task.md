# Functional Requirements
## Core Features
### 1. Document Management API

> **Implementation notes (where this is implemented in the codebase):**
>
> - `app/routers/documents_router.py`
>   - `create_document()` -> `POST /documents`
>   - `get_document()` -> `GET /documents/{document_id}`
>   - `list_documents()` -> `GET /documents`
>   - `delete_document()` -> `DELETE /documents/{document_id}`
>   - `get_documents_service()` is used with FastAPI `Depends(...)` to inject `DocumentsService`
> - `app/services/documents_service.py`
>   - `DocumentsService.create/get/list/delete()` orchestrate business logic
> - `app/repositories/documents_repository.py`
>   - `DocumentsRepository.create/get/list/delete()` stores documents in-memory
> - `app/schemas/document_schema.py`
>   - `DocumentCreateRequest`, `DocumentResponse`, `DocumentListResponse`

Implement REST endpoints to:

 - Create a document
 - Get document by ID
 - List documents
 - Delete document

Document model:
```json
{
  "id": "uuid",
  "title": "string",
  "content": "string",
  "summary": "string | null",
  "created_at": "datetime"
}
```

### 2. AI Summary Feature (Minimal AI)

> **Implementation notes (where this is implemented in the codebase):**
>
> - `app/routers/documents_router.py`
>   - `summarize_document()` -> `POST /documents/{document_id}/summarize`
> - `app/services/documents_service.py`
>   - `DocumentsService.summarize()` generates and persists summary
> - `app/services/summarizer_service.py`
>   - `SummarizerService.summarize()` minimal summarizer (first sentence + truncation)
> - `app/repositories/documents_repository.py`
>   - `DocumentsRepository.set_summary()` persists summary on the in-memory record

Implement an endpoint:

`POST /documents/{id}/summarize`

Requirements:

 - Generate a short summary of the content

You may:

 - Use a simple NLP library, OR
 - Use a stub/mock summarizer, OR
 - Call an external AI API

We are evaluating integration design, not AI sophistication.

### 3. Search Endpoint

> **Implementation notes (where this is implemented in the codebase):**
>
> - `app/routers/documents_router.py`
>   - `search_documents()` -> `GET /documents/search?q=...`
> - `app/services/documents_service.py`
>   - `DocumentsService.search()`
> - `app/repositories/documents_repository.py`
>   - `DocumentsRepository.search()` uses an in-memory inverted index
>   - `_tokenize()` tokenizes title/content and query for search matching

Implement:

`GET /documents/search?q=...`

Requirements:
 - Basic full-text search over title and content

Simple implementation is acceptable but must be reasonably efficient

## Technical Requirements
### Backend

> **Implementation notes (how requirements are satisfied):**
>
> - Python runtime is declared in `pyproject.toml` (`requires-python = ">=3.12"`).
> - FastAPI application entrypoint: `app/main.py` (`create_app()` and `app`).
> - Pydantic models: `app/schemas/document_schema.py`.
> - Tests: `tests/` (see `tests/test_documents_api.py`).
> - Formatter/linter tooling:
>   - `pyproject.toml` includes optional dev dependencies for `black` and `ruff`.
> - AWS awareness:
>   - Lambda adapter included via `mangum` (`app/aws_lambda_handler.py`).
>   - A reference AWS SAM template is provided (`template.yaml`) for API Gateway -> Lambda.

Requirements:

 - Python 3.12+
 - FastAPI
 - Pydantic models

AWS Awareness - you may use [localstack](https://docs.localstack.cloud/aws/) to mimic AWS resources

Your implementation **must** demonstrate a production mindset

### Production suggestion (replace in-memory storage)

If this service needs persistence beyond process memory, a typical production setup would be:

 - **Best default choice: PostgreSQL (AWS RDS / Aurora PostgreSQL)**
   - Strong consistency, easy querying (list/search), good operational maturity.
   - Use SQLAlchemy + Alembic migrations.
   - Search options:
     - Start with `ILIKE` + indexes for simple needs.
     - Upgrade to Postgres full-text search (`tsvector`) for efficient text search.
 - **AWS-native alternative: DynamoDB (AWS managed NoSQL)**
   - Great for scale and low ops; good fit for key-based access patterns.
   - For search, you typically pair it with OpenSearch or build a secondary index strategy.
 - **If search is a core feature: OpenSearch (or Postgres FTS) for indexing**
   - Use Postgres/DynamoDB as the source of truth and OpenSearch as the search index.

In this codebase, the change would be isolated to replacing `app/repositories/documents_repository.py` with a DB-backed repository implementation while keeping the router/service layers largely the same.

## Ideal Deliverables

> **Implementation notes (what is included in this repo):**
>
> 1. Source code: `app/`
> 2. README: `README.md` (local run instructions, architecture, design decisions, test running)
> 3. Tests: `tests/`
> 4. AWS deployment: `template.yaml` + `app/aws_lambda_handler.py` (SAM/Lambda reference)
> 5. (Optional) Docker setup: not included

Deliverables:

 1. Source code
 2. README including:
    1. How to run locally
    2. Architecture explanation
    3. Design decisions
 3. Tests
 4. AWS deployment
 5. (Optional) Docker setup
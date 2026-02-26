# Summarizer (FastAPI)

## Run locally

### 1) Install

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[test]"
```

### 2) Start API

```bash
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000/docs

## API examples

### Create a document

```bash
curl -X POST "http://127.0.0.1:8000/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Hunter x Hunter Overview",
    "content": "Hunter x Hunter is a popular Japanese anime and manga series created by Yoshihiro Togashi. The story follows a young boy named Gon Freecss, who discovers that his father, Ging Freecss, is a legendary Hunter. Hunters are skilled individuals licensed to track down treasures, rare creatures, and even criminals.\n\nDetermined to find his father, Gon takes the challenging Hunter Examination. During the exam, he meets important friends such as Killua Zoldyck, Kurapika, and Leorio. Together, they face dangerous trials that test their strength, intelligence, and loyalty.\n\nOne of the most important concepts in the series is Nen, a special energy system that allows characters to develop unique abilities. Nen battles are strategic and require deep understanding and training rather than just physical strength.\n\nHunter x Hunter is known for its strong character development and complex story arcs. Popular arcs include the Yorknew City arc, the Greed Island arc, and the Chimera Ant arc. Each arc explores different themes such as friendship, revenge, morality, and survival.\n\nOverall, Hunter x Hunter stands out because it combines adventure, emotional depth, and intense action. It remains one of the most respected anime series worldwide due to its storytelling and memorable characters."
  }'
```

## Run tests

```bash
.\.venv\Scripts\activate
python -m pytest -q
```

## Dev tooling (format / lint)

Install dev dependencies:

```bash
pip install -e ".[dev]"
```

Format:

```bash
python -m black .
```

Lint:

```bash
python -m ruff check .
```

## Tests included

- `tests/test_documents_api.py`
  - Covers create/get/list/delete document endpoints
  - Covers `POST /documents/{id}/summarize`
  - Covers `GET /documents/search?q=...`

## Architecture

- `app/main.py`: FastAPI app factory + router registration
- `app/routers/*_router.py`: HTTP layer
- `app/schemas/*_schema.py`: Pydantic request/response models
- `app/services/*_service.py`: business logic
- `app/repositories/*_repository.py`: data access (in-memory + inverted index)

## Design decisions

- In-memory storage keeps the exercise simple while demonstrating layering.
- Search uses a lightweight inverted index for basic efficiency.
- Summarization is intentionally minimal (first sentence + max length).

## AWS deployment (reference)

This repo includes `mangum` as a Lambda adapter. A typical production path:

- API Gateway (HTTP API) -> Lambda running FastAPI via Mangum
- DynamoDB for documents (instead of in-memory)

If you want to mimic AWS locally, use LocalStack and deploy via SAM/Terraform.

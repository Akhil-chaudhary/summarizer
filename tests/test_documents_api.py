from fastapi.testclient import TestClient


def _create_doc(client: TestClient, *, title: str, content: str) -> dict:
    """Author: Akhil Chaudhary

    Helper to create a document and assert on the basic response contract.
    """
    resp = client.post("/documents", json={"title": title, "content": content})
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"]
    assert body["title"] == title
    assert body["content"] == content
    assert "created_at" in body
    return body


def test_create_and_get_document(client: TestClient) -> None:
    """Author: Akhil Chaudhary

    Validate that a created document can be retrieved and has expected default fields.
    """
    created = _create_doc(client, title="Hello", content="This is a long text. Second sentence.")
    doc_id = created["id"]

    get_resp = client.get(f"/documents/{doc_id}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["id"] == doc_id
    assert fetched["summary"] is None


def test_list_documents_returns_created_docs(client: TestClient) -> None:
    """Author: Akhil Chaudhary

    Validate list endpoint returns all created documents.
    """
    _create_doc(client, title="Doc A", content="alpha")
    _create_doc(client, title="Doc B", content="beta")

    list_resp = client.get("/documents")
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    assert len(items) == 2


def test_delete_document_is_idempotent_for_missing_doc(client: TestClient) -> None:
    """Author: Akhil Chaudhary

    Validate delete removes a document and missing resources return 404.
    """
    created = _create_doc(client, title="To delete", content="content")
    doc_id = created["id"]

    delete_resp = client.delete(f"/documents/{doc_id}")
    assert delete_resp.status_code == 204

    missing_get = client.get(f"/documents/{doc_id}")
    assert missing_get.status_code == 404

    missing_delete = client.delete(f"/documents/{doc_id}")
    assert missing_delete.status_code == 404


def test_get_document_invalid_uuid_returns_404(client: TestClient) -> None:
    """Author: Akhil Chaudhary

    Validate that invalid UUID path parameter returns 404.
    """
    resp = client.get("/documents/not-a-uuid")
    assert resp.status_code == 404


def test_summarize_persists_summary(client: TestClient) -> None:
    """Author: Akhil Chaudhary

    Validate summarize endpoint returns a summary and persists it on the document.
    """
    created = _create_doc(client, title="Sum", content="First sentence. Second sentence.")
    doc_id = created["id"]

    summ_resp = client.post(f"/documents/{doc_id}/summarize")
    assert summ_resp.status_code == 200
    summ_body = summ_resp.json()
    assert summ_body["id"] == doc_id
    assert isinstance(summ_body["summary"], str)
    assert summ_body["summary"]

    after = client.get(f"/documents/{doc_id}").json()
    assert after["summary"] == summ_body["summary"]


def test_summarize_missing_document_returns_404(client: TestClient) -> None:
    """Author: Akhil Chaudhary

    Validate summarize endpoint returns 404 for a missing document.
    """
    resp = client.post("/documents/00000000-0000-0000-0000-000000000000/summarize")
    assert resp.status_code == 404


def test_search_finds_by_title_or_content_and_is_case_insensitive(client: TestClient) -> None:
    """Author: Akhil Chaudhary

    Validate search matches tokens in both title and content and is case-insensitive.
    """
    _create_doc(client, title="Hello World", content="some text")
    _create_doc(client, title="Another", content="HELLO there")
    _create_doc(client, title="Unrelated", content="zzz")

    resp = client.get("/documents/search", params={"q": "hello"})
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 2


def test_search_empty_query_returns_422(client: TestClient) -> None:
    """Author: Akhil Chaudhary

    Validate that the required query parameter is enforced by FastAPI.
    """
    resp = client.get("/documents/search")
    assert resp.status_code == 422


def test_search_only_punctuation_returns_empty(client: TestClient) -> None:
    """Author: Akhil Chaudhary

    Validate search returns empty results when query contains no tokenizable terms.
    """
    _create_doc(client, title="Hello", content="World")
    resp = client.get("/documents/search", params={"q": "!!!"})
    assert resp.status_code == 200
    assert resp.json()["items"] == []

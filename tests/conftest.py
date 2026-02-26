import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.repositories.documents_repository import DocumentsRepository
from app.routers.documents_router import get_documents_service
from app.services.documents_service import DocumentsService
from app.services.summarizer_service import SummarizerService


@pytest.fixture()
def client() -> TestClient:
    """Author: Akhil Chaudhary

    Provide an isolated TestClient instance per test by overriding service dependencies.
    """
    app = create_app()

    repo = DocumentsRepository()
    summarizer = SummarizerService()
    service = DocumentsService(repo=repo, summarizer=summarizer)

    app.dependency_overrides[get_documents_service] = lambda: service
    return TestClient(app)

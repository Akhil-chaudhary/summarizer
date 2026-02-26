from fastapi import APIRouter, Depends, HTTPException, status

from app.repositories.documents_repository import DocumentsRepository
from app.schemas.document_schema import (
    DocumentCreateRequest,
    DocumentListResponse,
    DocumentResponse,
    DocumentSummaryResponse,
)
from app.services.documents_service import DocumentsService
from app.services.summarizer_service import SummarizerService

router = APIRouter(prefix="/documents", tags=["documents"])

_repo = DocumentsRepository()
_summarizer = SummarizerService()


def get_documents_service() -> DocumentsService:
    """Author: Akhil Chaudhary

    Provide a DocumentsService instance wired to shared in-memory dependencies.
    """

    return DocumentsService(repo=_repo, summarizer=_summarizer)


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    payload: DocumentCreateRequest,
    service: DocumentsService = Depends(get_documents_service),
) -> DocumentResponse:
    """Author: Akhil Chaudhary

    Create a new document and return the persisted representation.
    """
    return service.create(payload)


@router.get("/search", response_model=DocumentListResponse)
def search_documents(
    q: str,
    service: DocumentsService = Depends(get_documents_service),
) -> DocumentListResponse:
    """Author: Akhil Chaudhary

    Search documents by a query string across title and content.
    """
    return DocumentListResponse(items=service.search(q))


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    service: DocumentsService = Depends(get_documents_service),
) -> DocumentResponse:
    """Author: Akhil Chaudhary

    Retrieve a single document by its UUID.
    """
    doc = service.get(document_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc


@router.get("", response_model=DocumentListResponse)
def list_documents(
    service: DocumentsService = Depends(get_documents_service),
) -> DocumentListResponse:
    """Author: Akhil Chaudhary

    List all documents.

    Future improvement: add pagination support via `limit` and `offset` query parameters.
    """
    return DocumentListResponse(items=service.list())


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    service: DocumentsService = Depends(get_documents_service),
) -> None:
    """Author: Akhil Chaudhary

    Delete a document by UUID.
    """
    deleted = service.delete(document_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return None


@router.post("/{document_id}/summarize", response_model=DocumentSummaryResponse)
def summarize_document(
    document_id: str,
    service: DocumentsService = Depends(get_documents_service),
) -> DocumentSummaryResponse:
    """Author: Akhil Chaudhary

    Generate a summary for a document and persist it onto the document.
    """
    summary = service.summarize(document_id)
    if summary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentSummaryResponse(id=document_id, summary=summary)

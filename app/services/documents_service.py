from app.repositories.documents_repository import DocumentsRepository
from app.schemas.document_schema import DocumentCreateRequest, DocumentResponse
from app.services.summarizer_service import SummarizerService


class DocumentsService:
    def __init__(
        self,
        repo: DocumentsRepository | None = None,
        summarizer: SummarizerService | None = None,
    ) -> None:
        """Author: Akhil Chaudhary

        Initialize the documents service with repository and summarizer dependencies.
        """
        self._repo = repo or DocumentsRepository()
        self._summarizer = summarizer or SummarizerService()

    def create(self, payload: DocumentCreateRequest) -> DocumentResponse:
        """Author: Akhil Chaudhary

        Create and persist a new document from the incoming API payload.
        """
        return self._repo.create(title=payload.title, content=payload.content)

    def get(self, document_id: str) -> DocumentResponse | None:
        """Author: Akhil Chaudhary

        Fetch a document by UUID string.
        """
        return self._repo.get(document_id)

    def list(self) -> list[DocumentResponse]:
        """Author: Akhil Chaudhary

        Return all stored documents.
        """
        return self._repo.list()

    def delete(self, document_id: str) -> bool:
        """Author: Akhil Chaudhary

        Delete a document by UUID string.
        """
        return self._repo.delete(document_id)

    def summarize(self, document_id: str) -> str | None:
        """Author: Akhil Chaudhary

        Generate and persist a summary for the given document.
        """
        doc = self._repo.get(document_id)
        if doc is None:
            return None
        summary = self._summarizer.summarize(doc.content)
        self._repo.set_summary(document_id, summary)
        return summary

    def search(self, query: str) -> list[DocumentResponse]:
        """Author: Akhil Chaudhary

        Search documents by query string.
        """
        return self._repo.search(query)

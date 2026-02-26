from __future__ import annotations

import re
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.schemas.document_schema import DocumentResponse

_token_re = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def _tokenize(text: str) -> set[str]:
    """Author: Akhil Chaudhary

    Tokenize the given text into a set of normalized alphanumeric terms.
    """
    return {m.group(0).lower() for m in _token_re.finditer(text)}


@dataclass
class _DocRecord:
    doc: DocumentResponse
    tokens: set[str]


class DocumentsRepository:
    """In-memory repository with a small inverted index for basic full-text search."""

    def __init__(self) -> None:
        """Author: Akhil Chaudhary

        Initialize in-memory document storage and search index.
        """
        self._lock = threading.RLock()
        self._docs: dict[UUID, _DocRecord] = {}
        self._index: dict[str, set[UUID]] = {}

    def create(self, *, title: str, content: str) -> DocumentResponse:
        """Author: Akhil Chaudhary

        Create and store a new document record and update the inverted index.
        """
        with self._lock:
            doc_id = uuid4()
            doc = DocumentResponse(
                id=doc_id,
                title=title,
                content=content,
                summary=None,
                created_at=datetime.now(tz=timezone.utc),
            )

            tokens = _tokenize(f"{title} {content}")
            self._docs[doc_id] = _DocRecord(doc=doc, tokens=tokens)
            self._add_to_index(doc_id, tokens)
            return doc

    def get(self, document_id: str) -> DocumentResponse | None:
        """Author: Akhil Chaudhary

        Retrieve a document by UUID string; returns None for invalid UUID or missing record.
        """
        try:
            doc_uuid = UUID(document_id)
        except ValueError:
            return None

        with self._lock:
            rec = self._docs.get(doc_uuid)
            return rec.doc if rec else None

    def list(self) -> list[DocumentResponse]:
        """Author: Akhil Chaudhary

        List documents ordered by creation time (descending).
        """
        with self._lock:
            return sorted(
                (r.doc for r in self._docs.values()), key=lambda d: d.created_at, reverse=True
            )

    def delete(self, document_id: str) -> bool:
        """Author: Akhil Chaudhary

        Delete a document by UUID string and remove it from the inverted index.
        """
        try:
            doc_uuid = UUID(document_id)
        except ValueError:
            return False

        with self._lock:
            rec = self._docs.pop(doc_uuid, None)
            if rec is None:
                return False
            self._remove_from_index(doc_uuid, rec.tokens)
            return True

    def set_summary(self, document_id: str, summary: str) -> bool:
        """Author: Akhil Chaudhary

        Update the stored summary for a document.
        """
        try:
            doc_uuid = UUID(document_id)
        except ValueError:
            return False

        with self._lock:
            rec = self._docs.get(doc_uuid)
            if rec is None:
                return False
            rec.doc.summary = summary
            return True

    def search(self, query: str) -> list[DocumentResponse]:
        """Author: Akhil Chaudhary

        Perform a simple full-text search using the inverted index.
        """
        q_tokens = _tokenize(query)
        if not q_tokens:
            return []

        with self._lock:
            candidate_ids: set[UUID] | None = None
            for t in q_tokens:
                ids = self._index.get(t, set())
                candidate_ids = ids if candidate_ids is None else (candidate_ids & ids)
                if not candidate_ids:
                    return []

            docs = [self._docs[doc_id].doc for doc_id in candidate_ids]
            docs.sort(key=lambda d: d.created_at, reverse=True)
            return docs

    def _add_to_index(self, doc_id: UUID, tokens: set[str]) -> None:
        """Author: Akhil Chaudhary

        Add document tokens to the inverted index.
        """
        for t in tokens:
            bucket = self._index.get(t)
            if bucket is None:
                self._index[t] = {doc_id}
            else:
                bucket.add(doc_id)

    def _remove_from_index(self, doc_id: UUID, tokens: set[str]) -> None:
        """Author: Akhil Chaudhary

        Remove document tokens from the inverted index.
        """
        for t in tokens:
            bucket = self._index.get(t)
            if not bucket:
                continue
            bucket.discard(doc_id)
            if not bucket:
                self._index.pop(t, None)

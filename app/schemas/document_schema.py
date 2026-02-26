from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


class DocumentResponse(BaseModel):
    id: UUID
    title: str
    content: str
    summary: str | None
    created_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]


class DocumentSummaryResponse(BaseModel):
    id: str
    summary: str

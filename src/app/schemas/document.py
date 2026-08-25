from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict

"""
This schema is used to represent the response for the document upload endpoint.
"""
class DocumentUploadResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    job_id: uuid.UUID


class DocumentAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cleaned_text: str
    character_count: int
    word_count: int
    line_count: int
    paragraph_count: int
    unique_word_count: int
    average_word_length: float
    keywords: list[dict]
    created_at: datetime


"""
This schema is used to represent the response for the document endpoint.
"""
class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    file_type: str
    file_size: int
    status: str
    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None = None
    analysis: DocumentAnalysisResponse | None = None

"""
This schema is used to represent the response for the paginated documents endpoint.
"""
class PaginatedDocumentsResponse(BaseModel):
    items: list[DocumentResponse]
    page: int
    limit: int
    total: int
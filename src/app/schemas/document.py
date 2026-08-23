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

"""
This schema is used to represent the response for the document endpoint.
"""
class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id:uuid.UUID
    filename: str
    file_type:str
    file_size:int
    status:str
    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None = None

"""
This schema is used to represent the response for the paginated documents endpoint.
"""
class PaginatedDocumentsResponse(BaseModel):
    items: list[DocumentResponse]
    page: int
    limit: int
    total: int
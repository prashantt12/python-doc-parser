import uuid
from pydantic import BaseModel

"""
This schema is used to represent the response for the document upload endpoint.
"""
class DocumentUploadResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    job_id: uuid.UUID
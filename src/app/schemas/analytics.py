import uuid
from pydantic import BaseModel

class DocumentSearchResult(BaseModel):
    document_id: uuid.UUID
    filename: str
    matches: int

class DocumentStatisticsResponse(BaseModel):
    total_documents: int
    average_words: float
    median_words: float
    std_deviation: float
    minimum_words: int
    maximum_words: int

class DocumentAnalyticsResponse(BaseModel):
    documents_per_day: dict[str, int]
    documents_by_file_type: dict[str, int]
    average_file_size_bytes: float
    success_rate: float
    average_processing_time_seconds: float | None
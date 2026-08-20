import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class DocumentAnalysis(Base):
    __tablename__ = "document_analyses"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id"), primary_key=True
    )
    cleaned_text: Mapped[str] = mapped_column(Text, nullable=False)
    character_count: Mapped[int] = mapped_column(Integer, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    line_count: Mapped[int] = mapped_column(Integer, nullable=False)
    paragraph_count: Mapped[int] = mapped_column(Integer, nullable=False)
    unique_word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    average_word_length: Mapped[float] = mapped_column(Float, nullable=False)
    keywords: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
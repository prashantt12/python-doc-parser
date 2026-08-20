import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(16), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="UPLOADED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
from datetime import datetime, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document
from app.exceptions import *
from sqlalchemy import delete, func, select

"""
This function is used to create a new document in the database. It will not commit the session yet, so the document id will be generated but not yet assigned. This is to avoid race conditions when multiple documents are created at the same time.
"""
async def create_document(
    session: AsyncSession,
    *,
    id: uuid.UUID,
    user_id: uuid.UUID,
    filename: str,
    file_type: str,
    file_size: int,
    storage_path: str,
    status: str = "PROCESSING",
) -> Document:
    document = Document(
        id=id,
        user_id=user_id,
        filename=filename,
        file_type=file_type,
        file_size=file_size,
        storage_path=storage_path,
        status=status,
    )
    session.add(document)
    await session.flush() # This is used to generate the document id without full commit yet
    return document


"""
This function is used to list the documents for a given user. 
It will return a tuple of a list of documents and the total number of documents for the user.
"""
async def list_documents(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    page: int,
    limit: int,
) -> tuple[list[Document], int]:
    """Returns page of docs, total count for user."""
    offset = (page - 1) * limit

    # total number of documents for the user
    total_result = await session.execute(
        select(func.count())
        .select_from(Document)
        .where(Document.user_id == user_id)
    )
    total = total_result.scalar_one()

    # list of documents for the user
    result = await session.execute(
        select(Document)
        .where(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    return list(result.scalars().all()), total


"""
This function is used to get a document by its id and the user id.
It will return the document if it exists, otherwise it will return None.
"""
async def get_document_by_id(
    session: AsyncSession,
    *,
    document_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Document | None:
    result = await session.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == user_id,
        )
    )
    return result.scalar_one_or_none() #return the document if it exists, otherwise return None

"""
This function is used to delete a document row from the database.
"""
async def delete_document_row(
    session:AsyncSession,
    *,
    document: Document,
) -> None:
    await session.delete(document)

"""
Function to get a document by id.
"""
async def get_document_by_id_only(
    session: AsyncSession,
    *,
    document_id: uuid.UUID,
) -> Document | None:
    result = await session.execute(
        select(Document).where(Document.id == document_id)
    )
    return result.scalar_one_or_none()

"""
Mark the status of a document as COMPLETED.
"""
async def mark_document_completed(
    session: AsyncSession,
    *,
    document_id: uuid.UUID,
) -> None:
    result = await session.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one()
    document.status = "COMPLETED"
    document.processed_at = datetime.now(timezone.utc)


async def mark_document_failed(
    session: AsyncSession,
    *,
    document_id: uuid.UUID,
) -> None:
    result = await session.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one()
    document.status = "FAILED"
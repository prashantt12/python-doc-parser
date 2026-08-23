import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document
from app.exceptions import *

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
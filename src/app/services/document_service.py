import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import DocumentNotFoundError
from app.models.analysis import DocumentAnalysis
from app.models.document import Document
from app.repositories import analysis as analysis_repo
from app.repositories import document as document_repo
from app.repositories import job as job_repo
from app.utils.files import (
    build_storage_path,
    sanitize_filename,
    validate_file_size,
    validate_file_type,
)

MAX_PAGE_LIMIT = 100

"""
This function is used to upload a document to the database and the storage.
"""
async def upload_document(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    upload: UploadFile
) -> tuple[uuid.UUID, str, uuid.UUID]:
    filename = upload.filename or "upload"
    file_type = validate_file_type(filename)

    data = await upload.read()
    validate_file_size(len(data))

    document_id = uuid.uuid4()
    safe_name = sanitize_filename(filename)
    path = build_storage_path(
        user_id=user_id,
        document_id=document_id,
        file_type=file_type
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

    document = await document_repo.create_document(
        session,
        id=document_id,
        user_id = user_id,
        filename=safe_name,
        file_type=file_type,
        file_size=len(data),
        storage_path=str(path),
        status="PROCESSING"
    )

    job = await job_repo.create_job(
        session, document_id=document.id
    )
    await session.commit()

    return document.id, document.status, job.id

"""
Enforces pagination limits and clamps values to valid ranges.
"""
def _clamp_pagination(
    page: int,
    limit: int
) -> tuple[int,int]:
    page = max(page, 1)
    limit = min(max(limit,1), MAX_PAGE_LIMIT)
    return page, limit

"""
Returns (documents, page, limit, total) for the paginated response.
"""
async def list_documents(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[Document], int, int, int]:
    page, limit = _clamp_pagination(page, limit)
    items, total = await document_repo.list_documents(
        session, user_id=user_id, page=page, limit=limit
    )
    return items, page, limit, total

"""
Return document (and analysis when completed) or raise — API maps to 404 JSON.
"""
async def get_document(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    document_id: uuid.UUID,
) -> tuple[Document, DocumentAnalysis | None]:
    document = await document_repo.get_document_by_id(
        session, document_id=document_id, user_id=user_id
    )
    if document is None:
        raise DocumentNotFoundError()
    analysis = None
    if document.status == "COMPLETED":
        analysis = await analysis_repo.get_analysis_by_document_id(
            session, document_id=document_id
        )
    return document, analysis

async def delete_document(
    session: AsyncSession,
    *,
    user_id:uuid.UUID,
    document_id:uuid.UUID,
) -> None:
    document, _ = await get_document(
        session, user_id=user_id, document_id=document_id
    )
    # delete all jobs for the document before deleting the document row
    await job_repo.delete_jobs_for_document(
        session, document_id=document_id
    )
    # delete all analysis for the document
    await analysis_repo.delete_analysis_for_document(
        session, document_id=document_id
    )
    # delete the document row
    await document_repo.delete_document_row(
        session, document=document
    )
    await session.commit()

    file_path = Path(document.storage_path)
    if file_path.is_file():
        file_path.unlink()
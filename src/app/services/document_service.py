import uuid
from pathlib import Path
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import document as document_repo
from app.repositories import job as job_repo
from app.utils.files import *

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

    document.id = document_id # This is used to assign the document id to the document object

    job = await job_repo.create_job(
        session, document_id=document.id
    )
    await session.commit()

    return document.id, document.status, job.id
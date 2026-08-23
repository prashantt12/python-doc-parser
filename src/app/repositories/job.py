import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import Job
from sqlalchemy import delete
"""
This function is used to create a new job in the database. It will not commit the session yet, so the job id will be generated but not yet assigned. This is to avoid race conditions when multiple jobs are created at the same time.
"""
async def create_job(
    session: AsyncSession,
    *,
    document_id: uuid.UUID,
) -> Job:
    job = Job(
        document_id=document_id,
        type = "PROCESS_DOCUMENT",
        status = "PENDING",
    )
    session.add(job)
    await session.flush()
    return job


"""
This function is used to delete all jobs for a given document before deleting the document row.
"""
async def delete_jobs_for_document(
    session: AsyncSession,
    *,
    document_id: uuid.UUID,
) -> None:
    await session.execute(
        delete(Job).where(Job.document_id == document_id)
    )
from datetime import datetime, timedelta, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import Job
from sqlalchemy import delete, select
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

"""
Pick one due PENDING job and mark it as RUNNING.
"""
async def claim_pending_job(
    session: AsyncSession,
) -> Job | None:
    now = datetime.now(timezone.utc)
    
    # select the first job that is pending and has no next retry time or the next retry time is in the past
    result = await session.execute(
        select(Job).where(
            Job.status == "PENDING",
            (Job.next_retry_at.is_(None)) | (Job.next_retry_at <= now),
        )
        .order_by(Job.created_at)
        .limit(1)
        .with_for_update(skip_locked=True) # lock the selected row for update (no other session/worker can lock the same row)
    )

    job = result.scalar_one_or_none()
    if job is None:
        return None
    
    job.status = "RUNNING" # mark the job as running
    job.attempts += 1 # increment the number of attempts
    job.started_at = now # set the started_at time
    job.error = None # clear the error
    await session.flush() # flush the session to update the job in the database
    return job


"""
Mark the status of a job as COMPLETED.
"""
async def mark_job_completed(
    session: AsyncSession,
    *,
    job_id: uuid.UUID,
) -> None:
    result = await session.execute(
        select(Job).where(Job.id == job_id)
    )
    job = result.scalar_one()
    job.status = "COMPLETED"
    job.completed_at = datetime.now(timezone.utc)


"""
Mark the status of a job as FAILED.
"""
async def mark_job_failed(
    session: AsyncSession,
    *,
    job_id: uuid.UUID,
    error: str,
) -> None:
    result = await session.execute(
        select(Job).where(Job.id == job_id)
    )
    job = result.scalar_one()
    job.status = "FAILED"
    job.completed_at = datetime.now(timezone.utc)
    job.error = error


"""
Schedule a job to be retried after a delay. Retry Backoff algorithm.
"""
async def schedule_job_retry(
    session: AsyncSession,
    *,
    job_id: uuid.UUID,
    error: str,
    delay_seconds: int,
) -> None:
    result = await session.execute(
        select(Job).where(Job.id == job_id)
    )
    job = result.scalar_one()
    job.status = "PENDING"
    job.error = error
    job.next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds) # set the next retry time


"""
Get a job by id
"""
async def get_job_by_id(
    session: AsyncSession,
    *,
    job_id: uuid.UUID,
) -> Job | None:
    result = await session.execute(
        select(Job).where(Job.id == job_id)
    )
    return result.scalar_one_or_none()
import asyncio
import logging
import uuid

from app.config import settings
from app.db import SessionLocal
from app.exceptions import DocumentProcessingError
from app.repositories import document as document_repo
from app.repositories import job as job_repo
from app.services import processing_service

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 1.0

"""
This function is used to retry the job after a certain delay.
"""
def _retry_delay_seconds(attempt: int) -> int:
    return 2 ** max(attempt - 1, 0)

"""
This function is used to process a single job.
"""
async def _process_one_job(job_id: uuid.UUID, document_id: uuid.UUID) -> None:
    # create a session to get the document
    async with SessionLocal() as session:
        # get the document by id only
        document = await document_repo.get_document_by_id_only(
            session,
            document_id=document_id,
        )
        # if the document is not found, raise an error
        if document is None:
            raise DocumentProcessingError(
                f"Document {document_id} not found",
                retryable=False,
            )
        # if document is found, process the document
        await processing_service.process_document(session, document=document)
        # mark the job as completed
        await job_repo.mark_job_completed(session, job_id=job_id)
        # mark the document as completed
        await document_repo.mark_document_completed(
            session,
            document_id=document_id,
        )
        await session.commit()
        logger.info(
            "processing_completed job_id=%s document_id=%s",
            job_id,
            document_id,
        )

"""
This function is used to handle the failure of a job.
"""
async def _handle_failure(
    job_id: uuid.UUID,
    document_id: uuid.UUID,
    exc: Exception,
) -> None:
    # get the message of the exception
    message = str(exc)
    print(f"Error: {exc}")
    retryable = getattr(exc, "retryable", True) # get the retryable attribute of the exception, default to True if not set

    async with SessionLocal() as session:
        # get the job by id
        job = await job_repo.get_job_by_id(session, job_id=job_id)
        # if the job is not found, return
        if job is None:
            return
        # if the job is retryable and the attempts are less than the max retry attempts, schedule a retry
        if retryable and job.attempts < settings.max_retry_attempts:
            delay = _retry_delay_seconds(job.attempts) # calculate the delay for the next retry
            # schedule a retry for the job
            await job_repo.schedule_job_retry(
                session,
                job_id=job_id,
                error=message,
                delay_seconds=delay,
            )
            logger.warning(
                "processing_failed job_id=%s retry_in=%ss error=%s",
                job_id,
                delay,
                message,
            )
        else: # in the else because the job is not retryable.

            # mark the job as failed
            await job_repo.mark_job_failed(session, job_id=job_id, error=message)
            # mark the document as failed
            await document_repo.mark_document_failed(
                session,
                document_id=document_id,
            )
            logger.error(
                "processing_failed job_id=%s permanent error=%s",
                job_id,
                message,
            )
        await session.commit()

"""
This function is used to run the worker. It is a loop that will continue to run until the stop event is set.
"""
async def run_worker(stop_event: asyncio.Event) -> None:
    logger.info("worker_started")
    while not stop_event.is_set(): # continue to run until the stop event is set
        try:
            async with SessionLocal() as session:
                # claim a pending job
                job = await job_repo.claim_pending_job(session)
                # if the job is not found, sleep for the poll interval
                if job is None:
                    await asyncio.sleep(POLL_INTERVAL_SECONDS)
                    continue
                job_id = job.id # get the job id
                document_id = job.document_id # get the document id

                 # commit the session because the job is claimed and we need to update the job status so the job is not claimed by another worker.
                await session.commit()
            try:
                # process the job
                await _process_one_job(job_id, document_id)
            # if the job processing fails, handle the failure
            except DocumentProcessingError as exc:
                # handle the failure of the job
                await _handle_failure(job_id, document_id, exc)
            # if any other exception occurs, handle the failure
            except Exception as exc:
                # handle the failure of the job
                await _handle_failure(
                    job_id,
                    document_id,
                    DocumentProcessingError(str(exc), retryable=True),
                )
        except asyncio.CancelledError: # if the worker is cancelled, break the loop
            break
        except Exception: # if any other exception occurs, log the error and sleep for the poll interval
            logger.exception("worker_loop_error")
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
    logger.info("worker_stopped")

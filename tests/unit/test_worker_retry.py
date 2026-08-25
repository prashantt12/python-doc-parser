import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.exceptions import DocumentProcessingError
from app.workers.document_worker import _handle_failure, _retry_delay_seconds


def test_retry_delay_seconds_uses_exponential_backoff() -> None:
    assert _retry_delay_seconds(1) == 1
    assert _retry_delay_seconds(2) == 2
    assert _retry_delay_seconds(3) == 4


@pytest.mark.asyncio
async def test_handle_failure_schedules_retry_when_retryable_and_under_max() -> None:
    job_id = uuid.uuid4()
    document_id = uuid.uuid4()
    exc = DocumentProcessingError("temporary", retryable=True)

    mock_job = type("Job", (), {"attempts": 1})()

    with (
        patch("app.workers.document_worker.SessionLocal") as session_local,
        patch("app.workers.document_worker.job_repo.get_job_by_id", new_callable=AsyncMock) as get_job,
        patch("app.workers.document_worker.job_repo.schedule_job_retry", new_callable=AsyncMock) as schedule_retry,
        patch("app.workers.document_worker.job_repo.mark_job_failed", new_callable=AsyncMock) as mark_failed,
    ):
        session = AsyncMock()
        session_local.return_value.__aenter__.return_value = session
        get_job.return_value = mock_job

        await _handle_failure(job_id, document_id, exc)

        schedule_retry.assert_awaited_once()
        mark_failed.assert_not_awaited()
        session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_failure_marks_failed_when_not_retryable() -> None:
    job_id = uuid.uuid4()
    document_id = uuid.uuid4()
    exc = DocumentProcessingError("permanent", retryable=False)

    mock_job = type("Job", (), {"attempts": 1})()

    with (
        patch("app.workers.document_worker.SessionLocal") as session_local,
        patch("app.workers.document_worker.job_repo.get_job_by_id", new_callable=AsyncMock) as get_job,
        patch("app.workers.document_worker.job_repo.schedule_job_retry", new_callable=AsyncMock) as schedule_retry,
        patch("app.workers.document_worker.job_repo.mark_job_failed", new_callable=AsyncMock) as mark_failed,
        patch("app.workers.document_worker.document_repo.mark_document_failed", new_callable=AsyncMock) as mark_doc_failed,
    ):
        session = AsyncMock()
        session_local.return_value.__aenter__.return_value = session
        get_job.return_value = mock_job

        await _handle_failure(job_id, document_id, exc)

        schedule_retry.assert_not_awaited()
        mark_failed.assert_awaited_once()
        mark_doc_failed.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_failure_marks_failed_when_attempts_exhausted() -> None:
    job_id = uuid.uuid4()
    document_id = uuid.uuid4()
    exc = DocumentProcessingError("still failing", retryable=True)

    mock_job = type("Job", (), {"attempts": 3})()

    with (
        patch("app.workers.document_worker.SessionLocal") as session_local,
        patch("app.workers.document_worker.job_repo.get_job_by_id", new_callable=AsyncMock) as get_job,
        patch("app.workers.document_worker.job_repo.schedule_job_retry", new_callable=AsyncMock) as schedule_retry,
        patch("app.workers.document_worker.job_repo.mark_job_failed", new_callable=AsyncMock) as mark_failed,
        patch("app.workers.document_worker.document_repo.mark_document_failed", new_callable=AsyncMock),
        patch("app.workers.document_worker.settings.max_retry_attempts", 3),
    ):
        session = AsyncMock()
        session_local.return_value.__aenter__.return_value = session
        get_job.return_value = mock_job

        await _handle_failure(job_id, document_id, exc)

        schedule_retry.assert_not_awaited()
        mark_failed.assert_awaited_once()

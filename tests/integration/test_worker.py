import uuid
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.config import settings
import app.db as db
from app.exceptions import DocumentProcessingError
from app.models.analysis import DocumentAnalysis
from app.models.document import Document
from app.repositories import analysis as analysis_repo
from app.services import processing_service
from tests.helpers import upload_fixture, wait_for_job_status


@pytest.mark.asyncio
async def test_upload_processes_to_completed_with_analysis(
    client_with_worker: AsyncClient,
) -> None:
    payload = await upload_fixture(client_with_worker)
    job = await wait_for_job_status(
        client_with_worker,
        payload["job_id"],
        status="COMPLETED",
    )
    assert job["attempts"] == 1
    assert job["error"] is None

    document_response = await client_with_worker.get(
        f"/documents/{payload['document_id']}"
    )
    assert document_response.status_code == 200
    document = document_response.json()
    assert document["status"] == "COMPLETED"
    assert document["processed_at"] is not None
    assert document["analysis"] is not None
    assert "hello" in document["analysis"]["cleaned_text"].lower()
    assert document["analysis"]["word_count"] > 0
    assert len(document["analysis"]["keywords"]) > 0

    async with db.SessionLocal() as session:
        analysis = await analysis_repo.get_analysis_by_document_id(
            session,
            document_id=uuid.UUID(payload["document_id"]),
        )
    assert analysis is not None


@pytest.mark.asyncio
async def test_non_retryable_failure_marks_job_and_document_failed(
    client_with_worker: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = await upload_fixture(client_with_worker)

    async with db.SessionLocal() as session:
        document = (
            await session.execute(
                select(Document).where(
                    Document.id == uuid.UUID(payload["document_id"])
                )
            )
        ).scalar_one()
        Path(document.storage_path).unlink()

    job = await wait_for_job_status(
        client_with_worker,
        payload["job_id"],
        status="FAILED",
    )
    assert job["attempts"] == 1
    assert "not found" in (job["error"] or "").lower()

    document_response = await client_with_worker.get(
        f"/documents/{payload['document_id']}"
    )
    assert document_response.json()["status"] == "FAILED"


@pytest.mark.asyncio
async def test_retryable_failures_retry_until_max_attempts(
    client_with_worker: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def always_fail(*_args, **_kwargs) -> None:
        raise DocumentProcessingError("transient failure", retryable=True)

    monkeypatch.setattr(processing_service, "process_document", always_fail)

    payload = await upload_fixture(client_with_worker)
    job = await wait_for_job_status(
        client_with_worker,
        payload["job_id"],
        status="FAILED",
        timeout=15.0,
    )
    assert job["attempts"] == settings.max_retry_attempts
    assert job["error"] == "transient failure"

    document_response = await client_with_worker.get(
        f"/documents/{payload['document_id']}"
    )
    assert document_response.json()["status"] == "FAILED"

    async with db.SessionLocal() as session:
        analysis = (
            await session.execute(select(DocumentAnalysis))
        ).scalar_one_or_none()
    assert analysis is None

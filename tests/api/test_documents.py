import uuid
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select

import app.db as db
from app.config import settings
from app.models.document import Document
from app.models.job import Job
from tests.helpers import upload_fixture


@pytest.mark.asyncio
async def test_upload_rejects_unsupported_file_type(client_no_worker: AsyncClient) -> None:
    response = await client_no_worker.post(
        "/documents",
        files={"file": ("report.docx", b"fake", "application/octet-stream")},
    )
    assert response.status_code == 400
    assert response.json()["error"] == "UNSUPPORTED_FILE_TYPE"


@pytest.mark.asyncio
async def test_upload_rejects_oversized_file(
    client_no_worker: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "max_file_size", 10)
    response = await client_no_worker.post(
        "/documents",
        files={"file": ("sample.txt", b"x" * 20, "text/plain")},
    )
    assert response.status_code == 400
    assert response.json()["error"] == "FILE_TOO_LARGE"


@pytest.mark.asyncio
async def test_upload_creates_file_document_and_job_rows(
    client_no_worker: AsyncClient,
    test_storage: Path,
) -> None:
    payload = await upload_fixture(client_no_worker)

    assert payload["status"] == "PROCESSING"
    document_id = uuid.UUID(payload["document_id"])
    job_id = uuid.UUID(payload["job_id"])

    async with db.SessionLocal() as session:
        document = (
            await session.execute(
                select(Document).where(Document.id == document_id)
            )
        ).scalar_one()
        job = (
            await session.execute(select(Job).where(Job.id == job_id))
        ).scalar_one()

    assert document.status == "PROCESSING"
    assert document.filename == "sample.txt"
    assert job.status == "PENDING"
    assert job.document_id == document_id
    assert Path(document.storage_path).is_file()


@pytest.mark.asyncio
async def test_list_documents_pagination(client_no_worker: AsyncClient) -> None:
    for index in range(3):
        await upload_fixture(
            client_no_worker,
            filename="sample.txt",
        )

    page_one = await client_no_worker.get("/documents", params={"page": 1, "limit": 2})
    assert page_one.status_code == 200
    data = page_one.json()
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["limit"] == 2
    assert len(data["items"]) == 2

    page_two = await client_no_worker.get("/documents", params={"page": 2, "limit": 2})
    assert page_two.status_code == 200
    data = page_two.json()
    assert data["page"] == 2
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_list_documents_rejects_limit_above_max(
    client_no_worker: AsyncClient,
) -> None:
    response = await client_no_worker.get("/documents", params={"page": 1, "limit": 101})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_document_returns_404_for_unknown_id(
    client_no_worker: AsyncClient,
) -> None:
    response = await client_no_worker.get(f"/documents/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json()["error"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_delete_removes_rows_and_file(client_no_worker: AsyncClient) -> None:
    payload = await upload_fixture(client_no_worker)
    document_id = payload["document_id"]

    get_response = await client_no_worker.get(f"/documents/{document_id}")
    storage_path = None
    async with db.SessionLocal() as session:
        document = (
            await session.execute(
                select(Document).where(Document.id == uuid.UUID(document_id))
            )
        ).scalar_one()
        storage_path = Path(document.storage_path)
    assert storage_path.is_file()

    delete_response = await client_no_worker.delete(f"/documents/{document_id}")
    assert delete_response.status_code == 204
    assert not storage_path.exists()

    async with db.SessionLocal() as session:
        remaining_docs = (
            await session.execute(select(func.count()).select_from(Document))
        ).scalar_one()
        remaining_jobs = (
            await session.execute(select(func.count()).select_from(Job))
        ).scalar_one()
    assert remaining_docs == 0
    assert remaining_jobs == 0


@pytest.mark.asyncio
async def test_delete_unknown_document_returns_404(client_no_worker: AsyncClient) -> None:
    response = await client_no_worker.delete(f"/documents/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json()["error"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_delete_succeeds_when_file_already_missing(
    client_no_worker: AsyncClient,
) -> None:
    payload = await upload_fixture(client_no_worker)
    document_id = payload["document_id"]

    async with db.SessionLocal() as session:
        document = (
            await session.execute(
                select(Document).where(Document.id == uuid.UUID(document_id))
            )
        ).scalar_one()
        Path(document.storage_path).unlink()

    response = await client_no_worker.delete(f"/documents/{document_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_uploaded_document_stays_processing_without_worker(
    client_no_worker: AsyncClient,
) -> None:
    payload = await upload_fixture(client_no_worker)

    response = await client_no_worker.get(f"/documents/{payload['document_id']}")
    assert response.status_code == 200
    assert response.json()["status"] == "PROCESSING"
    assert response.json()["analysis"] is None

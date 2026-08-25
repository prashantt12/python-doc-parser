import pytest
from httpx import AsyncClient

from tests.helpers import upload_and_complete


@pytest.mark.asyncio
async def test_analytics_returns_empty_defaults_when_no_documents(
    client_no_worker: AsyncClient,
) -> None:
    response = await client_no_worker.get("/analytics/documents")
    assert response.status_code == 200
    assert response.json() == {
        "documents_per_day": {},
        "documents_by_file_type": {},
        "average_file_size_bytes": 0.0,
        "success_rate": 0.0,
        "average_processing_time_seconds": None,
    }


@pytest.mark.asyncio
async def test_analytics_returns_expected_shape_after_completed_upload(
    client_with_worker: AsyncClient,
) -> None:
    await upload_and_complete(client_with_worker)

    response = await client_with_worker.get("/analytics/documents")
    assert response.status_code == 200
    data = response.json()

    assert data["documents_by_file_type"]["txt"] == 1
    assert len(data["documents_per_day"]) == 1
    assert data["average_file_size_bytes"] > 0
    assert data["success_rate"] == 1.0
    assert data["average_processing_time_seconds"] is not None
    assert data["average_processing_time_seconds"] >= 0

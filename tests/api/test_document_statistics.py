import pytest
from httpx import AsyncClient

from tests.helpers import upload_and_complete


@pytest.mark.asyncio
async def test_statistics_returns_zeros_when_no_completed_documents(
    client_no_worker: AsyncClient,
) -> None:
    response = await client_no_worker.get("/documents/statistics")
    assert response.status_code == 200
    assert response.json() == {
        "total_documents": 0,
        "average_words": 0.0,
        "median_words": 0.0,
        "std_deviation": 0.0,
        "minimum_words": 0,
        "maximum_words": 0,
    }


@pytest.mark.asyncio
async def test_statistics_returns_expected_shape_after_upload(
    client_with_worker: AsyncClient,
) -> None:
    await upload_and_complete(client_with_worker)

    response = await client_with_worker.get("/documents/statistics")
    assert response.status_code == 200
    data = response.json()

    assert data["total_documents"] == 1
    assert data["minimum_words"] == data["maximum_words"]
    assert data["average_words"] == data["median_words"]
    assert data["minimum_words"] > 0
    assert data["std_deviation"] == 0.0

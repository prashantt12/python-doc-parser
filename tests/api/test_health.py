import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_ok(client_no_worker: AsyncClient) -> None:
    response = await client_no_worker.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_ready_returns_healthy_components(
    client_no_worker: AsyncClient,
) -> None:
    response = await client_no_worker.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "healthy"
    assert data["storage"] == "healthy"


@pytest.mark.asyncio
async def test_request_id_is_returned_in_response_header(
    client_no_worker: AsyncClient,
) -> None:
    response = await client_no_worker.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")


@pytest.mark.asyncio
async def test_request_id_echoes_client_header(client_no_worker: AsyncClient) -> None:
    response = await client_no_worker.get(
        "/health",
        headers={"X-Request-ID": "test-request-123"},
    )
    assert response.headers.get("X-Request-ID") == "test-request-123"

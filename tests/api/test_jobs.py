import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_job_returns_404_for_unknown_id(client_no_worker: AsyncClient) -> None:
    response = await client_no_worker.get(f"/jobs/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json()["error"] == "JOB_NOT_FOUND"

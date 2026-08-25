import asyncio
import time
from pathlib import Path

import pytest
from httpx import AsyncClient

FIXTURES_DIR = Path(__file__).parent / "fixtures"


async def upload_fixture(
    client: AsyncClient,
    filename: str = "sample.txt",
) -> dict:
    content = (FIXTURES_DIR / filename).read_bytes()
    response = await client.post(
        "/documents",
        files={"file": (filename, content, "text/plain")},
    )
    assert response.status_code == 200, response.text
    return response.json()


async def wait_for_job_status(
    client: AsyncClient,
    job_id: str,
    *,
    status: str,
    timeout: float = 10.0,
) -> dict:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response = await client.get(f"/jobs/{job_id}")
        assert response.status_code == 200, response.text
        data = response.json()
        if data["status"] == status:
            return data
        if data["status"] == "FAILED" and status != "FAILED":
            pytest.fail(f"job failed unexpectedly: {data}")
        await asyncio.sleep(0.05)
    pytest.fail(f"job {job_id} did not reach status {status}")


async def upload_and_complete(client: AsyncClient) -> dict:
    payload = await upload_fixture(client)
    await wait_for_job_status(client, payload["job_id"], status="COMPLETED")
    return payload

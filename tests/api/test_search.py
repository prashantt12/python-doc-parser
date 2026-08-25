import pytest
from httpx import AsyncClient

from tests.helpers import upload_and_complete, upload_fixture


@pytest.mark.asyncio
async def test_search_returns_empty_when_no_completed_documents(
    client_no_worker: AsyncClient,
) -> None:
    await upload_fixture(client_no_worker)

    response = await client_no_worker.get("/documents/search", params={"q": "hello"})
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_search_finds_known_word_in_completed_document(
    client_with_worker: AsyncClient,
) -> None:
    payload = await upload_and_complete(client_with_worker)

    response = await client_with_worker.get("/documents/search", params={"q": "hello"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1

    match = next(
        item for item in results if item["document_id"] == payload["document_id"]
    )
    assert match["filename"] == "sample.txt"
    assert match["matches"] >= 1


@pytest.mark.asyncio
async def test_search_returns_empty_for_unknown_word(
    client_with_worker: AsyncClient,
) -> None:
    await upload_and_complete(client_with_worker)

    response = await client_with_worker.get(
        "/documents/search",
        params={"q": "zzzznotfound"},
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_search_rejects_empty_query(client_with_worker: AsyncClient) -> None:
    response = await client_with_worker.get("/documents/search", params={"q": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_route_is_not_treated_as_document_id(
    client_with_worker: AsyncClient,
) -> None:
    response = await client_with_worker.get("/documents/search", params={"q": "test"})
    assert response.status_code == 200

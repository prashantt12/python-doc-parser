import asyncio
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import app.db as db
import app.workers.document_worker as document_worker
from app.config import settings
from app.main import create_app


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        if asyncio.iscoroutinefunction(getattr(item, "obj", None)):
            item.add_marker(pytest.mark.asyncio(loop_scope="session"))


@pytest_asyncio.fixture(scope="session", autouse=True)
async def test_db_engine() -> AsyncIterator[None]:
    await db.engine.dispose()
    db.engine = create_async_engine(
        settings.database_url,
        echo=False,
        poolclass=NullPool,
    )
    db.SessionLocal = async_sessionmaker(db.engine, expire_on_commit=False)
    document_worker.SessionLocal = db.SessionLocal
    yield
    await db.engine.dispose()


@pytest.fixture(autouse=True)
def quiet_sqlalchemy() -> None:
    db.engine.echo = False


@pytest.fixture
def test_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    storage = tmp_path / "storage"
    storage.mkdir()
    monkeypatch.setattr(settings, "storage_path", storage)
    return storage


async def _truncate_tables() -> None:
    async with db.SessionLocal() as session:
        await session.execute(
            text(
                "TRUNCATE document_analyses, jobs, documents "
                "RESTART IDENTITY CASCADE"
            )
        )
        await session.commit()


@pytest.fixture
async def clean_db() -> AsyncIterator[None]:
    await _truncate_tables()
    yield
    await _truncate_tables()


@pytest.fixture
async def client_no_worker(
    test_storage: Path,
    clean_db: None,
) -> AsyncIterator[AsyncClient]:
    app = create_app(enable_worker=False)
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


@pytest.fixture
async def client_with_worker(
    test_storage: Path,
    clean_db: None,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncIterator[AsyncClient]:
    monkeypatch.setattr("app.workers.document_worker.POLL_INTERVAL_SECONDS", 0.05)
    monkeypatch.setattr(
        "app.workers.document_worker._retry_delay_seconds",
        lambda attempt: 0,
    )
    app = create_app(enable_worker=True)
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

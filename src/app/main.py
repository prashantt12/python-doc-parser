import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.documents import router as documents_router
from app.api.jobs import router as jobs_router
from app.config import settings
from app.db import SessionLocal
from app.exceptions import (
    DocumentNotFoundError,
    FileTooLargeError,
    JobNotFoundError,
    UnsupportedFileTypeError,
)
from app.logging import setup_logging
from app.repositories.user import get_or_create_demo_user
from app.workers.document_worker import run_worker as run_document_worker

setup_logging()


def create_app(*, enable_worker: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        settings.storage_path.mkdir(parents=True, exist_ok=True)
        async with SessionLocal() as session:
            user = await get_or_create_demo_user(session, settings.demo_user_email)
            app.state.demo_user_id = user.id

        stop_event = asyncio.Event()
        worker_task = None
        if enable_worker:
            worker_task = asyncio.create_task(run_document_worker(stop_event))
        yield

        if worker_task is not None:
            stop_event.set()
            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                pass

    app = FastAPI(title="Intelligent Document Parser", lifespan=lifespan)

    @app.exception_handler(UnsupportedFileTypeError)
    async def unsupported_file_type_handler(
        request: Request,
        exc: UnsupportedFileTypeError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "error": "UNSUPPORTED_FILE_TYPE",
                "message": str(exc),
            },
        )

    @app.exception_handler(FileTooLargeError)
    async def file_too_large_handler(
        request: Request,
        exc: FileTooLargeError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "error": "FILE_TOO_LARGE",
                "message": str(exc),
            },
        )

    @app.exception_handler(DocumentNotFoundError)
    async def document_not_found_handler(
        request: Request,
        exc: DocumentNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "error": "DOCUMENT_NOT_FOUND",
                "message": "Document does not exist",
            },
        )

    @app.exception_handler(JobNotFoundError)
    async def job_not_found_handler(
        request: Request,
        exc: JobNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "error": "JOB_NOT_FOUND",
                "message": "Job does not exist",
            },
        )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    async def ready() -> dict[str, str]:
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
        storage = Path(settings.storage_path)
        storage.mkdir(parents=True, exist_ok=True)
        probe = storage / ".write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)

        return {
            "status": "healthy",
            "database": "healthy",
            "storage": "healthy",
        }

    app.include_router(documents_router)
    app.include_router(jobs_router)
    return app


app = create_app()
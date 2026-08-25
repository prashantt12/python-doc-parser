import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.exceptions import JobNotFoundError
from app.repositories import job as job_repo
from app.schemas.job import JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> JobResponse:
    job = await job_repo.get_job_by_id(session, job_id=job_id)
    if job is None:
        raise JobNotFoundError()
    return JobResponse.model_validate(job)

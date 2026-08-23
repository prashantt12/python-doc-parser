import uuid
from fastapi import APIRouter, Depends, Request, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.schemas.document import DocumentUploadResponse
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("", response_model=DocumentUploadResponse)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
) -> DocumentUploadResponse:
    user_id: uuid.UUID = request.app.state.demo_user_id
    document_id, status, job_id = await document_service.upload_document(
        session,
        user_id=user_id,
        upload=file
    )
    return DocumentUploadResponse(
        document_id=document_id,
        status=status,
        job_id=job_id
    )
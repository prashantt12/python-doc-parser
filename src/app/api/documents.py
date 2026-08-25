import uuid
from fastapi import APIRouter, Depends, Request, File, UploadFile, Query, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.schemas.document import (
    DocumentAnalysisResponse,
    DocumentResponse,
    DocumentUploadResponse,
    PaginatedDocumentsResponse,
)
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

"""
This endpoint is used to list all documents for the user.
"""
@router.get("", response_model=PaginatedDocumentsResponse)
async def list_documents(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> PaginatedDocumentsResponse:
    user_id: uuid.UUID = request.app.state.demo_user_id
    items, page, limit, total = await document_service.list_documents(
        session,
        user_id=user_id,
        page=page,
        limit=limit
    )
    return PaginatedDocumentsResponse(
        items=[DocumentResponse.model_validate(d) for d in items],
        page=page,
        limit=limit,
        total=total
    )

"""
This endpoint is used to get a specific document for the user.
"""
@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    request: Request,
    document_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    user_id: uuid.UUID = request.app.state.demo_user_id
    document, analysis = await document_service.get_document(
        session, user_id=user_id, document_id=document_id
    )
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        file_type=document.file_type,
        file_size=document.file_size,
        status=document.status,
        created_at=document.created_at,
        updated_at=document.updated_at,
        processed_at=document.processed_at,
        analysis=(
            DocumentAnalysisResponse.model_validate(analysis)
            if analysis is not None
            else None
        ),
    )

"""
This endpoint is used to delete a specific document for the user.
"""
@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    request: Request,
    document_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> None:
    user_id: uuid.UUID = request.app.state.demo_user_id
    await document_service.delete_document(
        session, user_id=user_id, document_id=document_id
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
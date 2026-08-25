import uuid
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.schemas.analytics import DocumentAnalyticsResponse
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/documents", response_model=DocumentAnalyticsResponse)
async def get_document_analytics(
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> DocumentAnalyticsResponse:
    user_id:uuid.UUID = request.app.state.demo_user_id
    return await analytics_service.get_document_analytics(
        session, user_id=user_id
    )
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from app.models.analysis import DocumentAnalysis

"""
This function is used to delete all analysis for a given document before deleting the document row.
"""
async def delete_analysis_for_document(
    session: AsyncSession,
    *,
    document_id: uuid.UUID,
) -> None:
    await session.execute(
        delete(DocumentAnalysis).where(DocumentAnalysis.document_id == document_id)
    )

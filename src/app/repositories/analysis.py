import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import DocumentAnalysis
from app.utils.statistics import DocumentStats

"""
This function is used to create a new analysis for a document.
"""
async def create_analysis(
    session: AsyncSession,
    *,
    document_id: uuid.UUID,
    cleaned_text: str,
    stats: DocumentStats,
    keywords: list[dict],
) -> DocumentAnalysis:
    analysis = DocumentAnalysis(
        document_id=document_id,
        cleaned_text=cleaned_text,
        character_count=stats.character_count,
        word_count=stats.word_count,
        line_count=stats.line_count,
        paragraph_count=stats.paragraph_count,
        unique_word_count=stats.unique_word_count,
        average_word_length=stats.average_word_length,
        keywords=keywords,
    )
    session.add(analysis)
    await session.flush()
    return analysis

"""
This function is used to delete an analysis for a document.
"""
async def delete_analysis_for_document(
    session: AsyncSession,
    *,
    document_id: uuid.UUID,
) -> None:
    await session.execute(
        delete(DocumentAnalysis).where(DocumentAnalysis.document_id == document_id)
    )


async def get_analysis_by_document_id(
    session: AsyncSession,
    *,
    document_id: uuid.UUID,
) -> DocumentAnalysis | None:
    result = await session.execute(
        select(DocumentAnalysis).where(DocumentAnalysis.document_id == document_id)
    )
    return result.scalar_one_or_none()

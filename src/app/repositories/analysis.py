import uuid

from app.models.document import Document
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

"""
This function is used to get an analysis by document id.
"""
async def get_analysis_by_document_id(
    session: AsyncSession,
    *,
    document_id: uuid.UUID,
) -> DocumentAnalysis | None:
    result = await session.execute(
        select(DocumentAnalysis).where(DocumentAnalysis.document_id == document_id)
    )
    return result.scalar_one_or_none()

"""
This function is used to search the completed analyses for a user.
"""
async def search_completed_analyses(
    session: AsyncSession,
    *,
    user_id,
    query: str,
) -> list[tuple[uuid.UUID, str, str]]:
    pattern = f"%{query}%"  # Build a SQL pattern for the search query
    result = await session.execute(
        select(
            Document.id,
            Document.filename,
            DocumentAnalysis.cleaned_text
        )
        .join(DocumentAnalysis, DocumentAnalysis.document_id == Document.id)
        .where(
            Document.user_id == user_id,
            Document.status == "COMPLETED",
            DocumentAnalysis.cleaned_text.ilike(pattern),
        )
    )

    return list(result.all())

"""
This function is used to list the word counts for all completed documents for a user.
"""
async def list_word_counts_for_completed(session: AsyncSession, *, user_id: uuid.UUID) -> list[int]:
    result = await session.execute(
        select(DocumentAnalysis.word_count)
        .join(Document, Document.id == DocumentAnalysis.document_id)
        .where(
            Document.user_id == user_id,
            Document.status == "COMPLETED",
        )
    )
    return [row[0] for row in result.all()]
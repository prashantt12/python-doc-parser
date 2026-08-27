import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import DocumentProcessingError
from app.models.document import Document
from app.parsers.factory import get_parser
from app.repositories import analysis as analysis_repo
from app.utils.statistics import compute_statistics
from app.utils.text import clean_text, extract_keywords


logger = logging.getLogger(__name__)

"""
Parse file on disk, analyze text, persist document_analyses.
Does NOT update job/document status — worker does that after success.
"""
async def process_document(
    session: AsyncSession,
    document: Document
) -> None:
    path = Path(document.storage_path)
    if not path.is_file():
        raise DocumentProcessingError(
            f"File not found: {path}", retryable=False
        )
    try:
        parser = get_parser(document.file_type)
        raw_text = await parser.parse(path)
    except Exception as exc:
        raise DocumentProcessingError(
            f"Parse Failed: {exc}",
            retryable=True
        ) from exc
    
    logger.info(
        "document_parsed document_id=%s file_type=%s",
        document.id,
        document.file_type,
    )

    cleaned = clean_text(raw_text)
    stats = compute_statistics(cleaned)
    keywords = extract_keywords(cleaned)

    await analysis_repo.create_analysis(
        session,
        document_id=document.id,
        cleaned_text=cleaned,
        stats=stats,
        keywords=keywords,
    )
    logger.info("analysis_completed document_id=%s", document.id)


"""After attempt 1 fail wait 1s, after 2 wait 2s, after 3 wait 4s."""
def retry_delay_seconds(attempt: int) -> int:
    return 2 ** (attempt - 1)
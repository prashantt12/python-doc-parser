import uuid
from datetime import timezone
import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import analysis as analysis_repo
from app.repositories import document as document_repo
from app.schemas.analytics import (
    DocumentAnalyticsResponse,
    DocumentSearchResult,
    DocumentStatisticsResponse,
)

"""
This function is used to count the number of matches in a text for a query.
"""
def _count_matches(text: str, query: str) -> int:
    return text.lower().count(query.lower())

"""
This function is used to search the documents completed analyses for a user.
"""
async def search_documents(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    query: str,
) -> list[DocumentSearchResult]:
    # search the completed analyses for the user
    rows =await analysis_repo.search_completed_analyses(
        session, user_id=user_id, query=query
    )

    # create the search results
    results = [
        DocumentSearchResult(
            document_id=document_id,
            filename=filename,
            matches=_count_matches(cleaned_text, query),
        ) for document_id, filename, cleaned_text in rows
    ]

    results.sort(key = lambda item: item.matches, reverse=True) # sort the results by the number of matches in descending order
    return results

"""
This function is used to get the statistics for the documents for a user.
"""
async def get_document_statistics(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
) -> DocumentStatisticsResponse:
    word_counts = await analysis_repo.list_word_counts_for_completed(
        session, user_id=user_id
    )

    if not word_counts:
        return DocumentStatisticsResponse(
            total_documents=0,
            average_words=0,
            median_words=0,
            std_deviation=0,
            minimum_words=0,
            maximum_words=0,
        )
    # convert the word counts to a numpy array, dtype means data type
    arr = np.array(word_counts, dtype=np.float64)
    return DocumentStatisticsResponse(
        total_documents=len(word_counts),
        average_words = float(np.mean(arr)),
        median_words = float(np.median(arr)),
        std_deviation = float(np.std(arr)),
        minimum_words = int(np.min(arr)),
        maximum_words = int(np.max(arr)),
    )

"""
Function:
This function is used to get the analytics for the documents for a user.

Parameters:
    session: AsyncSession - The database session.
    user_id: uuid.UUID - The ID of the user.

Returns:
    DocumentAnalyticsResponse - The analytics for the documents for the user.
"""
async def get_document_analytics(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
) -> DocumentAnalyticsResponse:
    # list the documents for the user
    documents = await document_repo.list_documents_for_user(
        session, user_id=user_id
    )

    # if no documents are found, return the default response
    if not documents:
        return DocumentAnalyticsResponse(
            documents_per_day={},
            documents_by_file_type={},
            average_file_size_bytes=0.0,
            success_rate=0.0,
            average_processing_time_seconds=None,
        )

    # create a pandas dataframe from the documents, why because in result we need to perform calculations on the data, and pandas is a good tool for that
    df = pd.DataFrame(
        [
            {
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "status": doc.status,
                "created_at": doc.created_at,
                "processed_at": doc.processed_at,
            } for doc in documents
        ]
    )

    # convert the created_at column to a date string and count the number of documents per day
    df["created_day"] = df["created_at"].dt.tz_convert(timezone.utc).dt.strftime("%Y-%m-%d")
    documents_per_day = df["created_day"].value_counts().sort_index().to_dict()

    documents_by_file_type = df["file_type"].value_counts().to_dict()    # count the number of documents by file type
    average_file_size_bytes = float(df["file_size"].mean()) # calculate the average file size in bytes

    success_rate = float((df["status"] == "COMPLETED").mean()) # calculate the success rate
    completed = df[df["status"] == "COMPLETED"].dropna(subset=["processed_at"]) # get the completed documents and drop the rows with missing processed_at values

    # if no completed documents are found, return the default response
    if completed.empty:
        average_processing_time_seconds = None
    else:
        durations = (
            completed["processed_at"] - completed["created_at"]
        ).dt.total_seconds()
        average_processing_time_seconds = float(durations.mean()) # calculate the average processing time in seconds
    
    return DocumentAnalyticsResponse(
        documents_per_day=documents_per_day,
        documents_by_file_type=documents_by_file_type,
        average_file_size_bytes=average_file_size_bytes,
        success_rate=success_rate,
        average_processing_time_seconds=average_processing_time_seconds,
    )
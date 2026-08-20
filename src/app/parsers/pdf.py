"""
PDF parser for document parsing.

Function Description:
    This function is used to parse a PDF file and return the text content of the file.

    Args:
        path: Path to the PDF file.

    Returns:
        A string of the text content of the file.
"""

import asyncio
from pathlib import Path
from pypdf import PdfReader
from app.parsers.base import DocumentParser

class PDFParser(DocumentParser):
    # runs on a worker thread in the thread pool
    async def parse(self, path: Path) -> str:
        return await asyncio.to_thread(self._parse_sync, path)

    # runs on the main thread
    def _parse_sync(self, path: Path) -> str:
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)
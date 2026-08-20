"""
Text parser for document parsing.

Function Description:
    This function is used to parse a text file and return the text content of the file.

    Args:
        path: Path to the text file.

    Returns:
        A string of the text content of the file.
"""

from pathlib import Path
from app.parsers.base import DocumentParser

class TextParser(DocumentParser):
    async def parse(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="replace")
"""
Base class for document parsers.
"""

from abc import ABC, abstractmethod
from pathlib import Path

class DocumentParser(ABC):
    @abstractmethod
    async def parse(self, path: Path) -> str:
        """Return raw extracted text from the file at path."""
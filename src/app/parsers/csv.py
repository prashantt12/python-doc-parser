"""
CSV parser for document parsing.

Function Description:
    This function is used to parse a CSV file and return the text content of the file. 

    Args:
        path: Path to the CSV file.

    Returns:
        A string of the text content of the file.
"""

import csv
from pathlib import Path
from app.parsers.base import DocumentParser

class CSVParser(DocumentParser):
    async def parse(self, path: Path) -> str:
        lines: list[str] = []
        with path.open(encoding="utf-8", errors="replace", newline="") as handle:
            for row in csv.reader(handle):
                cells = [cell.strip() for cell in row if cell.strip()]
                if cells:
                    lines.append(" ".join(cells))
        return "/n".join(lines)
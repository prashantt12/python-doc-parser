"""
JSON parser for document parsing.

Function Description:
    This function is used to parse a JSON file and return the text content of the file.

    Args:
        path: Path to the JSON file.

    Returns:
        A string of the text content of the file.
"""

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from app.parsers.base import DocumentParser

def _flatten(value: Any) -> Iterator[str]:
    if value is None:
        return
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key)
            yield from _flatten(nested)
    elif isinstance(value, list):
        for item in value:
            yield from _flatten(item)
    else:
        yield str(value)

class JsonParser(DocumentParser):
    async def parse(self, path: Path) -> str:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        return " ".join(_flatten(data))
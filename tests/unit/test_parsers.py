from pathlib import Path

import pytest

from app.exceptions import UnsupportedFileTypeError
from app.parsers.factory import get_parser

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


@pytest.mark.asyncio
async def test_text_parser():
    text = await get_parser("txt").parse(FIXTURES / "sample.txt")
    assert "Hello" in text


@pytest.mark.asyncio
async def test_csv_parser():
    text = await get_parser("csv").parse(FIXTURES / "sample.csv")
    assert "engine" in text
    assert "torque" in text


@pytest.mark.asyncio
async def test_json_parser():
    text = await get_parser("json").parse(FIXTURES / "sample.json")
    assert "engine" in text
    assert "7000" in text


def test_factory_unknown_type():
    with pytest.raises(UnsupportedFileTypeError):
        get_parser("docx")


def test_factory_selects_expected_classes():
    assert type(get_parser("txt")).__name__ == "TextParser"
    assert type(get_parser("pdf")).__name__ == "PDFParser"
    assert type(get_parser("csv")).__name__ == "CSVParser"
    assert type(get_parser("json")).__name__ == "JsonParser"

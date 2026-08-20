from app.exceptions import UnsupportedFileTypeError
from app.parsers.base import DocumentParser
from app.parsers.text import TextParser
from app.parsers.pdf import PDFParser
from app.parsers.csv import CSVParser
from app.parsers.json import JsonParser

_PARSERS: dict[str, type[DocumentParser]] = {
    "txt": TextParser,
    "md": TextParser,
    "pdf": PDFParser,
    "csv": CSVParser,
    "json": JsonParser,
}

def get_parser(file_type:str) -> DocumentParser:
    parser_cls = _PARSERS.get(file_type.lower().lstrip("."))
    if parser_cls is None:
        raise UnsupportedFileTypeError(file_type)
    return parser_cls()
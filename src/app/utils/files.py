"""
This Utility File sits in front of Parsers to handle file operations and validation.
"""

import re
import uuid
from pathlib import Path
from app.config import settings
from app.exceptions import FileTooLargeError, UnsupportedFileTypeError

ALLOWED_EXTENSIONS = {"pdf", "txt", "csv", "json", "md"}

"""
This function is used to get the extension of a file.
"""
def extension_of(filename: str) -> str:
    return Path(filename).suffix.lower().lstrip(".")

"""
This function is used to validate the file type of a file.
"""
def validate_file_type(filename: str) -> str:
    file_type = extension_of(filename)
    if file_type not in ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeError(file_type)
    return file_type

"""
This function is used to validate the size of a file.
"""
def validate_file_size(size_bytes: int) -> None:
    if size_bytes > settings.max_file_size:
        raise FileTooLargeError(size_bytes, settings.max_file_size)

"""
This function is used to sanitize the filename of a file.
"""
def sanitize_filename(filename: str) -> str:
    name = Path(filename).name
    name = re.sub(r"[^\w.\-]+", "_", name)
    return (name[:255] or "upload")

"""
This function is used to build the storage path of a file.
"""
def build_storage_path(*, user_id: uuid.UUID, document_id: uuid.UUID, file_type: str) -> Path:
    return (
        settings.storage_path
        / f"user_{user_id}"
        / f"document_{document_id}"
        / f"original.{file_type}"
    )
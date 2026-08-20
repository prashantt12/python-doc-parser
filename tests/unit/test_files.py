from uuid import uuid4

import pytest

from app.exceptions import FileTooLargeError, UnsupportedFileTypeError
from app.utils.files import (
    build_storage_path,
    sanitize_filename,
    validate_file_size,
    validate_file_type,
)


def test_validate_file_type_accepts_pdf():
    assert validate_file_type("Manual.PDF") == "pdf"


def test_validate_file_type_rejects_docx():
    with pytest.raises(UnsupportedFileTypeError):
        validate_file_type("x.docx")


def test_sanitize_strips_path_traversal():
    name = sanitize_filename("../../weird name*.pdf")
    assert ".." not in name
    assert "/" not in name


def test_storage_path_uses_uuids_not_user_filename():
    path = build_storage_path(
        user_id=uuid4(),
        document_id=uuid4(),
        file_type="pdf",
    )
    assert path.name == "original.pdf"
    assert "user_" in str(path)
    assert "document_" in str(path)


def test_validate_file_size_rejects_oversized():
    with pytest.raises(FileTooLargeError):
        validate_file_size(11 * 1024 * 1024)

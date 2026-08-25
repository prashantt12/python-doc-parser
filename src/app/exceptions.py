class UnsupportedFileTypeError(Exception):
    def __init__(self, file_type: str) -> None:
        self.file_type = file_type
        super().__init__(f"Unsupported file type: {file_type}")

class FileTooLargeError(Exception):
    def __init__(self, size_bytes: int, max_bytes: int) -> None:
        self.size_bytes = size_bytes
        self.max_bytes = max_bytes
        super().__init__(f"File too large: {size_bytes} bytes, max allowed: {max_bytes} bytes")

class DocumentNotFoundError(Exception):
    pass

class JobNotFoundError(Exception):
    pass


class DocumentProcessingError(Exception):
    def __init__(self, message: str, *, retryable: bool = True) -> None:
        self.message = message
        self.retryable = retryable
        super().__init__(message)
import logging
import sys
from logging import LogRecord

from app.config import settings
from app.middleware.request_id import get_request_id


class RequestIdFilter(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


def setup_logging() -> None:
    logging.basicConfig(
        level=settings.log_level.upper(),
        format=(
            "%(asctime)s %(levelname)s [%(name)s] "
            "request_id=%(request_id)s %(message)s"
        ),
        stream=sys.stdout,
        force=True,
    )
    request_filter = RequestIdFilter()
    for handler in logging.root.handlers:
        if not any(isinstance(existing, RequestIdFilter) for existing in handler.filters):
            handler.addFilter(request_filter)

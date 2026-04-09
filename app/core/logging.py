import logging
import sys

try:
    from pythonjsonlogger import jsonlogger
except ImportError:  # pragma: no cover - exercised by local runtime, not logic tests
    jsonlogger = None


class _RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        if not hasattr(record, "agent"):
            record.agent = "-"
        if not hasattr(record, "duration_ms"):
            record.duration_ms = 0
        return True


def _build_formatter() -> logging.Formatter:
    if jsonlogger is not None:
        return jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(agent)s %(duration_ms)s"
        )

    return logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s "
        "request_id=%(request_id)s agent=%(agent)s duration_ms=%(duration_ms)s"
    )


def setup_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setFormatter(_build_formatter())
    log_handler.addFilter(_RequestContextFilter())

    root_logger.handlers = [log_handler]


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


setup_logging()

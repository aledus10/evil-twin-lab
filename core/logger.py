"""Centralized logging configuration for Evil Twin Lab."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from rich.logging import RichHandler


SUCCESS_LEVEL = 25
LOG_FILE_NAME = "evil-twin-lab.log"
MAX_LOG_BYTES = 2 * 1024 * 1024
BACKUP_COUNT = 3
_HANDLER_MARKER = "_evil_twin_lab_handler"


class EvilTwinLogger(logging.Logger):
    """Logger with a dedicated level for successful operations."""

    def success(self, message: object, *args: object, **kwargs: Any) -> None:
        """Log a successful operation while preserving deferred formatting."""
        if self.isEnabledFor(SUCCESS_LEVEL):
            self._log(SUCCESS_LEVEL, message, args, **kwargs)


def _register_success_level() -> None:
    """Register the custom SUCCESS level and logger class once per process."""
    logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")
    if logging.getLoggerClass() is not EvilTwinLogger:
        logging.setLoggerClass(EvilTwinLogger)


def _project_root() -> Path:
    """Return the project root independently of the current working directory."""
    return Path(__file__).resolve().parent.parent


def _is_managed_handler(handler: logging.Handler) -> bool:
    """Return whether a handler was created by this logging module."""
    return bool(getattr(handler, _HANDLER_MARKER, False))


def _mark_managed(handler: logging.Handler) -> logging.Handler:
    """Mark a handler so repeated configuration calls can identify it safely."""
    setattr(handler, _HANDLER_MARKER, True)
    return handler


def configure_logging() -> logging.Logger:
    """Configure Rich console and rotating file logging exactly once.

    Existing handlers that do not belong to Evil Twin Lab are left untouched.
    Repeated calls reuse the handlers created during the first call.
    """
    _register_success_level()

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    log_directory = _project_root() / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)
    log_path = log_directory / LOG_FILE_NAME

    managed_handlers = [
        handler for handler in root_logger.handlers if _is_managed_handler(handler)
    ]

    if not any(isinstance(handler, RichHandler) for handler in managed_handlers):
        console_handler = _mark_managed(
            RichHandler(
                level=logging.INFO,
                rich_tracebacks=True,
                show_path=False,
            )
        )
        console_handler.setFormatter(logging.Formatter("%(message)s"))
        root_logger.addHandler(console_handler)

    if not any(
        isinstance(handler, RotatingFileHandler)
        and Path(handler.baseFilename).resolve() == log_path.resolve()
        for handler in managed_handlers
    ):
        file_handler = _mark_managed(
            RotatingFileHandler(
                log_path,
                maxBytes=MAX_LOG_BYTES,
                backupCount=BACKUP_COUNT,
                encoding="utf-8",
            )
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> EvilTwinLogger:
    """Return a named Evil Twin Lab logger with the ``success`` method."""
    _register_success_level()
    logger = logging.getLogger(name)
    if not isinstance(logger, EvilTwinLogger):
        raise TypeError(f"Logger {name!r} was created before EvilTwinLogger setup")
    return logger

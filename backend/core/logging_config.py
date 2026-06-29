"""
backend/core/logging_config.py
Structured logging configuration using Python's logging module + structlog.
"""
from __future__ import annotations

import logging
import sys

import structlog


def configure_logging(debug: bool = False) -> None:
    """Configure structured logging for the application."""
    log_level = logging.DEBUG if debug else logging.INFO

    # Standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Suppress noisy third-party loggers
    for noisy in ["uvicorn.access", "sqlalchemy.engine", "lightkurve"]:
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Structlog processors
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if debug else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.getLogger("horizon").info(
        "Logging configured | level=%s | structured=%s",
        "DEBUG" if debug else "INFO",
        not debug,
    )

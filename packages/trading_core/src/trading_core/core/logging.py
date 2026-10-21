"""Structured logging bootstrap."""

from __future__ import annotations

import logging
import sys
from typing import Any, cast

import structlog


def configure_logging(log_level: str = "INFO") -> None:
    """Configure stdlib and structlog for JSON logs."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level)

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None, **kwargs: Any) -> structlog.stdlib.BoundLogger:
    """Return a structured logger optionally bound with context."""
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name).bind(**kwargs))

"""
Structured JSON logging manager with rotating file handler.
"""

import logging
import json
import uuid
import sys
import os
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, Optional


class JSONFormatter(logging.Formatter):
    """Custom formatter producing structured JSON log items."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include custom extra fields if attached to the log record
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_obj.update(record.extra)

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def configure_logging(log_level: str = "INFO", log_file: str = "logs/app.log") -> None:
    """Setup application root logger with JSON console output and rotating file handler."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)

    # Rotating file handler
    try:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10_485_760,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)
    except Exception as e:
        root_logger.warning(f"Failed to setup file logging: {e}")

    # Set specific log levels for third-party libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)


def get_request_id() -> str:
    """Generate or retrieve trace/request ID for execution context."""
    return str(uuid.uuid4())


def get_logger(name: str) -> logging.Logger:
    """Get a logger with configured formatters."""
    return logging.getLogger(name)
"""
Centralized logging configuration using loguru.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Union

from loguru import logger

# Remove default handler
logger.remove()

# Default format
DEFAULT_FORMAT = "<level>{level: <8}</level> | <cyan>{message}</cyan>"
FILE_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"


def setup_logger(
    level: str = "INFO",
    log_file: Optional[Union[Path, str]] = None,
    rotation: str = "1 MB",
    retention: str = "7 days",
    colorize: bool = True,
    format: str = DEFAULT_FORMAT,
) -> None:
    """
    Configure the global logger.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for log output
        rotation: When to rotate the log file
        retention: How long to keep old logs
        colorize: Whether to use colors in console output
        format: Log message format
    """
    # Console handler
    logger.add(
        sys.stderr,
        format=format,
        level=level,
        colorize=colorize,
    )

    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(log_path),
            format=FILE_FORMAT,
            level="DEBUG",
            rotation=rotation,
            retention=retention,
        )


# Export logger instance
__all__ = ["logger", "setup_logger"]

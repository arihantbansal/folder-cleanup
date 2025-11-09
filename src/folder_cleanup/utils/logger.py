"""Logging utilities with Rich integration."""

import logging
import sys
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler


# Global console instance
console = Console()


def setup_logger(name: str = "folder_cleanup", verbose: bool = False) -> logging.Logger:
    """
    Set up a logger with Rich formatting.

    Args:
        name: Logger name
        verbose: Enable verbose (DEBUG) logging

    Returns:
        logging.Logger: Configured logger instance

    Example:
        >>> logger = setup_logger("my_module", verbose=True)
        >>> logger.info("Processing started")
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create Rich handler
    handler = RichHandler(
        console=console,
        show_time=True,
        show_path=verbose,
        markup=True,
        rich_tracebacks=True,
        tracebacks_show_locals=verbose,
    )

    # Set format
    formatter = logging.Formatter(
        "%(message)s",
        datefmt="[%X]",
    )
    handler.setFormatter(formatter)

    # Add handler
    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (defaults to "folder_cleanup")

    Returns:
        logging.Logger: Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.warning("Something might be wrong")
    """
    return logging.getLogger(name or "folder_cleanup")

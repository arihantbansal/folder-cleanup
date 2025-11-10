"""Utility modules for folder-cleanup."""

from .config import load_config
from .logger import setup_logger, get_logger
from .file_utils import get_file_type, safe_read_file, is_text_file
from .errors import (
    show_ollama_connection_error,
    show_ollama_model_error,
    show_permission_error,
    show_ai_insights,
    show_processing_estimate,
)

__all__ = [
    "load_config",
    "setup_logger",
    "get_logger",
    "get_file_type",
    "safe_read_file",
    "is_text_file",
    "show_ollama_connection_error",
    "show_ollama_model_error",
    "show_permission_error",
    "show_ai_insights",
    "show_processing_estimate",
]

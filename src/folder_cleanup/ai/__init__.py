"""AI integration modules for folder-cleanup."""

from .ollama_client import OllamaClient
from .analyzer import FileAnalyzer

__all__ = ["OllamaClient", "FileAnalyzer"]

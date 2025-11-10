"""Configuration management utilities."""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from ..models.schemas import Config


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Ollama settings
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "deepseek-r1:7b"
    ollama_timeout: int = 120

    # File processing
    max_file_size_mb: int = 10
    max_content_length: int = 50000
    batch_size: int = 5

    # Logging
    log_level: str = "INFO"


def load_config(
    config_path: Optional[Path] = None,
    ollama_model: Optional[str] = None,
    dry_run: bool = True,
    verbose: bool = False,
    file_limit: Optional[int] = None,
    allowed_extensions: Optional[list[str]] = None,
    fast_mode: bool = False,
    show_ai_insights: bool = True,
) -> Config:
    """
    Load application configuration from environment and arguments.

    Args:
        config_path: Optional path to .env file
        ollama_model: Override Ollama model from command line
        dry_run: Enable dry-run mode
        verbose: Enable verbose logging
        file_limit: Maximum number of files to process
        allowed_extensions: Filter to only these file extensions
        fast_mode: Skip Phase 1 pattern discovery
        show_ai_insights: Display AI-discovered patterns

    Returns:
        Config: Application configuration object

    Example:
        >>> config = load_config(ollama_model="llama3.2:3b", file_limit=10)
        >>> print(config.file_limit)
        10
    """
    # Change to config directory if specified
    if config_path and config_path.exists():
        os.chdir(config_path.parent)

    # Load settings from environment
    settings = Settings()

    # Create config with overrides
    config = Config(
        ollama_host=settings.ollama_host,
        ollama_model=ollama_model or settings.ollama_model,
        ollama_timeout=settings.ollama_timeout,
        max_file_size_mb=settings.max_file_size_mb,
        max_content_length=settings.max_content_length,
        batch_size=settings.batch_size,
        dry_run=dry_run,
        verbose=verbose,
        file_limit=file_limit,
        allowed_extensions=allowed_extensions,
        fast_mode=fast_mode,
        show_ai_insights=show_ai_insights,
    )

    return config

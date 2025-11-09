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
) -> Config:
    """
    Load application configuration from environment and arguments.

    Args:
        config_path: Optional path to .env file
        ollama_model: Override Ollama model from command line
        dry_run: Enable dry-run mode
        verbose: Enable verbose logging

    Returns:
        Config: Application configuration object

    Example:
        >>> config = load_config(ollama_model="llama3.2:3b")
        >>> print(config.ollama_model)
        llama3.2:3b
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
    )

    return config

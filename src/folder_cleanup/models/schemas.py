"""Data schemas and models for folder-cleanup."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class FileType(str, Enum):
    """Supported file types for processing."""

    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    CODE = "code"
    DATA = "data"
    OTHER = "other"


class FileInfo(BaseModel):
    """Information about a file to be processed."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    path: Path = Field(..., description="Absolute path to the file")
    name: str = Field(..., description="Current filename")
    extension: str = Field(..., description="File extension including dot")
    size_bytes: int = Field(..., description="File size in bytes")
    modified_time: datetime = Field(..., description="Last modification time")
    file_type: FileType = Field(..., description="Categorized file type")
    mime_type: Optional[str] = Field(None, description="MIME type if detected")
    content_preview: Optional[str] = Field(None, description="Preview of file content")

    @property
    def size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.size_bytes / (1024 * 1024)

    def __str__(self) -> str:
        """String representation of file info."""
        return f"{self.name} ({self.size_mb:.2f} MB)"


class AnalysisResult(BaseModel):
    """Result of AI analysis for a file."""

    file_info: FileInfo = Field(..., description="Original file information")
    suggested_name: str = Field(..., description="AI-suggested filename")
    suggested_folder: str = Field(..., description="AI-suggested folder path")
    category: str = Field(..., description="Content category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reasoning: Optional[str] = Field(None, description="AI reasoning for suggestions")

    def __str__(self) -> str:
        """String representation of analysis result."""
        return f"{self.file_info.name} → {self.suggested_name} ({self.confidence:.0%})"


class RenameOperation(BaseModel):
    """A file rename operation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    original_path: Path = Field(..., description="Original file path")
    new_name: str = Field(..., description="New filename")
    reason: Optional[str] = Field(None, description="Reason for rename")

    @property
    def new_path(self) -> Path:
        """Get the new file path after rename."""
        return self.original_path.parent / self.new_name


class MoveOperation(BaseModel):
    """A file move operation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    original_path: Path = Field(..., description="Original file path")
    destination_folder: Path = Field(..., description="Destination folder path")
    reason: Optional[str] = Field(None, description="Reason for move")

    @property
    def destination_path(self) -> Path:
        """Get the full destination path."""
        return self.destination_folder / self.original_path.name


class OrganizationPlan(BaseModel):
    """Complete plan for organizing files."""

    rename_operations: list[RenameOperation] = Field(
        default_factory=list, description="List of rename operations"
    )
    move_operations: list[MoveOperation] = Field(
        default_factory=list, description="List of move operations"
    )
    folders_to_create: list[Path] = Field(
        default_factory=list, description="Folders that need to be created"
    )
    total_files: int = Field(0, description="Total number of files to process")
    estimated_time_seconds: float = Field(0.0, description="Estimated processing time")

    def __str__(self) -> str:
        """String representation of organization plan."""
        return (
            f"Plan: {len(self.rename_operations)} renames, "
            f"{len(self.move_operations)} moves, "
            f"{len(self.folders_to_create)} new folders"
        )


class Config(BaseModel):
    """Application configuration."""

    # Ollama settings
    ollama_host: str = Field(default="http://localhost:11434", description="Ollama host URL")
    ollama_model: str = Field(default="deepseek-r1:7b", description="Ollama model to use")
    ollama_timeout: int = Field(default=120, description="Ollama request timeout in seconds")

    # File processing settings
    max_file_size_mb: int = Field(default=10, description="Maximum file size to read in MB")
    max_content_length: int = Field(
        default=50000, description="Maximum content length to send to AI"
    )
    batch_size: int = Field(default=5, description="Number of files to process in parallel")

    # Filtering settings
    ignore_patterns: list[str] = Field(
        default_factory=lambda: [
            ".git",
            ".gitignore",
            "node_modules",
            "__pycache__",
            "*.pyc",
            ".DS_Store",
            "venv",
            ".env",
        ],
        description="Patterns to ignore during scanning",
    )
    allowed_extensions: Optional[list[str]] = Field(
        None, description="If set, only process these extensions"
    )
    file_limit: Optional[int] = Field(
        None, description="Maximum number of files to process (for testing)"
    )

    # Performance settings
    fast_mode: bool = Field(
        default=False, description="Skip Phase 1 pattern discovery for faster processing"
    )

    # Behavior settings
    dry_run: bool = Field(default=True, description="Run in dry-run mode by default")
    create_backups: bool = Field(default=False, description="Create backups before operations")
    verbose: bool = Field(default=False, description="Enable verbose logging")
    show_ai_insights: bool = Field(
        default=True, description="Display AI-discovered patterns and insights"
    )

    model_config = ConfigDict(env_file=".env", env_prefix="")

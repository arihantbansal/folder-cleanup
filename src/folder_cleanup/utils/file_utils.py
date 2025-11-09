"""File handling utilities."""

import mimetypes
from pathlib import Path
from typing import Optional

from ..models.schemas import FileType
from .logger import get_logger

logger = get_logger(__name__)


# File type mappings based on extensions and MIME types
FILE_TYPE_EXTENSIONS = {
    FileType.DOCUMENT: {
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".rtf",
        ".odt",
        ".pages",
        ".tex",
        ".md",
        ".markdown",
    },
    FileType.IMAGE: {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".svg",
        ".webp",
        ".tiff",
        ".ico",
        ".heic",
    },
    FileType.VIDEO: {
        ".mp4",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
        ".mkv",
        ".webm",
        ".m4v",
        ".mpg",
        ".mpeg",
    },
    FileType.AUDIO: {
        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".ogg",
        ".m4a",
        ".wma",
        ".opus",
    },
    FileType.ARCHIVE: {
        ".zip",
        ".tar",
        ".gz",
        ".bz2",
        ".7z",
        ".rar",
        ".xz",
        ".tar.gz",
        ".tgz",
    },
    FileType.CODE: {
        ".py",
        ".js",
        ".ts",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".hpp",
        ".rs",
        ".go",
        ".rb",
        ".php",
        ".swift",
        ".kt",
        ".scala",
        ".sh",
        ".bash",
        ".json",
        ".xml",
        ".yaml",
        ".yml",
        ".toml",
        ".css",
        ".scss",
        ".html",
        ".jsx",
        ".tsx",
        ".vue",
    },
    FileType.DATA: {
        ".csv",
        ".xlsx",
        ".xls",
        ".db",
        ".sqlite",
        ".sql",
        ".parquet",
        ".avro",
    },
}

# Text-based file extensions
TEXT_EXTENSIONS = (
    FILE_TYPE_EXTENSIONS[FileType.DOCUMENT]
    | FILE_TYPE_EXTENSIONS[FileType.CODE]
    | {".log", ".ini", ".cfg", ".conf", ".env"}
)


def get_file_type(path: Path, mime_type: Optional[str] = None) -> FileType:
    """
    Determine the type of a file based on extension and MIME type.

    Args:
        path: Path to the file
        mime_type: Optional MIME type (will be detected if not provided)

    Returns:
        FileType: Categorized file type

    Example:
        >>> get_file_type(Path("document.pdf"))
        <FileType.DOCUMENT: 'document'>
        >>> get_file_type(Path("photo.jpg"))
        <FileType.IMAGE: 'image'>
    """
    extension = "".join(path.suffixes).lower()

    # Check extension-based mapping
    for file_type, extensions in FILE_TYPE_EXTENSIONS.items():
        if extension in extensions:
            return file_type

    # Fall back to MIME type if available
    if not mime_type:
        mime_type, _ = mimetypes.guess_type(str(path))

    if mime_type:
        if mime_type.startswith("text/"):
            return FileType.DOCUMENT
        elif mime_type.startswith("image/"):
            return FileType.IMAGE
        elif mime_type.startswith("video/"):
            return FileType.VIDEO
        elif mime_type.startswith("audio/"):
            return FileType.AUDIO

    return FileType.OTHER


def is_text_file(path: Path, max_check_bytes: int = 8192) -> bool:
    """
    Check if a file is likely a text file.

    Args:
        path: Path to the file
        max_check_bytes: Number of bytes to check for binary content

    Returns:
        bool: True if file appears to be text

    Example:
        >>> is_text_file(Path("script.py"))
        True
        >>> is_text_file(Path("image.jpg"))
        False
    """
    # Check extension first
    extension = "".join(path.suffixes).lower()
    if extension in TEXT_EXTENSIONS:
        return True

    # Check MIME type
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type and mime_type.startswith("text/"):
        return True

    # Check file content for binary data
    try:
        with path.open("rb") as f:
            chunk = f.read(max_check_bytes)
            # If there are null bytes, it's likely binary
            if b"\x00" in chunk:
                return False
            # Try to decode as UTF-8
            try:
                chunk.decode("utf-8")
                return True
            except UnicodeDecodeError:
                return False
    except Exception as e:
        logger.warning(f"Could not check if {path} is text file: {e}")
        return False


def safe_read_file(path: Path, max_size_mb: int = 10, max_length: int = 50000) -> Optional[str]:
    """
    Safely read text content from a file with size limits.

    Args:
        path: Path to the file
        max_size_mb: Maximum file size in megabytes
        max_length: Maximum content length to return

    Returns:
        Optional[str]: File content or None if file is too large/binary/unreadable

    Example:
        >>> content = safe_read_file(Path("README.md"))
        >>> if content:
        ...     print(content[:100])
    """
    try:
        # Check file size
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            logger.debug(f"File {path} is too large ({size_mb:.2f} MB)")
            return None

        # Check if it's a text file
        if not is_text_file(path):
            logger.debug(f"File {path} is not a text file")
            return None

        # Read content
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            content = f.read(max_length)

        return content

    except Exception as e:
        logger.warning(f"Could not read file {path}: {e}")
        return None

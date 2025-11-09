"""Tests for file utilities."""

from pathlib import Path
import pytest

from folder_cleanup.utils.file_utils import get_file_type, is_text_file
from folder_cleanup.models.schemas import FileType


def test_get_file_type_document():
    """Test document file type detection."""
    assert get_file_type(Path("document.pdf")) == FileType.DOCUMENT
    assert get_file_type(Path("notes.txt")) == FileType.DOCUMENT
    assert get_file_type(Path("report.docx")) == FileType.DOCUMENT


def test_get_file_type_image():
    """Test image file type detection."""
    assert get_file_type(Path("photo.jpg")) == FileType.IMAGE
    assert get_file_type(Path("image.png")) == FileType.IMAGE
    assert get_file_type(Path("graphic.svg")) == FileType.IMAGE


def test_get_file_type_code():
    """Test code file type detection."""
    assert get_file_type(Path("script.py")) == FileType.CODE
    assert get_file_type(Path("app.js")) == FileType.CODE
    assert get_file_type(Path("config.json")) == FileType.CODE


def test_get_file_type_archive():
    """Test archive file type detection."""
    assert get_file_type(Path("archive.zip")) == FileType.ARCHIVE
    assert get_file_type(Path("backup.tar.gz")) == FileType.ARCHIVE
    assert get_file_type(Path("compressed.7z")) == FileType.ARCHIVE


def test_get_file_type_other():
    """Test unknown file type detection."""
    assert get_file_type(Path("unknown.xyz")) == FileType.OTHER
    assert get_file_type(Path("noextension")) == FileType.OTHER


def test_is_text_file():
    """Test text file detection."""
    # Extension-based detection
    assert is_text_file(Path("script.py"))
    assert is_text_file(Path("document.txt"))
    assert is_text_file(Path("config.json"))

    # Binary files should return False
    assert not is_text_file(Path("image.jpg"))
    assert not is_text_file(Path("video.mp4"))

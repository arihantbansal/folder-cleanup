"""Tests for data models."""

from pathlib import Path
from datetime import datetime

from folder_cleanup.models.schemas import (
    FileInfo,
    FileType,
    AnalysisResult,
    RenameOperation,
    MoveOperation,
)


def test_file_info_creation():
    """Test FileInfo model creation."""
    file_info = FileInfo(
        path=Path("/tmp/test.txt"),
        name="test.txt",
        extension=".txt",
        size_bytes=1024,
        modified_time=datetime.now(),
        file_type=FileType.DOCUMENT,
    )

    assert file_info.name == "test.txt"
    assert file_info.size_mb == 1024 / (1024 * 1024)
    assert file_info.file_type == FileType.DOCUMENT


def test_analysis_result_creation():
    """Test AnalysisResult model creation."""
    file_info = FileInfo(
        path=Path("/tmp/photo.jpg"),
        name="IMG_001.jpg",
        extension=".jpg",
        size_bytes=2048,
        modified_time=datetime.now(),
        file_type=FileType.IMAGE,
    )

    result = AnalysisResult(
        file_info=file_info,
        suggested_name="vacation_paris.jpg",
        suggested_folder="Photos/Travel",
        category="travel",
        confidence=0.9,
    )

    assert result.suggested_name == "vacation_paris.jpg"
    assert result.category == "travel"
    assert result.confidence == 0.9


def test_rename_operation():
    """Test RenameOperation model."""
    op = RenameOperation(
        original_path=Path("/tmp/old.txt"),
        new_name="new.txt",
    )

    assert op.new_path == Path("/tmp/new.txt")


def test_move_operation():
    """Test MoveOperation model."""
    op = MoveOperation(
        original_path=Path("/tmp/file.txt"),
        destination_folder=Path("/tmp/Documents"),
    )

    assert op.destination_path == Path("/tmp/Documents/file.txt")

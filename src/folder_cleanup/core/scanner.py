"""File scanning and discovery module."""

from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

from pathspec import PathSpec
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from ..models.schemas import FileInfo, Config
from ..utils.file_utils import get_file_type, safe_read_file
from ..utils.logger import get_logger, console

logger = get_logger(__name__)


class FileScanner:
    """
    Scans directories and collects file information.

    This class recursively scans directories, respects ignore patterns,
    and collects metadata about files for processing.

    Attributes:
        config: Application configuration
        ignore_spec: PathSpec for ignore patterns
    """

    def __init__(self, config: Config):
        """
        Initialize the file scanner.

        Args:
            config: Application configuration containing ignore patterns
                   and file processing settings
        """
        self.config = config
        self.ignore_spec = PathSpec.from_lines("gitwildmatch", config.ignore_patterns)
        logger.debug(f"Scanner initialized with {len(config.ignore_patterns)} ignore patterns")

    def should_ignore(self, path: Path, base_path: Path) -> bool:
        """
        Check if a path should be ignored based on ignore patterns.

        Args:
            path: Path to check
            base_path: Base directory for relative path calculation

        Returns:
            bool: True if path should be ignored

        Example:
            >>> scanner = FileScanner(config)
            >>> scanner.should_ignore(Path(".git/config"), Path("/home"))
            True
        """
        try:
            relative = path.relative_to(base_path)
            # Check against ignore patterns
            if self.ignore_spec.match_file(str(relative)):
                return True

            # Ignore hidden files/directories (starting with .)
            if any(part.startswith(".") for part in path.parts):
                return True

            return False

        except ValueError:
            # Path is not relative to base_path
            return True

    def scan_file(self, path: Path) -> Optional[FileInfo]:
        """
        Scan a single file and extract its information.

        Args:
            path: Path to the file to scan

        Returns:
            Optional[FileInfo]: File information or None if file cannot be read

        Example:
            >>> scanner = FileScanner(config)
            >>> file_info = scanner.scan_file(Path("document.pdf"))
            >>> print(file_info.name)
            document.pdf
        """
        try:
            # Get file stats
            stat = path.stat()

            # Skip if file is too large for content reading
            size_mb = stat.st_size / (1024 * 1024)
            content_preview = None

            if size_mb <= self.config.max_file_size_mb:
                content_preview = safe_read_file(
                    path,
                    max_size_mb=self.config.max_file_size_mb,
                    max_length=self.config.max_content_length,
                )

            # Create FileInfo object
            file_info = FileInfo(
                path=path.absolute(),
                name=path.name,
                extension="".join(path.suffixes).lower(),
                size_bytes=stat.st_size,
                modified_time=datetime.fromtimestamp(stat.st_mtime),
                file_type=get_file_type(path),
                content_preview=content_preview,
            )

            logger.debug(f"Scanned: {file_info}")
            return file_info

        except Exception as e:
            logger.warning(f"Failed to scan {path}: {e}")
            return None

    def scan_directory(
        self, directory: Path, recursive: bool = True, show_progress: bool = True
    ) -> list[FileInfo]:
        """
        Scan a directory and collect information about all files.

        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories recursively
            show_progress: Whether to display progress bar

        Returns:
            list[FileInfo]: List of file information objects

        Raises:
            FileNotFoundError: If directory does not exist
            PermissionError: If directory is not accessible

        Example:
            >>> scanner = FileScanner(config)
            >>> files = scanner.scan_directory(Path("~/Downloads"))
            >>> print(f"Found {len(files)} files")
        """
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")

        logger.info(f"Scanning directory: {directory}")

        files: list[FileInfo] = []
        pattern = "**/*" if recursive else "*"

        try:
            # Count total files first for progress bar
            all_paths = list(directory.glob(pattern))
            total_files = sum(
                1
                for p in all_paths
                if p.is_file() and not self.should_ignore(p, directory)
            )

            logger.info(f"Found {total_files} files to process")

            if show_progress and total_files > 0:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    console=console,
                ) as progress:
                    task = progress.add_task("[cyan]Scanning files...", total=total_files)

                    for path in all_paths:
                        if not path.is_file():
                            continue

                        if self.should_ignore(path, directory):
                            continue

                        # Apply extension filter if configured
                        if self.config.allowed_extensions:
                            ext = "".join(path.suffixes).lower()
                            if ext not in self.config.allowed_extensions:
                                progress.advance(task)
                                continue

                        file_info = self.scan_file(path)
                        if file_info:
                            files.append(file_info)

                        progress.advance(task)
            else:
                # Scan without progress bar
                for path in all_paths:
                    if not path.is_file():
                        continue

                    if self.should_ignore(path, directory):
                        continue

                    if self.config.allowed_extensions:
                        ext = "".join(path.suffixes).lower()
                        if ext not in self.config.allowed_extensions:
                            continue

                    file_info = self.scan_file(path)
                    if file_info:
                        files.append(file_info)

        except PermissionError as e:
            logger.error(f"Permission denied accessing {directory}: {e}")
            raise

        logger.info(f"Scanned {len(files)} files successfully")
        return files

    def filter_files(
        self, files: list[FileInfo], min_size_mb: float = 0, max_size_mb: Optional[float] = None
    ) -> list[FileInfo]:
        """
        Filter files based on size criteria.

        Args:
            files: List of files to filter
            min_size_mb: Minimum file size in MB
            max_size_mb: Maximum file size in MB (None for no limit)

        Returns:
            list[FileInfo]: Filtered list of files

        Example:
            >>> scanner = FileScanner(config)
            >>> large_files = scanner.filter_files(all_files, min_size_mb=1.0)
        """
        filtered = []

        for file_info in files:
            size_mb = file_info.size_mb

            if size_mb < min_size_mb:
                continue

            if max_size_mb is not None and size_mb > max_size_mb:
                continue

            filtered.append(file_info)

        logger.info(f"Filtered {len(files)} → {len(filtered)} files")
        return filtered

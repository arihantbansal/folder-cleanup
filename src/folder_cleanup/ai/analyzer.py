"""File analysis using AI."""

from typing import Optional

from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)

from ..models.schemas import FileInfo, AnalysisResult, Config
from ..utils.logger import get_logger, console
from .ollama_client import OllamaClient, OllamaClientError
from .prompts import build_combined_prompt

logger = get_logger(__name__)


class FileAnalyzer:
    """
    Analyzes files using AI to suggest better names and organization.

    This class uses an Ollama client to send file information to an LLM
    and receive suggestions for renaming and organizing files.

    Attributes:
        config: Application configuration
        client: Ollama client instance
    """

    def __init__(self, config: Config):
        """
        Initialize the file analyzer.

        Args:
            config: Application configuration

        Raises:
            OllamaClientError: If Ollama client cannot be initialized
        """
        self.config = config
        self.client = OllamaClient(config)

        logger.debug("FileAnalyzer initialized")

    def analyze_file(self, file_info: FileInfo) -> Optional[AnalysisResult]:
        """
        Analyze a single file and get AI suggestions.

        Args:
            file_info: Information about the file to analyze

        Returns:
            Optional[AnalysisResult]: Analysis result or None if analysis failed

        Example:
            >>> analyzer = FileAnalyzer(config)
            >>> result = analyzer.analyze_file(file_info)
            >>> print(result.suggested_name)
            vacation_paris_2024.jpg
        """
        try:
            logger.debug(f"Analyzing: {file_info.name}")

            # Build prompt
            prompt = build_combined_prompt(
                filename=file_info.name,
                extension=file_info.extension,
                file_type=file_info.file_type.value,
                size_mb=file_info.size_mb,
                modified_time=file_info.modified_time.isoformat(),
                content=file_info.content_preview,
            )

            # Get AI response
            response = self.client.generate_json(prompt, temperature=0.3)

            if not response:
                logger.warning(f"No response for {file_info.name}")
                return None

            # Extract fields with defaults
            suggested_name = response.get("suggested_name", file_info.name)
            folder_path = response.get("folder_path", "Uncategorized")
            category = response.get("category", "other")
            confidence = float(response.get("confidence", 0.5))
            reasoning = response.get("reasoning", "")

            # Ensure extension is preserved
            if not suggested_name.endswith(file_info.extension):
                suggested_name = suggested_name.rsplit(".", 1)[0] + file_info.extension

            # Create analysis result
            result = AnalysisResult(
                file_info=file_info,
                suggested_name=suggested_name,
                suggested_folder=folder_path,
                category=category,
                confidence=confidence,
                reasoning=reasoning,
            )

            logger.debug(f"Analysis complete: {result}")
            return result

        except Exception as e:
            logger.error(f"Failed to analyze {file_info.name}: {e}")
            return None

    def analyze_batch(
        self, files: list[FileInfo], show_progress: bool = True
    ) -> list[AnalysisResult]:
        """
        Analyze multiple files in batch.

        Args:
            files: List of files to analyze
            show_progress: Whether to show progress bar

        Returns:
            list[AnalysisResult]: List of successful analysis results

        Example:
            >>> analyzer = FileAnalyzer(config)
            >>> results = analyzer.analyze_batch(files)
            >>> print(f"Analyzed {len(results)} files")
        """
        results: list[AnalysisResult] = []

        if not files:
            logger.warning("No files to analyze")
            return results

        logger.info(f"Analyzing {len(files)} files...")

        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "[cyan]Analyzing files with AI...", total=len(files)
                )

                for file_info in files:
                    result = self.analyze_file(file_info)
                    if result:
                        results.append(result)
                    progress.advance(task)
        else:
            for file_info in files:
                result = self.analyze_file(file_info)
                if result:
                    results.append(result)

        logger.info(f"Successfully analyzed {len(results)}/{len(files)} files")
        return results

    def check_model_available(self) -> bool:
        """
        Check if the configured AI model is available.

        Returns:
            bool: True if model is ready to use

        Example:
            >>> analyzer = FileAnalyzer(config)
            >>> if not analyzer.check_model_available():
            ...     print("Please pull the model first")
        """
        return self.client.check_health()

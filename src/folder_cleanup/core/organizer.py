"""File organization and operations module."""

import shutil
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..models.schemas import (
    AnalysisResult,
    OrganizationPlan,
    RenameOperation,
    MoveOperation,
    Config,
)
from ..utils.logger import get_logger, console

logger = get_logger(__name__)


class FileOrganizer:
    """
    Handles file organization operations.

    This class creates organization plans from analysis results and
    executes file operations (rename, move) safely with dry-run support.

    Attributes:
        config: Application configuration
        base_directory: Base directory for organizing files
    """

    def __init__(self, config: Config, base_directory: Path):
        """
        Initialize the file organizer.

        Args:
            config: Application configuration
            base_directory: Base directory where files will be organized
        """
        self.config = config
        self.base_directory = base_directory.absolute()

        logger.debug(f"FileOrganizer initialized with base: {self.base_directory}")

    def create_plan(self, analysis_results: list[AnalysisResult]) -> OrganizationPlan:
        """
        Create an organization plan from analysis results.

        Args:
            analysis_results: List of AI analysis results

        Returns:
            OrganizationPlan: Complete organization plan

        Example:
            >>> organizer = FileOrganizer(config, Path("/path"))
            >>> plan = organizer.create_plan(results)
            >>> print(plan)
        """
        rename_operations: list[RenameOperation] = []
        move_operations: list[MoveOperation] = []
        folders_to_create: set[Path] = set()

        for result in analysis_results:
            file_path = result.file_info.path

            # Create rename operation if name changed
            if result.suggested_name != result.file_info.name:
                rename_op = RenameOperation(
                    original_path=file_path,
                    new_name=result.suggested_name,
                    reason=result.reasoning,
                )
                rename_operations.append(rename_op)
                # Update path for move operation
                file_path = rename_op.new_path

            # Create move operation if folder changed
            destination_folder = self.base_directory / result.suggested_folder

            # Only move if it's a different directory
            if destination_folder != file_path.parent:
                move_op = MoveOperation(
                    original_path=file_path,
                    destination_folder=destination_folder,
                    reason=result.reasoning,
                )
                move_operations.append(move_op)
                folders_to_create.add(destination_folder)

        # Create organization plan
        plan = OrganizationPlan(
            rename_operations=rename_operations,
            move_operations=move_operations,
            folders_to_create=sorted(folders_to_create),
            total_files=len(analysis_results),
            estimated_time_seconds=len(analysis_results) * 0.1,  # Rough estimate
        )

        logger.info(f"Created plan: {plan}")
        return plan

    def preview_plan(self, plan: OrganizationPlan, max_display: int = 20) -> None:
        """
        Display a preview of the organization plan.

        Args:
            plan: Organization plan to preview
            max_display: Maximum number of operations to display

        Example:
            >>> organizer = FileOrganizer(config, Path("/path"))
            >>> organizer.preview_plan(plan)
        """
        console.print("\n[bold cyan]Organization Plan Preview[/bold cyan]\n")

        # Summary
        console.print(
            Panel(
                f"[yellow]Total files:[/yellow] {plan.total_files}\n"
                f"[yellow]Renames:[/yellow] {len(plan.rename_operations)}\n"
                f"[yellow]Moves:[/yellow] {len(plan.move_operations)}\n"
                f"[yellow]New folders:[/yellow] {len(plan.folders_to_create)}",
                title="Summary",
                border_style="cyan",
            )
        )

        # Rename operations
        if plan.rename_operations:
            console.print("\n[bold]Rename Operations:[/bold]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Current Name", style="dim")
            table.add_column("→", justify="center")
            table.add_column("New Name", style="green")

            for i, op in enumerate(plan.rename_operations[:max_display]):
                table.add_row(op.original_path.name, "→", op.new_name)

            console.print(table)

            if len(plan.rename_operations) > max_display:
                console.print(
                    f"[dim]... and {len(plan.rename_operations) - max_display} more[/dim]"
                )

        # Move operations
        if plan.move_operations:
            console.print("\n[bold]Move Operations:[/bold]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("File", style="dim")
            table.add_column("→", justify="center")
            table.add_column("Destination", style="blue")

            for i, op in enumerate(plan.move_operations[:max_display]):
                rel_dest = op.destination_folder.relative_to(self.base_directory)
                table.add_row(op.original_path.name, "→", str(rel_dest))

            console.print(table)

            if len(plan.move_operations) > max_display:
                console.print(
                    f"[dim]... and {len(plan.move_operations) - max_display} more[/dim]"
                )

        # New folders
        if plan.folders_to_create:
            console.print("\n[bold]Folders to Create:[/bold]")
            for folder in plan.folders_to_create[:max_display]:
                rel_folder = folder.relative_to(self.base_directory)
                console.print(f"  📁 {rel_folder}")

            if len(plan.folders_to_create) > max_display:
                console.print(
                    f"[dim]... and {len(plan.folders_to_create) - max_display} more[/dim]"
                )

        console.print()

    def execute_plan(self, plan: OrganizationPlan, dry_run: bool = True) -> dict[str, int]:
        """
        Execute the organization plan.

        Args:
            plan: Organization plan to execute
            dry_run: If True, only simulate operations without making changes

        Returns:
            dict[str, int]: Statistics about executed operations

        Example:
            >>> organizer = FileOrganizer(config, Path("/path"))
            >>> stats = organizer.execute_plan(plan, dry_run=False)
            >>> print(f"Renamed {stats['renamed']} files")
        """
        stats = {"renamed": 0, "moved": 0, "folders_created": 0, "errors": 0}

        if dry_run:
            logger.info("[DRY RUN] No actual changes will be made")
            console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")

        # Create folders
        for folder in plan.folders_to_create:
            try:
                if not dry_run:
                    folder.mkdir(parents=True, exist_ok=True)
                    logger.debug(f"Created folder: {folder}")

                stats["folders_created"] += 1

            except Exception as e:
                logger.error(f"Failed to create folder {folder}: {e}")
                stats["errors"] += 1

        # Execute renames
        for op in plan.rename_operations:
            try:
                if op.original_path.exists():
                    if not dry_run:
                        op.original_path.rename(op.new_path)
                        logger.debug(f"Renamed: {op.original_path.name} → {op.new_name}")

                    stats["renamed"] += 1
                else:
                    logger.warning(f"File not found for rename: {op.original_path}")

            except Exception as e:
                logger.error(f"Failed to rename {op.original_path}: {e}")
                stats["errors"] += 1

        # Execute moves
        for op in plan.move_operations:
            try:
                if op.original_path.exists():
                    destination = op.destination_path

                    # Handle name conflicts
                    if destination.exists() and destination != op.original_path:
                        logger.warning(f"Destination exists: {destination}")
                        # Add counter to filename
                        base = destination.stem
                        ext = destination.suffix
                        counter = 1
                        while destination.exists():
                            destination = op.destination_folder / f"{base}_{counter}{ext}"
                            counter += 1

                    if not dry_run:
                        shutil.move(str(op.original_path), str(destination))
                        logger.debug(f"Moved: {op.original_path.name} → {destination}")

                    stats["moved"] += 1
                else:
                    logger.warning(f"File not found for move: {op.original_path}")

            except Exception as e:
                logger.error(f"Failed to move {op.original_path}: {e}")
                stats["errors"] += 1

        # Print summary
        mode = "[yellow](DRY RUN)[/yellow]" if dry_run else ""
        console.print(
            Panel(
                f"[green]✓ Folders created:[/green] {stats['folders_created']}\n"
                f"[green]✓ Files renamed:[/green] {stats['renamed']}\n"
                f"[green]✓ Files moved:[/green] {stats['moved']}\n"
                f"[red]✗ Errors:[/red] {stats['errors']}",
                title=f"Execution Summary {mode}",
                border_style="green" if stats["errors"] == 0 else "red",
            )
        )

        return stats

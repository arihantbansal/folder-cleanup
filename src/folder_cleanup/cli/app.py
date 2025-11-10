"""Main CLI application."""

import sys
from pathlib import Path
from typing import Optional
import time

import typer
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from typing_extensions import Annotated

from .. import __version__
from ..models.schemas import Config
from ..core.scanner import FileScanner
from ..core.organizer import FileOrganizer
from ..ai.analyzer import FileAnalyzer
from ..ai.ollama_client import OllamaClientError
from ..utils.config import load_config
from ..utils.logger import setup_logger, get_logger, console
from ..utils.errors import (
    show_ollama_connection_error,
    show_ollama_model_error,
    show_permission_error,
    show_ai_insights,
    show_processing_estimate,
)

# Create Typer app
app = typer.Typer(
    name="folder-cleanup",
    help="AI-powered file organizer using local LLMs",
    add_completion=False,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"folder-cleanup version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    """
    Folder Cleanup - AI-powered file organizer.

    Intelligently rename and organize files using local LLMs via Ollama.
    """
    pass


@app.command()
def scan(
    directory: Annotated[
        Path,
        typer.Argument(
            help="Directory to scan",
            exists=True,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
        ),
    ],
    recursive: Annotated[bool, typer.Option("--recursive", "-r", help="Scan recursively")] = True,
    verbose: Annotated[bool, typer.Option("--verbose", help="Enable verbose logging")] = False,
) -> None:
    """
    Scan a directory and show file information.

    This command scans the specified directory and displays information
    about the files found, without making any changes.

    Example:
        folder-cleanup scan ~/Downloads
        folder-cleanup scan ~/Documents --recursive
    """
    # Setup logging
    logger = setup_logger(verbose=verbose)

    try:
        console.print(
            Panel.fit(
                f"[cyan]Scanning:[/cyan] {directory}\n"
                f"[cyan]Recursive:[/cyan] {recursive}",
                title="📁 Folder Cleanup - Scan",
                border_style="cyan",
            )
        )

        # Load configuration
        config = load_config(verbose=verbose)

        # Create scanner
        scanner = FileScanner(config)

        # Scan directory
        files = scanner.scan_directory(directory, recursive=recursive)

        # Display results
        console.print(f"\n[green]✓ Found {len(files)} files[/green]")

        # Show file type breakdown
        type_counts: dict[str, int] = {}
        for file_info in files:
            file_type = file_info.file_type.value
            type_counts[file_type] = type_counts.get(file_type, 0) + 1

        console.print("\n[bold]File Types:[/bold]")
        for file_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            console.print(f"  {file_type}: {count}")

        console.print()

    except Exception as e:
        logger.error(f"Scan failed: {e}")
        raise typer.Exit(code=1)


@app.command()
def organize(
    directory: Annotated[
        Path,
        typer.Argument(
            help="Directory to organize",
            exists=True,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
        ),
    ],
    model: Annotated[
        Optional[str],
        typer.Option("--model", "-m", help="Ollama model to use (e.g., deepseek-r1:7b)"),
    ] = None,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", "-d", help="Preview changes without executing")
    ] = True,
    execute: Annotated[
        bool, typer.Option("--execute", "-e", help="Execute changes (disables dry-run)")
    ] = False,
    limit: Annotated[
        Optional[int],
        typer.Option("--limit", "-l", help="Limit number of files to process (for testing)"),
    ] = None,
    extensions: Annotated[
        Optional[str],
        typer.Option("--extensions", "-x", help="Filter by extensions (e.g., .pdf,.jpg,.png)"),
    ] = None,
    fast: Annotated[
        bool, typer.Option("--fast", "-f", help="Fast mode: skip pattern discovery")
    ] = False,
    recursive: Annotated[bool, typer.Option("--recursive", "-r", help="Scan recursively")] = True,
    verbose: Annotated[bool, typer.Option("--verbose", help="Enable verbose logging")] = False,
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Auto-confirm, skip prompts")
    ] = False,
) -> None:
    """
    Organize files using AI with intelligent multi-phase analysis.

    This command scans files, analyzes them with AI, and organizes them
    by renaming and moving into appropriate folders.

    By default, runs in DRY-RUN mode (preview only).
    Use --execute to apply changes.

    Examples:
        # Preview organization (safe)
        folder-cleanup organize ~/Downloads

        # Actually organize files (requires confirmation)
        folder-cleanup organize ~/Downloads --execute

        # Test on 10 files first
        folder-cleanup organize ~/Downloads --limit 10

        # Only organize PDFs and images
        folder-cleanup organize ~/Downloads --extensions .pdf,.jpg,.png

        # Fast mode (skip pattern discovery for speed)
        folder-cleanup organize ~/Downloads --fast --execute

        # Use different model
        folder-cleanup organize ~/Documents --model llama3.2:3b
    """
    # Setup logging
    logger = setup_logger(verbose=verbose)

    # Determine if we should execute
    should_execute = execute and not dry_run

    # Parse extensions if provided
    ext_list = None
    if extensions:
        ext_list = [ext.strip() if ext.startswith('.') else f'.{ext.strip()}'
                    for ext in extensions.split(',')]

    try:
        # Display header
        mode_text = "[yellow]DRY RUN[/yellow]" if not should_execute else "[green]EXECUTE[/green]"
        info_lines = [
            f"[cyan]Directory:[/cyan] {directory}",
            f"[cyan]Model:[/cyan] {model or 'default'}",
            f"[cyan]Mode:[/cyan] {mode_text}",
        ]

        if limit:
            info_lines.append(f"[cyan]Limit:[/cyan] {limit} files")
        if ext_list:
            info_lines.append(f"[cyan]Extensions:[/cyan] {', '.join(ext_list)}")
        if fast:
            info_lines.append(f"[cyan]Fast Mode:[/cyan] Enabled (skip pattern discovery)")

        console.print(
            Panel.fit(
                "\n".join(info_lines),
                title="🤖 Folder Cleanup - Intelligent Organizer",
                border_style="cyan",
            )
        )

        # Load configuration with all options
        config = load_config(
            ollama_model=model,
            dry_run=not should_execute,
            verbose=verbose,
            file_limit=limit,
            allowed_extensions=ext_list,
            fast_mode=fast,
        )

        # Step 1: Scan files
        console.print("\n[bold]Step 1/4: Scanning files...[/bold]")

        try:
            scanner = FileScanner(config)
            files = scanner.scan_directory(directory, recursive=recursive)
        except PermissionError:
            show_permission_error(str(directory))
            raise typer.Exit(code=1)
        except Exception as e:
            console.print(f"[red]✗ Scan failed: {e}[/red]")
            raise typer.Exit(code=1)

        if not files:
            console.print("[yellow]No files found to organize[/yellow]")
            if ext_list:
                console.print(f"[dim]Filter was: {', '.join(ext_list)}[/dim]")
            raise typer.Exit(code=0)

        console.print(f"[green]✓ Found {len(files)} files[/green]")

        # Show processing estimate
        show_processing_estimate(len(files), fast)

        # Confirmation prompt for execute mode
        if should_execute and not yes:
            if not typer.confirm(f"\n⚠️  Proceed to analyze and organize {len(files)} files?"):
                console.print("[yellow]Operation cancelled[/yellow]")
                raise typer.Exit(code=0)

        # Step 2: Analyze with AI (Multi-Phase Intelligent Analysis)
        console.print("\n[bold]Step 2/4: AI Analysis (Multi-Phase Strategy)...[/bold]")

        try:
            analyzer = FileAnalyzer(config)

            # Check if model is available
            if not analyzer.check_model_available():
                show_ollama_model_error(config.ollama_model)
                raise typer.Exit(code=1)

            # Use INTELLIGENT multi-phase analysis
            start_time = time.time()
            results = analyzer.analyze_batch_intelligent(files)
            analysis_time = time.time() - start_time

            if not results:
                console.print("[red]✗ AI analysis failed[/red]")
                console.print("[yellow]Check logs above for details[/yellow]")
                raise typer.Exit(code=1)

            console.print(f"\n[green]✓ Analyzed {len(results)} files with context[/green]")
            console.print(f"[dim]   Analysis time: {analysis_time:.1f}s[/dim]")

            # Show AI insights if pattern discovery was run
            if config.show_ai_insights and analyzer.discovered_patterns:
                show_ai_insights(analyzer.discovered_patterns)

        except OllamaClientError as e:
            show_ollama_connection_error(config.ollama_host, config.ollama_model)
            raise typer.Exit(code=1)

        # Step 3: Create organization plan
        console.print("\n[bold]Step 3/4: Creating organization plan...[/bold]")
        organizer = FileOrganizer(config, directory)
        plan = organizer.create_plan(results)
        console.print(f"[green]✓ Plan created[/green]")

        # Step 4: Preview and execute
        console.print("\n[bold]Step 4/4: Preview & Execute[/bold]")
        organizer.preview_plan(plan)

        if should_execute:
            # Final confirmation (only if not already confirmed)
            if not yes:
                if not typer.confirm("\n⚠️  Execute these changes?", default=False):
                    console.print("[yellow]Operation cancelled[/yellow]")
                    raise typer.Exit(code=0)

            console.print("\n[bold green]Executing changes...[/bold green]")
            start_time = time.time()
            stats = organizer.execute_plan(plan, dry_run=False)
            exec_time = time.time() - start_time

            if stats["errors"] > 0:
                console.print(
                    f"\n[yellow]⚠️  Completed with {stats['errors']} errors (took {exec_time:.1f}s)[/yellow]"
                )
                raise typer.Exit(code=1)
            else:
                console.print(f"\n[green]✨ Success! (took {exec_time:.1f}s)[/green]")

        else:
            console.print(
                "\n[yellow]💡 This was a dry run. Use --execute to apply changes.[/yellow]"
            )
            stats = organizer.execute_plan(plan, dry_run=True)

        console.print()

    except typer.Exit:
        raise
    except Exception as e:
        logger.error(f"Organization failed: {e}", exc_info=verbose)
        console.print(f"\n[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def check(
    model: Annotated[
        Optional[str],
        typer.Option("--model", "-m", help="Ollama model to check"),
    ] = None,
) -> None:
    """
    Check Ollama connection and model availability.

    This command verifies that Ollama is running and the specified
    model is available.

    Example:
        folder-cleanup check
        folder-cleanup check --model llama3.2:3b
    """
    logger = setup_logger()

    try:
        console.print(
            Panel.fit(
                "[cyan]Checking Ollama connection...[/cyan]",
                title="🔍 Health Check",
                border_style="cyan",
            )
        )

        config = load_config(ollama_model=model)

        analyzer = FileAnalyzer(config)

        if analyzer.check_model_available():
            console.print(f"\n[green]✓ Ollama is running[/green]")
            console.print(f"[green]✓ Model '{config.ollama_model}' is available[/green]")
            console.print(f"[green]✓ Ready to organize files![/green]\n")
        else:
            console.print(f"\n[yellow]⚠️  Ollama is running but model not found[/yellow]")
            console.print(f"\n[yellow]Pull the model with:[/yellow]")
            console.print(f"  ollama pull {config.ollama_model}\n")
            raise typer.Exit(code=1)

    except OllamaClientError as e:
        console.print(f"\n[red]✗ Cannot connect to Ollama: {e}[/red]")
        console.print("\n[yellow]Troubleshooting:[/yellow]")
        console.print("  1. Install Ollama: https://ollama.ai")
        console.print("  2. Start Ollama service")
        console.print(f"  3. Pull a model: ollama pull {config.ollama_model}\n")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()

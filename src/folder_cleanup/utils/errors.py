"""Enhanced error handling utilities."""

from typing import Optional
from rich.panel import Panel
from rich.console import Console

console = Console()


class OllamaConnectionError(Exception):
    """Raised when cannot connect to Ollama."""

    pass


class OllamaModelNotFoundError(Exception):
    """Raised when Ollama model is not available."""

    pass


def show_ollama_connection_error(host: str, model: str) -> None:
    """
    Display helpful error message for Ollama connection issues.

    Args:
        host: Ollama host URL
        model: Model name that was requested
    """
    console.print("\n[bold red]✗ Cannot Connect to Ollama[/bold red]\n")

    console.print("[yellow]Troubleshooting Steps:[/yellow]\n")

    console.print("[bold]1. Check if Ollama is running:[/bold]")
    console.print(f"   → curl {host}/api/tags")
    console.print("   → If this fails, Ollama is not running\n")

    console.print("[bold]2. Start Ollama:[/bold]")
    console.print("   → macOS/Windows: Open the Ollama app")
    console.print("   → Linux: ollama serve")
    console.print("   → Check: https://ollama.ai for installation\n")

    console.print("[bold]3. Verify host configuration:[/bold]")
    console.print(f"   → Current OLLAMA_HOST: {host}")
    console.print("   → Default should be: http://localhost:11434")
    console.print("   → Check your .env file or environment variables\n")

    console.print("[dim]Still having issues? Check the Ollama logs[/dim]")


def show_ollama_model_error(model: str, available_models: Optional[list[str]] = None) -> None:
    """
    Display helpful error message when model is not found.

    Args:
        model: Model that was not found
        available_models: List of available models (if known)
    """
    console.print(f"\n[bold red]✗ Model '{model}' Not Found[/bold red]\n")

    console.print("[yellow]To fix this:[/yellow]\n")

    console.print(f"[bold]Pull the model:[/bold]")
    console.print(f"   → ollama pull {model}\n")

    if available_models:
        console.print("[bold]Available models on your system:[/bold]")
        for m in available_models[:10]:  # Show first 10
            console.print(f"   • {m}")
        if len(available_models) > 10:
            console.print(f"   ... and {len(available_models) - 10} more")
    else:
        console.print("[bold]Check available models:[/bold]")
        console.print("   → ollama list")

    console.print("\n[bold]Recommended models:[/bold]")
    console.print("   • deepseek-r1:7b (best balance)")
    console.print("   • llama3.2:3b (faster, lighter)")
    console.print("   • qwen2.5:7b (excellent quality)")


def show_permission_error(path: str) -> None:
    """
    Display helpful error for permission issues.

    Args:
        path: Path that had permission denied
    """
    console.print(f"\n[bold red]✗ Permission Denied:[/bold red] {path}\n")

    console.print("[yellow]Possible solutions:[/yellow]\n")

    console.print("[bold]1. Check permissions:[/bold]")
    console.print(f"   → ls -la {path}")
    console.print(f"   → You need read/write access to this directory\n")

    console.print("[bold]2. Run with appropriate permissions:[/bold]")
    console.print("   → Make sure you own the directory")
    console.print("   → Or have been granted access by the owner\n")

    console.print("[bold]3. Try a different directory:[/bold]")
    console.print("   → Choose a directory you have full access to")


def show_ai_insights(patterns: dict) -> None:
    """
    Display AI-discovered patterns and insights.

    Args:
        patterns: Dictionary of patterns from Phase 1 discovery
    """
    if not patterns:
        return

    insights = patterns.get("insights", "")
    pattern_list = patterns.get("patterns", [])
    categories = patterns.get("suggested_categories", [])

    if not (insights or pattern_list):
        return

    console.print("\n[bold cyan]🔍 AI-Discovered Patterns:[/bold cyan]\n")

    if insights:
        console.print(Panel(insights, title="Overall Strategy", border_style="cyan"))

    if pattern_list:
        console.print("\n[bold]Identified Groups:[/bold]")
        for i, pattern in enumerate(pattern_list[:5], 1):  # Show top 5
            pattern_type = pattern.get("type", "unknown")
            description = pattern.get("description", "")
            file_count = len(pattern.get("file_indices", []))

            icon = {
                "temporal": "📅",
                "project": "💼",
                "topic": "📚",
                "semantic": "🔗",
            }.get(pattern_type, "📁")

            console.print(f"  {icon} {description} ({file_count} files)")

        if len(pattern_list) > 5:
            console.print(f"  [dim]... and {len(pattern_list) - 5} more patterns[/dim]")

    if categories:
        console.print(f"\n[bold]Suggested Categories:[/bold] {', '.join(categories[:8])}")

    console.print()


def estimate_processing_time(file_count: int, fast_mode: bool = False) -> tuple[int, int]:
    """
    Estimate processing time based on file count.

    Args:
        file_count: Number of files to process
        fast_mode: Whether fast mode is enabled

    Returns:
        tuple[int, int]: (min_seconds, max_seconds)
    """
    if fast_mode:
        # No Phase 1, just Phase 2
        seconds_per_file = 2  # ~2s per file in Phase 2
        total_seconds = file_count * seconds_per_file
        return total_seconds, int(total_seconds * 1.3)
    else:
        # Phase 1 + Phase 2 + Phase 3
        phase1 = min(60, file_count * 0.5)  # Max 60s for Phase 1
        phase2 = file_count * 2  # ~2s per file
        phase3 = min(20, file_count * 0.1)  # Max 20s for Phase 3

        total = int(phase1 + phase2 + phase3)
        return total, int(total * 1.5)


def show_processing_estimate(file_count: int, fast_mode: bool = False) -> None:
    """
    Show processing time estimate.

    Args:
        file_count: Number of files
        fast_mode: Whether fast mode is enabled
    """
    min_sec, max_sec = estimate_processing_time(file_count, fast_mode)

    min_str = f"{min_sec // 60}m {min_sec % 60}s" if min_sec >= 60 else f"{min_sec}s"
    max_str = f"{max_sec // 60}m {max_sec % 60}s" if max_sec >= 60 else f"{max_sec}s"

    console.print(f"\n[dim]⏱  Estimated time: {min_str} - {max_str}[/dim]")

    if not fast_mode and file_count > 20:
        console.print(
            f"[dim]💡 Tip: Use --fast to skip pattern discovery and process faster[/dim]"
        )

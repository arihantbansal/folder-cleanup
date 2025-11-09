#!/usr/bin/env python3
"""
Basic usage example of folder-cleanup as a Python library.

This demonstrates how to use the core components programmatically
instead of using the CLI.
"""

from pathlib import Path
from folder_cleanup.models.schemas import Config
from folder_cleanup.core.scanner import FileScanner
from folder_cleanup.core.organizer import FileOrganizer
from folder_cleanup.ai.analyzer import FileAnalyzer


def main():
    """Run a basic file organization workflow."""

    # 1. Create configuration
    config = Config(
        ollama_model="deepseek-r1:7b",
        dry_run=True,  # Safe mode - preview only
        verbose=True,
    )

    print("🤖 Folder Cleanup - Programmatic Example\n")

    # 2. Define directory to organize
    target_directory = Path.home() / "Downloads"
    print(f"📁 Target: {target_directory}\n")

    # 3. Scan files
    print("📊 Step 1: Scanning files...")
    scanner = FileScanner(config)
    files = scanner.scan_directory(target_directory, recursive=True)
    print(f"   Found {len(files)} files\n")

    if not files:
        print("No files to organize!")
        return

    # 4. Analyze with AI
    print("🧠 Step 2: Analyzing with AI...")
    analyzer = FileAnalyzer(config)

    # Check if model is available
    if not analyzer.check_model_available():
        print("❌ Error: Ollama model not available")
        print(f"   Run: ollama pull {config.ollama_model}")
        return

    results = analyzer.analyze_batch(files)
    print(f"   Analyzed {len(results)} files\n")

    # 5. Create organization plan
    print("📋 Step 3: Creating organization plan...")
    organizer = FileOrganizer(config, target_directory)
    plan = organizer.create_plan(results)
    print(f"   {plan}\n")

    # 6. Preview plan
    print("👀 Step 4: Previewing changes...")
    organizer.preview_plan(plan, max_display=10)

    # 7. Execute (dry-run mode)
    print("\n⚡ Step 5: Executing (dry-run)...")
    stats = organizer.execute_plan(plan, dry_run=True)

    print("\n✨ Done!")
    print(f"   To actually apply changes, set config.dry_run=False")


if __name__ == "__main__":
    main()

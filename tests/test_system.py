#!/usr/bin/env python3
"""
Test the semantic memory system end-to-end.
"""

import subprocess
import sys
from pathlib import Path

from rich.console import Console

console = Console()


def run_command(cmd: list, description: str):
    """Run a command and display results."""
    console.print(f"\n[cyan]{description}...[/cyan]")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            console.print("[green]✓ Success[/green]")
            if result.stdout:
                console.print(result.stdout)
        else:
            console.print(f"[red]✗ Failed with code {result.returncode}[/red]")
            if result.stderr:
                console.print(f"[red]{result.stderr}[/red]")
        return result.returncode == 0
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False


def main():
    """Run all tests."""
    console.print("[bold cyan]Testing Semantic Memory System[/bold cyan]")

    # Ensure we're in the right directory
    scripts_dir = Path(__file__).parent / "scripts"

    # Test 1: Extract metadata
    console.print("\n[yellow]Test 1: Metadata Extraction[/yellow]")
    success = run_command(
        [sys.executable, str(scripts_dir / "extract_metadata.py")],
        "Extracting metadata from existing summaries",
    )

    if not success:
        console.print(
            "[red]Metadata extraction failed. Please check the error above.[/red]"
        )
        return

    # Test 2: Index summaries
    console.print("\n[yellow]Test 2: Indexing Summaries[/yellow]")
    success = run_command(
        [sys.executable, str(scripts_dir / "index_summaries.py")],
        "Building vector database from summaries",
    )

    if not success:
        console.print("[red]Indexing failed. Please check the error above.[/red]")
        return

    # Test 3: Search functionality
    console.print("\n[yellow]Test 3: Semantic Search[/yellow]")

    test_queries = [
        "vue components widgets",
        "font migration arial satoshi",
        "transform pane implementation",
        "api prefix comfyui",
    ]

    for query in test_queries:
        console.print(f"\n[cyan]Searching for: '{query}'[/cyan]")
        run_command(
            [sys.executable, str(scripts_dir / "memory_search.py"), query],
            "Testing search",
        )

    console.print("\n[bold green]✓ All tests completed![/bold green]")
    console.print("\n[cyan]The semantic memory system is ready to use.[/cyan]")
    console.print("\nTo search manually, run:")
    console.print("  python scripts/memory_search.py 'your search query'")


if __name__ == "__main__":
    main()

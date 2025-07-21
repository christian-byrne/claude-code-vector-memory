#!/usr/bin/env python3
"""
Reindex all summaries in the semantic memory system.
Creates a backup before reindexing.
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console

console = Console()


def create_backup():
    """Create a backup of the current database."""
    db_path = Path("chroma_db")

    if not db_path.exists():
        console.print("[yellow]No existing database to backup[/yellow]")
        return None

    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(f"chroma_db_backup_{timestamp}")

    console.print(f"[cyan]Creating backup: {backup_path}[/cyan]")

    try:
        shutil.copytree(db_path, backup_path)
        console.print("[green]✅ Backup created successfully[/green]")
        return backup_path
    except Exception as e:
        console.print(f"[red]❌ Backup failed: {e}[/red]")
        return None


def run_reindex():
    """Run the indexing process."""
    console.print("\n[cyan]Reindexing summaries...[/cyan]")

    # Import and run the indexer
    sys.path.insert(0, str(Path(__file__).parent))

    try:
        from scripts.index_summaries import SummaryIndexer

        indexer = SummaryIndexer()
        indexer.index_all_summaries()
        indexer.get_collection_stats()

        return True
    except Exception as e:
        console.print(f"[red]❌ Reindexing failed: {e}[/red]")
        return False


def main():
    """Main reindex function."""
    console.print("[bold cyan]Semantic Memory System - Reindex[/bold cyan]")
    console.print("=================================\n")

    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        console.print(
            "[red]❌ Error: Not in the claude-code-vector-memory directory[/red]"
        )
        sys.exit(1)

    # Check if venv is activated
    if not hasattr(sys, "real_prefix") and not (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        console.print("[yellow]⚠️  Virtual environment not activated[/yellow]")
        console.print(
            "   Run: source venv/bin/activate (or venv\\Scripts\\activate on Windows)"
        )
        console.print("   Or use: ./setup.sh (or setup.bat on Windows)")
        sys.exit(1)

    # Create backup
    console.print("[cyan]Step 1: Creating backup[/cyan]")
    backup_path = create_backup()

    # Run reindex
    console.print("\n[cyan]Step 2: Reindexing[/cyan]")
    if run_reindex():
        console.print("\n[green]✅ Reindexing completed successfully![/green]")

        if backup_path:
            console.print(f"\n[yellow]Backup saved at: {backup_path}[/yellow]")
            console.print("You can remove it once you've verified the new index works")
    else:
        console.print("\n[red]❌ Reindexing failed[/red]")
        if backup_path:
            console.print(
                f"[yellow]Restore from backup: rm -rf chroma_db && mv {backup_path} chroma_db[/yellow]"
            )
        sys.exit(1)


if __name__ == "__main__":
    main()

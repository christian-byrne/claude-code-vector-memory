#!/usr/bin/env python3
"""
Extract and display metadata from existing summaries.
Useful for understanding what information can be extracted.
"""

import json
import re
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

SUMMARIES_DIR = Path.home() / ".claude" / "compacted-summaries"


def extract_metadata_from_file(filepath: Path) -> dict:
    """Extract all possible metadata from a summary file."""
    content = filepath.read_text(encoding="utf-8")
    filename = filepath.name

    metadata = {"filename": filename}

    # Extract date from filename
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
    if date_match:
        metadata["date"] = date_match.group(1)

    # Extract time from filename
    time_match = re.search(r"(\d{6})", filename)
    if time_match:
        metadata["time"] = time_match.group(1)

    # Extract semantic description
    if "-" in filename and date_match:
        parts = filename.split("-", 7)
        if len(parts) > 6:
            semantic_desc = parts[-1].replace(".md", "").replace("-", " ")
            metadata["semantic_description"] = semantic_desc

    # Extract title
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if title_match:
        metadata["title"] = title_match.group(1).strip()

    # Extract sections
    sections = re.findall(r"^##\s+(.+)$", content, re.MULTILINE)
    metadata["sections"] = sections

    # Extract file paths
    file_paths = re.findall(r"/(?:home|Users)/[^\s:]+\.[a-zA-Z]+", content)
    metadata["mentioned_files"] = list(set(file_paths))[:5]  # Top 5 unique

    # Extract URLs
    urls = re.findall(r"https?://[^\s]+", content)
    metadata["urls"] = list(set(urls))[:5]  # Top 5 unique

    # Extract commands
    commands = []
    for cmd in ["npm", "pip", "git", "python", "node", "cp", "mv", "mkdir"]:
        if cmd in content:
            commands.append(cmd)
    metadata["commands_used"] = commands

    # Extract technologies
    tech_patterns = {
        "vue": r"\b(?:vue|Vue)\b",
        "typescript": r"\b(?:typescript|TypeScript|\.ts)\b",
        "javascript": r"\b(?:javascript|JavaScript|\.js)\b",
        "python": r"\b(?:python|Python|\.py)\b",
        "react": r"\b(?:react|React)\b",
        "comfyui": r"\b(?:comfyui|ComfyUI)\b",
        "primevue": r"\b(?:primevue|PrimeVue)\b",
        "vitest": r"\b(?:vitest|Vitest)\b",
        "playwright": r"\b(?:playwright|Playwright)\b",
        "tailwind": r"\b(?:tailwind|Tailwind)\b",
        "pinia": r"\b(?:pinia|Pinia)\b",
    }

    found_techs = []
    for tech, pattern in tech_patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            found_techs.append(tech)
    metadata["technologies"] = found_techs

    # Content statistics
    metadata["char_count"] = len(content)
    metadata["line_count"] = len(content.splitlines())
    metadata["word_count"] = len(content.split())

    return metadata


def analyze_all_summaries():
    """Analyze all summaries and display findings."""
    if not SUMMARIES_DIR.exists():
        console.print(f"[red]Directory not found: {SUMMARIES_DIR}[/red]")
        return

    summary_files = list(SUMMARIES_DIR.glob("*.md"))
    if not summary_files:
        console.print("[yellow]No summary files found.[/yellow]")
        return

    console.print(f"\n[cyan]Analyzing {len(summary_files)} summary files...[/cyan]\n")

    all_metadata = []
    for filepath in summary_files:
        try:
            metadata = extract_metadata_from_file(filepath)
            all_metadata.append(metadata)
        except Exception as e:
            console.print(f"[red]Error processing {filepath.name}: {e}[/red]")

    # Display summary table
    table = Table(title="Summary Metadata Analysis")
    table.add_column("Filename", style="cyan", width=50)
    table.add_column("Date", style="yellow")
    table.add_column("Words", style="green")
    table.add_column("Technologies", style="magenta", width=30)
    table.add_column("Sections", style="blue")

    for meta in all_metadata:
        table.add_row(
            meta["filename"][:50] + "..."
            if len(meta["filename"]) > 50
            else meta["filename"],
            meta.get("date", "N/A"),
            str(meta.get("word_count", 0)),
            ", ".join(meta.get("technologies", []))[:30],
            str(len(meta.get("sections", []))),
        )

    console.print(table)

    # Aggregate statistics
    console.print("\n[cyan]Aggregate Statistics:[/cyan]")

    # Technology frequency
    tech_freq = {}
    for meta in all_metadata:
        for tech in meta.get("technologies", []):
            tech_freq[tech] = tech_freq.get(tech, 0) + 1

    console.print("\n[green]Most Common Technologies:[/green]")
    for tech, count in sorted(tech_freq.items(), key=lambda x: x[1], reverse=True):
        console.print(f"  • {tech}: {count} sessions")

    # Average content size
    avg_words = sum(m.get("word_count", 0) for m in all_metadata) / len(all_metadata)
    console.print(f"\n[green]Average Summary Size:[/green] {avg_words:.0f} words")

    # Date range
    dates = [m.get("date") for m in all_metadata if m.get("date")]
    if dates:
        console.print(f"\n[green]Date Range:[/green] {min(dates)} to {max(dates)}")

    return all_metadata


def export_metadata_json():
    """Export all metadata to JSON for further analysis."""
    all_metadata = []
    for filepath in SUMMARIES_DIR.glob("*.md"):
        try:
            metadata = extract_metadata_from_file(filepath)
            all_metadata.append(metadata)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    output_path = Path(__file__).parent.parent / "metadata_export.json"
    with open(output_path, "w") as f:
        json.dump(all_metadata, f, indent=2)

    console.print(f"\n[green]Metadata exported to: {output_path}[/green]")


if __name__ == "__main__":
    analyze_all_summaries()

    # Optional: export to JSON
    console.print("\n[cyan]Export metadata to JSON? (y/n):[/cyan] ", end="")
    if input().lower() == "y":
        export_metadata_json()

#!/usr/bin/env python3
"""
Add metadata to existing summaries that don't have YAML frontmatter.
This script analyzes summary content and adds appropriate metadata.
"""

import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml
from rich.console import Console
from rich.progress import track
from rich.table import Table

console = Console()

SUMMARIES_DIR = Path.home() / ".claude" / "compacted-summaries"


class MetadataAdder:
    def __init__(self):
        self.tech_patterns = {
            "vue": r"\b(?:vue|Vue|\.vue)\b",
            "typescript": r"\b(?:typescript|TypeScript|\.ts)\b",
            "javascript": r"\b(?:javascript|JavaScript|\.js)\b",
            "python": r"\b(?:python|Python|\.py)\b",
            "react": r"\b(?:react|React|\.jsx)\b",
            "node": r"\b(?:node|Node|npm)\b",
            "git": r"\b(?:git|Git)\b",
            "comfyui": r"\b(?:comfyui|ComfyUI)\b",
            "primevue": r"\b(?:primevue|PrimeVue)\b",
            "vitest": r"\b(?:vitest|Vitest)\b",
            "playwright": r"\b(?:playwright|Playwright)\b",
            "tailwind": r"\b(?:tailwind|Tailwind)\b",
            "pinia": r"\b(?:pinia|Pinia)\b",
            "sqlite": r"\b(?:sqlite|SQLite)\b",
            "chromadb": r"\b(?:chromadb|ChromaDB)\b",
            "semantic-search": r"\b(?:semantic|embedding|vector)\b",
        }

    def has_yaml_frontmatter(self, content: str) -> bool:
        """Check if content already has YAML frontmatter."""
        return content.strip().startswith("---")

    def extract_title_from_content(self, content: str) -> str:
        """Extract or generate a title from content."""
        # Try to find first # heading
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()

        # Try to find first line that's not empty
        lines = content.strip().split("\n")
        for line in lines:
            if line.strip() and not line.startswith("#"):
                return line.strip()[:50] + "..." if len(line) > 50 else line.strip()

        return "Untitled Session"

    def extract_project_from_paths(self, content: str) -> Optional[str]:
        """Extract project name from file paths."""
        # Look for common project paths
        project_patterns = [
            r"/projects/([^/]+)/",
            r"/home/[^/]+/([^/]+)/",
            r"([^/]+)/src/",
            r"([^/]+)/components/",
        ]

        for pattern in project_patterns:
            match = re.search(pattern, content)
            if match:
                project = match.group(1)
                # Clean up common prefixes
                if (
                    project.startswith("comfyui-")
                    or "comfyui" in project.lower()
                    or project not in ["home", "projects", "user", "Users"]
                ):
                    return project

        return None

    def estimate_complexity(self, content: str) -> str:
        """Estimate session complexity."""
        content.split("\n")
        word_count = len(content.split())

        # Count various indicators
        file_count = len(re.findall(r"(?:\.ts|\.js|\.vue|\.py|\.md|\.json)", content))
        len(re.findall(r"(?:npm|pip|git|python|node)", content))
        section_count = len(re.findall(r"^##\s+", content, re.MULTILINE))

        # Scoring
        if word_count > 2000 or file_count > 10 or section_count > 6:
            return "high"
        elif word_count > 800 or file_count > 5 or section_count > 3:
            return "medium"
        else:
            return "low"

    def extract_technologies(self, content: str) -> list[str]:
        """Extract technology keywords from content."""
        found_techs = []
        content.lower()

        for tech, pattern in self.tech_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                found_techs.append(tech)

        return sorted(set(found_techs))

    def extract_key_files(self, content: str) -> list[str]:
        """Extract important file paths."""
        # Find file paths
        file_pattern = r"(/[^\s:]+(?:\.ts|\.js|\.vue|\.py|\.md|\.json|\.css|\.html))"
        files = re.findall(file_pattern, content)

        # Also look for relative paths
        rel_pattern = (
            r"((?:src/|components/|tests/|scripts/)[^\s:]+(?:\.ts|\.js|\.vue|\.py))"
        )
        rel_files = re.findall(rel_pattern, content)

        all_files = files + rel_files
        # Deduplicate and return top 10 most relevant
        unique_files = []
        seen = set()
        for f in all_files:
            if f not in seen and not f.endswith(".d.ts"):
                seen.add(f)
                unique_files.append(f)

        return unique_files[:10]

    def determine_outcome(self, content: str) -> str:
        """Determine session outcome based on content."""
        content_lower = content.lower()

        # Check for blocking indicators
        if any(
            word in content_lower
            for word in ["error", "failed", "blocked", "issue", "problem"]
        ):
            # But check if they were resolved
            if any(
                word in content_lower
                for word in ["fixed", "resolved", "completed", "success"]
            ):
                return "success"
            else:
                return "partial"

        # Check for success indicators
        if any(
            word in content_lower
            for word in ["completed", "implemented", "created", "added"]
        ):
            return "success"

        return "success"  # Default to success if unclear

    def estimate_duration(self, content: str) -> str:
        """Estimate session duration based on content."""
        word_count = len(content.split())
        file_count = len(re.findall(r"(?:\.ts|\.js|\.vue|\.py|\.md)", content))

        # Rough estimation
        if word_count > 2000 or file_count > 10:
            return "2h+"
        elif word_count > 1000 or file_count > 5:
            return "1h"
        else:
            return "30m"

    def extract_tags(self, content: str, technologies: list[str]) -> list[str]:
        """Extract semantic tags from content."""
        tags = set(technologies)

        # Add action tags
        if re.search(r"\b(?:implement|create|add)\b", content, re.IGNORECASE):
            tags.add("implementation")
        if re.search(r"\b(?:fix|debug|resolve)\b", content, re.IGNORECASE):
            tags.add("bugfix")
        if re.search(r"\b(?:test|testing|vitest|playwright)\b", content, re.IGNORECASE):
            tags.add("testing")
        if re.search(r"\b(?:refactor|optimize|improve)\b", content, re.IGNORECASE):
            tags.add("refactoring")
        if re.search(r"\b(?:document|docs|readme)\b", content, re.IGNORECASE):
            tags.add("documentation")

        # Add domain tags
        if re.search(r"\b(?:ui|component|frontend|widget)\b", content, re.IGNORECASE):
            tags.add("frontend")
        if re.search(r"\b(?:api|backend|server|endpoint)\b", content, re.IGNORECASE):
            tags.add("backend")
        if re.search(r"\b(?:database|query|migration)\b", content, re.IGNORECASE):
            tags.add("database")

        return sorted(tags)

    def generate_metadata(self, content: str, filename: str) -> dict:
        """Generate metadata for a summary."""
        # Extract date from filename
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
        session_date = (
            date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")
        )

        # Extract all metadata
        title = self.extract_title_from_content(content)
        technologies = self.extract_technologies(content)
        tags = self.extract_tags(content, technologies)
        project = self.extract_project_from_paths(content)
        complexity = self.estimate_complexity(content)
        outcome = self.determine_outcome(content)
        duration = self.estimate_duration(content)
        key_files = self.extract_key_files(content)

        metadata = {
            "title": title,
            "tags": tags,
            "complexity": complexity,
            "outcome": outcome,
            "duration": duration,
            "date": session_date,
        }

        if project:
            metadata["project"] = project
        if technologies:
            metadata["technologies"] = technologies
        if key_files:
            metadata["key_files"] = key_files

        return metadata

    def add_metadata_to_file(self, filepath: Path) -> bool:
        """Add metadata to a single file."""
        try:
            content = filepath.read_text(encoding="utf-8")

            # Skip if already has metadata
            if self.has_yaml_frontmatter(content):
                return False

            # Generate metadata
            metadata = self.generate_metadata(content, filepath.name)

            # Create YAML frontmatter
            yaml_content = yaml.dump(
                metadata, default_flow_style=False, sort_keys=False
            )

            # Combine with content
            new_content = f"---\n{yaml_content}---\n\n{content}"

            # Backup original
            backup_path = filepath.with_suffix(".md.bak")
            shutil.copy2(filepath, backup_path)

            # Write new content
            filepath.write_text(new_content, encoding="utf-8")

            return True

        except Exception as e:
            console.print(f"[red]Error processing {filepath.name}: {e}[/red]")
            return False

    def process_all_summaries(self) -> None:
        """Process all summaries and add metadata."""
        if not SUMMARIES_DIR.exists():
            console.print(f"[red]Summaries directory not found: {SUMMARIES_DIR}[/red]")
            return

        summary_files = list(SUMMARIES_DIR.glob("*.md"))
        if not summary_files:
            console.print("[yellow]No summary files found.[/yellow]")
            return

        console.print(f"\n[cyan]Found {len(summary_files)} summary files[/cyan]")

        # Check which need metadata
        need_metadata = []
        for filepath in summary_files:
            content = filepath.read_text(encoding="utf-8")
            if not self.has_yaml_frontmatter(content):
                need_metadata.append(filepath)

        if not need_metadata:
            console.print("[green]All summaries already have metadata![/green]")
            return

        console.print(f"[yellow]{len(need_metadata)} files need metadata[/yellow]\n")

        # Process files
        results = []
        for filepath in track(need_metadata, description="Adding metadata..."):
            success = self.add_metadata_to_file(filepath)
            if success:
                results.append(filepath.name)

        # Show results
        if results:
            console.print(
                f"\n[green]Successfully added metadata to {len(results)} files:[/green]"
            )
            table = Table(title="Updated Summaries")
            table.add_column("Filename", style="cyan")

            for filename in results:
                table.add_row(filename)

            console.print(table)

            console.print("\n[yellow]Backup files created with .bak extension[/yellow]")
            console.print(
                "[cyan]Run reindex.sh to update the search index with new metadata[/cyan]"
            )
        else:
            console.print("\n[red]No files were updated[/red]")


def main():
    """Main entry point."""
    adder = MetadataAdder()

    console.print("[bold cyan]Adding Metadata to Existing Summaries[/bold cyan]")

    # Confirm with user
    console.print("\n[yellow]This will:[/yellow]")
    console.print("1. Analyze all summaries without metadata")
    console.print("2. Generate appropriate YAML frontmatter")
    console.print("3. Create .bak backup files")
    console.print("4. Update the original files")

    response = console.input("\n[cyan]Continue? (y/N):[/cyan] ")
    if response.lower() != "y":
        console.print("Aborted.")
        return

    adder.process_all_summaries()


if __name__ == "__main__":
    main()

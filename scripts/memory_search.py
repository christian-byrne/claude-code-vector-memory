#!/usr/bin/env python3
"""
Semantic search for Claude Code session summaries.
Finds the most relevant past sessions based on query similarity.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import chromadb
import chromadb.errors
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

# Configuration
DB_PATH = Path(__file__).parent.parent / "chroma_db"
COLLECTION_NAME = "claude_summaries"
SUMMARIES_DIR = Path.home() / ".claude" / "compacted-summaries"


class MemorySearcher:
    def __init__(self):
        """Initialize the searcher with ChromaDB connection."""
        try:
            self.client = chromadb.PersistentClient(path=str(DB_PATH))
            self.collection = self.client.get_collection(name=COLLECTION_NAME)
        except chromadb.errors.NotFoundError:
            console.print(
                f"[red]Collection '{COLLECTION_NAME}' not found in database.[/red]"
            )
            console.print(
                "[yellow]Please run index_summaries.py first to create and populate the database.[/yellow]"
            )
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error connecting to database: {e}[/red]")
            console.print(
                "[yellow]Please ensure ChromaDB is properly installed and the database path is accessible.[/yellow]"
            )
            sys.exit(1)

    def calculate_recency_score(self, date_str: str) -> float:
        """Calculate recency score (0-1) based on session date."""
        if not date_str:
            return 0.5  # Default middle score if no date

        try:
            session_date = datetime.strptime(date_str, "%Y-%m-%d")
            days_ago = (datetime.now() - session_date).days

            # Scoring: 1.0 for today, decreasing over time
            if days_ago <= 7:
                return 1.0
            elif days_ago <= 30:
                return 0.8
            elif days_ago <= 90:
                return 0.6
            elif days_ago <= 180:
                return 0.4
            else:
                return 0.2
        except:
            return 0.5

    def search(
        self, query: str, n_results: int = 5, min_similarity: float = 0.3
    ) -> list[dict]:
        """
        Search for similar summaries using semantic similarity.

        Args:
            query: Search query text
            n_results: Number of results to return
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            List of search results with metadata and scores
        """
        # Perform semantic search
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results * 2,  # Get more to filter by threshold
            include=["metadatas", "documents", "distances"],
        )

        if not results["ids"][0]:
            return []

        # Process results
        processed_results = []
        for i, _doc_id in enumerate(results["ids"][0]):
            distance = results["distances"][0][i]
            # Convert distance to similarity score
            # Using inverse distance formula for better range with ChromaDB's L2 distance
            similarity = 1 / (1 + distance)

            if similarity < min_similarity:
                continue

            metadata = results["metadatas"][0][i]
            document = results["documents"][0][i]

            # Calculate hybrid score
            recency_score = self.calculate_recency_score(metadata.get("session_date"))

            # Weighted scoring: 70% semantic similarity, 20% recency, 10% complexity bonus
            complexity_bonus = 0.1 if metadata.get("complexity") == "high" else 0
            hybrid_score = (0.7 * similarity) + (0.2 * recency_score) + complexity_bonus

            # Extract preview from document
            lines = document.split("\n")
            preview_lines = [
                line
                for line in lines[:10]
                if line.strip()
                and not line.startswith("Title:")
                and not line.startswith("Description:")
            ]
            preview = "\n".join(preview_lines[:5])

            processed_results.append(
                {
                    "filename": metadata.get("filename", "unknown"),
                    "title": metadata.get("title", "Untitled"),
                    "date": metadata.get("session_date", "unknown"),
                    "similarity": similarity,
                    "hybrid_score": hybrid_score,
                    "complexity": metadata.get("complexity", "unknown"),
                    "technologies": json.loads(metadata.get("technologies", "[]")),
                    "preview": preview,
                    "semantic_desc": metadata.get("semantic_description", ""),
                    "file_path": SUMMARIES_DIR / metadata.get("filename", ""),
                }
            )

        # Sort by hybrid score
        processed_results.sort(key=lambda x: x["hybrid_score"], reverse=True)

        return processed_results[:n_results]

    def display_results(self, results: list[dict], query: str) -> None:
        """Display search results in a formatted table."""
        if not results:
            console.print("[yellow]No relevant summaries found.[/yellow]")
            return

        console.print(
            f"\n[cyan]Found {len(results)} relevant session(s) for:[/cyan] '{query}'\n"
        )

        for i, result in enumerate(results, 1):
            # Create result panel
            title = f"{i}. {result['title']}"

            content = f"""
**File:** {result["filename"]}
**Date:** {result["date"]}
**Similarity:** {result["similarity"]:.1%} | **Relevance Score:** {result["hybrid_score"]:.1%}
**Complexity:** {result["complexity"]}
**Technologies:** {", ".join(result["technologies"]) if result["technologies"] else "N/A"}

**Preview:**
```
{result["preview"][:300]}...
```

**Path:** {result["file_path"]}
"""

            panel = Panel(
                Markdown(content),
                title=title,
                border_style="green" if result["similarity"] > 0.8 else "yellow",
            )
            console.print(panel)

    def get_full_summary(self, filename: str) -> Optional[str]:
        """Read the full content of a summary file."""
        filepath = SUMMARIES_DIR / filename
        if filepath.exists():
            return filepath.read_text(encoding="utf-8")
        return None


def main():
    """Main entry point for command-line usage."""
    if len(sys.argv) < 2:
        console.print("[red]Usage: python memory_search.py <query>[/red]")
        console.print("Example: python memory_search.py 'vue widget implementation'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    # Initialize searcher
    searcher = MemorySearcher()

    # Search
    console.print(f"[cyan]Searching for:[/cyan] {query}")
    results = searcher.search(query, n_results=3)

    # Display results
    searcher.display_results(results, query)

    # Offer to read full summaries
    if results:
        console.print("\n[cyan]To read a full summary, use:[/cyan]")
        for _i, result in enumerate(results, 1):
            console.print(f"  cat {result['file_path']}")


if __name__ == "__main__":
    main()

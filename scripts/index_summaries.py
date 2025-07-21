#!/usr/bin/env python3
"""
Index all session summaries into ChromaDB for semantic search.
Scans ~/.claude/compacted-summaries/ and creates embeddings for each.
"""

import json
import re
from datetime import datetime
from pathlib import Path

import chromadb
from rich.console import Console
from rich.progress import track
from rich.table import Table
from sentence_transformers import SentenceTransformer

console = Console()

# Configuration
SUMMARIES_DIR = Path.home() / ".claude" / "compacted-summaries"
DB_PATH = Path(__file__).parent.parent / "chroma_db"
COLLECTION_NAME = "claude_summaries"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class SummaryIndexer:
    def __init__(self):
        """Initialize the indexer with ChromaDB and embedding model."""
        console.print("[cyan]Initializing semantic memory system...[/cyan]")

        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(path=str(DB_PATH))

        # Create or get collection
        try:
            self.collection = self.client.get_collection(name=COLLECTION_NAME)
            console.print(
                f"[green]Found existing collection: {COLLECTION_NAME}[/green]"
            )
        except Exception:
            # Collection doesn't exist, create it
            console.print(
                f"[yellow]Collection not found, creating new collection: {COLLECTION_NAME}[/yellow]"
            )
            self.collection = self.client.create_collection(
                name=COLLECTION_NAME,
                metadata={"description": "Claude Code session summaries"},
            )
            console.print(f"[green]Created new collection: {COLLECTION_NAME}[/green]")

        # Initialize sentence transformer
        console.print("[cyan]Loading embedding model...[/cyan]")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        console.print("[green]Model loaded successfully[/green]")

    def extract_metadata(self, content: str, filename: str) -> dict:
        """Extract metadata from summary content and filename."""
        metadata = {"filename": filename, "indexed_at": datetime.now().isoformat()}

        # Extract date from filename (YYYY-MM-DD format)
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
        if date_match:
            metadata["session_date"] = date_match.group(1)

        # Extract semantic description from filename
        if "-" in filename and date_match:
            parts = filename.split("-", 7)  # Split after date-time pattern
            if len(parts) > 6:
                semantic_desc = parts[-1].replace(".md", "").replace("-", " ")
                metadata["semantic_description"] = semantic_desc

        # Extract title from content (first # heading)
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_match:
            metadata["title"] = title_match.group(1).strip()

        # Extract project path if mentioned
        project_match = re.search(r"/home/[^/]+/projects/([^\s]+)", content)
        if project_match:
            metadata["project_path"] = project_match.group(1)

        # Count various elements for complexity scoring
        metadata["file_count"] = len(
            re.findall(
                r"(?:modified|created|updated).*?\.(?:ts|js|vue|py|md)",
                content,
                re.IGNORECASE,
            )
        )
        metadata["command_count"] = len(
            re.findall(r"(?:npm|pip|git|grep|find|cp|mv)", content)
        )
        metadata["url_count"] = len(re.findall(r"https?://[^\s]+", content))

        # Estimate complexity based on content
        content_length = len(content)
        if content_length > 3000 or metadata["file_count"] > 10:
            metadata["complexity"] = "high"
        elif content_length > 1500 or metadata["file_count"] > 5:
            metadata["complexity"] = "medium"
        else:
            metadata["complexity"] = "low"

        # Extract key technologies mentioned
        tech_keywords = [
            "vue",
            "typescript",
            "python",
            "react",
            "node",
            "comfyui",
            "primevue",
            "vitest",
            "playwright",
            "tailwind",
            "pinia",
            "sqlite",
            "chromadb",
        ]
        found_techs = [tech for tech in tech_keywords if tech in content.lower()]
        if found_techs:
            metadata["technologies"] = json.dumps(found_techs)

        return metadata

    def create_document_text(self, content: str, metadata: dict) -> str:
        """Create searchable document text combining content and metadata."""
        # Combine title, semantic description, and content for better search
        parts = []

        if "title" in metadata:
            parts.append(f"Title: {metadata['title']}")
        if "semantic_description" in metadata:
            parts.append(f"Description: {metadata['semantic_description']}")
        if "technologies" in metadata:
            techs = json.loads(metadata["technologies"])
            parts.append(f"Technologies: {', '.join(techs)}")

        parts.append("\n" + content)

        return "\n".join(parts)

    def index_summary(self, filepath: Path) -> tuple[str, dict]:
        """Index a single summary file."""
        # Read file content
        content = filepath.read_text(encoding="utf-8")
        filename = filepath.name

        # Extract metadata
        metadata = self.extract_metadata(content, filename)

        # Create document ID (use filename as unique ID)
        doc_id = filename

        # Create searchable text
        doc_text = self.create_document_text(content, metadata)

        # Add to collection (ChromaDB handles embedding automatically)
        self.collection.upsert(ids=[doc_id], documents=[doc_text], metadatas=[metadata])

        return doc_id, metadata

    def index_all_summaries(self) -> None:
        """Index all summaries in the directory."""
        if not SUMMARIES_DIR.exists():
            console.print(
                f"[yellow]Creating summaries directory: {SUMMARIES_DIR}[/yellow]"
            )
            SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)

        # Get all markdown files
        summary_files = list(SUMMARIES_DIR.glob("*.md"))

        if not summary_files:
            console.print(f"[yellow]No summary files found in {SUMMARIES_DIR}[/yellow]")
            return

        console.print(
            f"\n[cyan]Found {len(summary_files)} summary files to index[/cyan]"
        )

        # Index each file with progress bar
        indexed_count = 0
        results = []

        for filepath in track(summary_files, description="Indexing summaries..."):
            try:
                doc_id, metadata = self.index_summary(filepath)
                indexed_count += 1
                results.append(
                    {
                        "filename": metadata["filename"],
                        "title": metadata.get("title", "N/A"),
                        "date": metadata.get("session_date", "N/A"),
                        "complexity": metadata.get("complexity", "N/A"),
                    }
                )
            except Exception as e:
                console.print(f"[red]Error indexing {filepath.name}: {e}[/red]")

        # Display results table
        console.print(
            f"\n[green]Successfully indexed {indexed_count}/{len(summary_files)} summaries[/green]\n"
        )

        if results:
            table = Table(title="Indexed Summaries")
            table.add_column("Filename", style="cyan")
            table.add_column("Title", style="green")
            table.add_column("Date", style="yellow")
            table.add_column("Complexity", style="magenta")

            for result in results:
                table.add_row(
                    result["filename"],
                    result["title"][:50] + "..."
                    if len(result["title"]) > 50
                    else result["title"],
                    result["date"],
                    result["complexity"],
                )

            console.print(table)

    def get_collection_stats(self) -> None:
        """Display collection statistics."""
        count = self.collection.count()
        console.print("\n[cyan]Collection Statistics:[/cyan]")
        console.print(f"Total documents: {count}")
        console.print(f"Database path: {DB_PATH}")
        console.print(f"Collection name: {COLLECTION_NAME}")
        console.print(f"Embedding model: {EMBEDDING_MODEL}")


if __name__ == "__main__":
    indexer = SummaryIndexer()
    indexer.index_all_summaries()
    indexer.get_collection_stats()

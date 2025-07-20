#!/usr/bin/env python3
"""
Health check and diagnostics for the semantic memory system.
"""

import json
import time
from datetime import datetime
from pathlib import Path

import chromadb
import chromadb.errors
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table
from sentence_transformers import SentenceTransformer

console = Console()

# Configuration
DB_PATH = Path(__file__).parent.parent / "chroma_db"
COLLECTION_NAME = "claude_summaries"
SUMMARIES_DIR = Path.home() / ".claude" / "compacted-summaries"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class MemoryHealthChecker:
    def __init__(self):
        """Initialize health checker."""
        self.db_exists = DB_PATH.exists()
        self.client = None
        self.collection = None
        self.embedder = None

    def check_database_status(self) -> dict:
        """Check ChromaDB status and basic metrics."""
        status = {
            "accessible": False,
            "total_documents": 0,
            "database_size_mb": 0,
            "error": None,
        }

        try:
            if not self.db_exists:
                status["error"] = "Database directory not found"
                return status

            self.client = chromadb.PersistentClient(path=str(DB_PATH))

            try:
                self.collection = self.client.get_collection(name=COLLECTION_NAME)
                status["accessible"] = True
                status["total_documents"] = self.collection.count()
            except chromadb.errors.NotFoundError:
                status["accessible"] = True  # DB is accessible, just no collection yet
                status["total_documents"] = 0
                status["error"] = (
                    f"Collection '{COLLECTION_NAME}' not found. Run index_summaries.py first."
                )

            # Calculate database size
            db_size = sum(f.stat().st_size for f in DB_PATH.rglob("*") if f.is_file())
            status["database_size_mb"] = round(db_size / (1024 * 1024), 2)

        except Exception as e:
            status["error"] = str(e)

        return status

    def analyze_coverage(self) -> dict:
        """Analyze which summaries are indexed."""
        coverage = {
            "total_summaries": 0,
            "indexed_summaries": 0,
            "missing_summaries": [],
            "orphaned_entries": [],
        }

        if not SUMMARIES_DIR.exists():
            coverage["error"] = "Summaries directory not found"
            return coverage

        # Get all summary files
        summary_files = list(SUMMARIES_DIR.glob("*.md"))
        coverage["total_summaries"] = len(summary_files)

        if self.collection:
            # Get all indexed documents
            try:
                indexed_docs = self.collection.get()
                indexed_filenames = set()

                if indexed_docs and indexed_docs.get("metadatas"):
                    for metadata in indexed_docs["metadatas"]:
                        if metadata and "filename" in metadata:
                            indexed_filenames.add(metadata["filename"])

                coverage["indexed_summaries"] = len(indexed_filenames)

                # Find missing summaries
                for summary_file in summary_files:
                    if summary_file.name not in indexed_filenames:
                        coverage["missing_summaries"].append(summary_file.name)

                # Find orphaned entries (in DB but not on disk)
                existing_files = {f.name for f in summary_files}
                for indexed_name in indexed_filenames:
                    if indexed_name not in existing_files:
                        coverage["orphaned_entries"].append(indexed_name)

            except Exception as e:
                coverage["error"] = str(e)

        return coverage

    def test_search_quality(self) -> list[dict]:
        """Test search functionality with common queries."""
        test_queries = [
            "vue component implementation",
            "typescript type safety",
            "python script",
            "git commit",
            "testing vitest",
            "frontend ui",
        ]

        results = []

        if not self.collection:
            return results

        for query in test_queries:
            try:
                start_time = time.time()

                search_results = self.collection.query(
                    query_texts=[query], n_results=3, include=["metadatas", "distances"]
                )

                search_time = (time.time() - start_time) * 1000  # ms

                # Calculate average similarity
                similarities = []
                if search_results["distances"] and search_results["distances"][0]:
                    for distance in search_results["distances"][0]:
                        similarity = max(0, 1 - (distance**2) / 2)
                        similarities.append(similarity)

                avg_similarity = (
                    sum(similarities) / len(similarities) if similarities else 0
                )

                results.append(
                    {
                        "query": query,
                        "num_results": len(similarities),
                        "avg_similarity": avg_similarity,
                        "search_time_ms": round(search_time, 2),
                        "top_match": search_results["metadatas"][0][0].get(
                            "title", "N/A"
                        )
                        if search_results["metadatas"][0]
                        else "None",
                    }
                )

            except Exception as e:
                results.append({"query": query, "error": str(e)})

        return results

    def analyze_metadata_quality(self) -> dict:
        """Analyze the quality of metadata in indexed documents."""
        quality = {
            "total": 0,
            "with_title": 0,
            "with_date": 0,
            "with_semantic_desc": 0,
            "with_technologies": 0,
            "with_complexity": 0,
            "missing_metadata": [],
        }

        if not self.collection:
            return quality

        try:
            docs = self.collection.get()
            if docs and docs.get("metadatas"):
                quality["total"] = len(docs["metadatas"])

                for i, metadata in enumerate(docs["metadatas"]):
                    if not metadata:
                        continue

                    doc_id = docs["ids"][i] if i < len(docs["ids"]) else "unknown"
                    missing = []

                    if "title" in metadata and metadata["title"]:
                        quality["with_title"] += 1
                    else:
                        missing.append("title")

                    if "session_date" in metadata and metadata["session_date"]:
                        quality["with_date"] += 1
                    else:
                        missing.append("date")

                    if (
                        "semantic_description" in metadata
                        and metadata["semantic_description"]
                    ):
                        quality["with_semantic_desc"] += 1
                    else:
                        missing.append("semantic_desc")

                    if "technologies" in metadata and metadata["technologies"] != "[]":
                        quality["with_technologies"] += 1
                    else:
                        missing.append("technologies")

                    if "complexity" in metadata and metadata["complexity"]:
                        quality["with_complexity"] += 1
                    else:
                        missing.append("complexity")

                    if missing:
                        quality["missing_metadata"].append(
                            {
                                "filename": metadata.get("filename", doc_id),
                                "missing": missing,
                            }
                        )

        except Exception as e:
            quality["error"] = str(e)

        return quality

    def test_embedding_model(self) -> dict:
        """Test the embedding model."""
        model_status = {
            "model_name": EMBEDDING_MODEL,
            "loaded": False,
            "dimension": None,
            "test_embedding_time_ms": None,
        }

        try:
            console.print("[cyan]Loading embedding model for testing...[/cyan]")
            self.embedder = SentenceTransformer(EMBEDDING_MODEL)
            model_status["loaded"] = True

            # Test embedding generation
            test_text = "This is a test sentence for embedding generation."
            start_time = time.time()
            embedding = self.embedder.encode(test_text)
            embedding_time = (time.time() - start_time) * 1000

            model_status["dimension"] = len(embedding)
            model_status["test_embedding_time_ms"] = round(embedding_time, 2)

        except Exception as e:
            model_status["error"] = str(e)

        return model_status

    def generate_report(self) -> None:
        """Generate comprehensive health report."""
        console.print("\n[bold cyan]Semantic Memory System Health Check[/bold cyan]\n")

        with Progress() as progress:
            task = progress.add_task("[cyan]Running health checks...", total=5)

            # 1. Database Status
            progress.update(task, description="[cyan]Checking database status...")
            db_status = self.check_database_status()
            progress.advance(task)

            # 2. Coverage Analysis
            progress.update(task, description="[cyan]Analyzing coverage...")
            coverage = self.analyze_coverage()
            progress.advance(task)

            # 3. Search Quality
            progress.update(task, description="[cyan]Testing search quality...")
            search_results = self.test_search_quality()
            progress.advance(task)

            # 4. Metadata Quality
            progress.update(task, description="[cyan]Analyzing metadata quality...")
            metadata_quality = self.analyze_metadata_quality()
            progress.advance(task)

            # 5. Model Status
            progress.update(task, description="[cyan]Testing embedding model...")
            model_status = self.test_embedding_model()
            progress.advance(task)

        # Generate report
        console.print("\n[bold green]═══ Health Report ═══[/bold green]\n")

        # Database Status
        if db_status["accessible"]:
            status_text = f"✅ Accessible | {db_status['total_documents']} documents | {db_status['database_size_mb']} MB"
        else:
            status_text = (
                f"❌ Not accessible: {db_status.get('error', 'Unknown error')}"
            )

        console.print(
            Panel(
                status_text,
                title="Database Status",
                border_style="green" if db_status["accessible"] else "red",
            )
        )

        # Coverage Analysis
        coverage_table = Table(title="Coverage Analysis")
        coverage_table.add_column("Metric", style="cyan")
        coverage_table.add_column("Value", style="green")
        coverage_table.add_row("Total Summaries", str(coverage["total_summaries"]))
        coverage_table.add_row("Indexed", str(coverage["indexed_summaries"]))
        coverage_table.add_row("Missing", str(len(coverage["missing_summaries"])))
        coverage_table.add_row("Orphaned", str(len(coverage["orphaned_entries"])))
        console.print(coverage_table)

        if coverage["missing_summaries"]:
            console.print("\n[yellow]Missing summaries:[/yellow]")
            for missing in coverage["missing_summaries"][:5]:
                console.print(f"  - {missing}")
            if len(coverage["missing_summaries"]) > 5:
                console.print(
                    f"  ... and {len(coverage['missing_summaries']) - 5} more"
                )

        # Search Quality
        if search_results:
            search_table = Table(title="Search Quality Tests")
            search_table.add_column("Query", style="cyan")
            search_table.add_column("Results", style="yellow")
            search_table.add_column("Avg Similarity", style="green")
            search_table.add_column("Time (ms)", style="magenta")

            for result in search_results:
                if "error" not in result:
                    search_table.add_row(
                        result["query"],
                        str(result["num_results"]),
                        f"{result['avg_similarity']:.1%}",
                        str(result["search_time_ms"]),
                    )
            console.print(search_table)

        # Metadata Quality
        if metadata_quality["total"] > 0:
            quality_table = Table(title="Metadata Quality")
            quality_table.add_column("Field", style="cyan")
            quality_table.add_column("Coverage", style="green")
            quality_table.add_column("Percentage", style="yellow")

            fields = [
                ("Title", metadata_quality["with_title"]),
                ("Date", metadata_quality["with_date"]),
                ("Semantic Description", metadata_quality["with_semantic_desc"]),
                ("Technologies", metadata_quality["with_technologies"]),
                ("Complexity", metadata_quality["with_complexity"]),
            ]

            for field_name, count in fields:
                percentage = (count / metadata_quality["total"]) * 100
                quality_table.add_row(
                    field_name,
                    f"{count}/{metadata_quality['total']}",
                    f"{percentage:.1f}%",
                )
            console.print(quality_table)

        # Model Status
        if model_status["loaded"]:
            model_text = f"✅ Model loaded | Dimension: {model_status['dimension']} | Test time: {model_status['test_embedding_time_ms']}ms"
        else:
            model_text = (
                f"❌ Model not loaded: {model_status.get('error', 'Unknown error')}"
            )

        console.print(
            Panel(
                model_text,
                title="Embedding Model Status",
                border_style="green" if model_status["loaded"] else "red",
            )
        )

        # Recommendations
        console.print("\n[bold yellow]Recommendations:[/bold yellow]")

        recommendations = []

        if coverage["missing_summaries"]:
            recommendations.append(
                f"Index {len(coverage['missing_summaries'])} missing summaries by running: python scripts/index_summaries.py"
            )

        if coverage["orphaned_entries"]:
            recommendations.append(
                f"Clean up {len(coverage['orphaned_entries'])} orphaned database entries"
            )

        if metadata_quality["total"] > 0:
            low_quality_fields = []
            for field, count in [
                ("title", metadata_quality["with_title"]),
                ("date", metadata_quality["with_date"]),
                ("technologies", metadata_quality["with_technologies"]),
            ]:
                if count / metadata_quality["total"] < 0.8:
                    low_quality_fields.append(field)

            if low_quality_fields:
                recommendations.append(
                    f"Improve metadata for fields: {', '.join(low_quality_fields)}"
                )

        if not recommendations:
            recommendations.append("System is healthy! No immediate actions needed.")

        for i, rec in enumerate(recommendations, 1):
            console.print(f"{i}. {rec}")

        # Save detailed report
        report_path = Path(__file__).parent.parent / "health_report.json"
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "database_status": db_status,
            "coverage": coverage,
            "search_quality": search_results,
            "metadata_quality": metadata_quality,
            "model_status": model_status,
        }

        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)

        console.print(f"\n[green]Detailed report saved to: {report_path}[/green]")


if __name__ == "__main__":
    checker = MemoryHealthChecker()
    checker.generate_report()

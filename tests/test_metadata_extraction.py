#!/usr/bin/env python3
"""
Unit tests for metadata extraction functionality.
"""

import sys
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.index_summaries import SummaryIndexer


class TestMetadataExtraction(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.indexer = SummaryIndexer()

    def test_extract_date_from_filename(self):
        """Test date extraction from various filename formats."""
        test_cases = [
            ("summary-2025-06-29-181658-vue-widgets.md", "2025-06-29"),
            ("summary-2024-12-25-000000.md", "2024-12-25"),
            ("no-date-in-filename.md", None),
        ]

        for filename, expected_date in test_cases:
            content = "# Test Summary"
            metadata = self.indexer.extract_metadata(content, filename)
            if expected_date:
                self.assertEqual(metadata.get("session_date"), expected_date)
            else:
                self.assertNotIn("session_date", metadata)

    def test_extract_semantic_description(self):
        """Test semantic description extraction from filename."""
        test_cases = [
            (
                "summary-2025-06-29-181658-vue-widgets-transform-pane.md",
                "vue widgets transform pane",
            ),
            ("summary-2025-06-29-181658.md", None),
        ]

        for filename, expected_desc in test_cases:
            content = "# Test"
            metadata = self.indexer.extract_metadata(content, filename)
            if expected_desc:
                self.assertEqual(metadata.get("semantic_description"), expected_desc)
            else:
                self.assertNotIn("semantic_description", metadata)

    def test_extract_title(self):
        """Test title extraction from markdown content."""
        test_cases = [
            (
                "# Vue Widget Implementation\n\nSome content",
                "Vue Widget Implementation",
            ),
            ("## Not a title\n# Actual Title\n", "Actual Title"),
            ("No title here", None),
        ]

        for content, expected_title in test_cases:
            metadata = self.indexer.extract_metadata(content, "test.md")
            if expected_title:
                self.assertEqual(metadata.get("title"), expected_title)
            else:
                self.assertNotIn("title", metadata)

    def test_complexity_scoring(self):
        """Test complexity scoring based on content."""
        # Low complexity
        low_content = "Short summary with minimal content."
        metadata = self.indexer.extract_metadata(low_content, "test.md")
        self.assertEqual(metadata.get("complexity"), "low")

        # Medium complexity
        medium_content = "# Summary\n" + ("Modified file.ts\n" * 6) + ("x" * 1600)
        metadata = self.indexer.extract_metadata(medium_content, "test.md")
        self.assertEqual(metadata.get("complexity"), "medium")

        # High complexity
        high_content = "# Summary\n" + ("Modified file.ts\n" * 12) + ("x" * 3500)
        metadata = self.indexer.extract_metadata(high_content, "test.md")
        self.assertEqual(metadata.get("complexity"), "high")

    def test_technology_extraction(self):
        """Test extraction of technology keywords."""
        content = """
        # Vue and TypeScript Implementation

        Used Vue 3 with TypeScript for the frontend.
        Also integrated PrimeVue components and Vitest for testing.
        Backend uses Python with SQLite database.
        """

        metadata = self.indexer.extract_metadata(content, "test.md")
        technologies = metadata.get("technologies", "[]")

        # Should be JSON string
        import json

        tech_list = json.loads(technologies)

        expected_techs = ["vue", "typescript", "primevue", "vitest", "python", "sqlite"]
        for tech in expected_techs:
            self.assertIn(tech, tech_list)

    def test_project_path_extraction(self):
        """Test extraction of project paths."""
        content = """
        Modified files in /home/user/projects/comfyui-frontend/src/
        Also updated /home/user/projects/another-project/test.ts
        """

        metadata = self.indexer.extract_metadata(content, "test.md")
        # Should extract first project path found
        self.assertEqual(metadata.get("project_path"), "comfyui-frontend/src/")

    def test_file_and_command_counting(self):
        """Test counting of files and commands."""
        content = """
        Modified src/components/Widget.vue
        Updated tests/widget.test.ts
        Created new file config.json

        Ran npm install
        Used git commit
        Executed pip install transformers
        """

        metadata = self.indexer.extract_metadata(content, "test.md")
        self.assertEqual(metadata.get("file_count"), 3)
        self.assertEqual(metadata.get("command_count"), 3)


if __name__ == "__main__":
    unittest.main()

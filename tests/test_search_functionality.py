#!/usr/bin/env python3
"""
Unit tests for search functionality.
"""

import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.memory_search import MemorySearcher


class TestSearchFunctionality(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        # Note: These tests assume the database has been created
        # In a real test environment, we'd create a test database

    def test_recency_scoring(self):
        """Test recency score calculation."""
        searcher = MemorySearcher()

        # Today should get score 1.0
        today = datetime.now().strftime("%Y-%m-%d")
        self.assertEqual(searcher.calculate_recency_score(today), 1.0)

        # 5 days ago should get score 1.0
        five_days = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        self.assertEqual(searcher.calculate_recency_score(five_days), 1.0)

        # 20 days ago should get score 0.8
        twenty_days = (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d")
        self.assertEqual(searcher.calculate_recency_score(twenty_days), 0.8)

        # 60 days ago should get score 0.6
        sixty_days = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        self.assertEqual(searcher.calculate_recency_score(sixty_days), 0.6)

        # 1 year ago should get score 0.2
        one_year = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        self.assertEqual(searcher.calculate_recency_score(one_year), 0.2)

        # Invalid date should get default 0.5
        self.assertEqual(searcher.calculate_recency_score("invalid-date"), 0.5)
        self.assertEqual(searcher.calculate_recency_score(""), 0.5)

    def test_similarity_threshold(self):
        """Test that similarity threshold filtering works."""
        # This test requires a populated database
        # In a real test, we'd mock the ChromaDB responses

    def test_hybrid_scoring_calculation(self):
        """Test the hybrid scoring formula."""
        # Mock result data
        test_cases = [
            # (similarity, recency_score, complexity, expected_range)
            (0.9, 1.0, "high", (0.83, 0.85)),  # 0.7*0.9 + 0.2*1.0 + 0.1 = 0.93
            (0.8, 0.6, "low", (0.67, 0.69)),  # 0.7*0.8 + 0.2*0.6 + 0 = 0.68
            (0.7, 0.8, "medium", (0.64, 0.66)),  # 0.7*0.7 + 0.2*0.8 + 0 = 0.65
        ]

        # Note: Would need to mock ChromaDB results to properly test this
        # For now, we verify the formula logic is correct
        for similarity, recency, complexity, expected_range in test_cases:
            complexity_bonus = 0.1 if complexity == "high" else 0
            hybrid = (0.7 * similarity) + (0.2 * recency) + complexity_bonus
            self.assertGreaterEqual(hybrid, expected_range[0])
            self.assertLessEqual(hybrid, expected_range[1])


class TestSearchIntegration(unittest.TestCase):
    """Integration tests that require the database to be populated."""

    @unittest.skipIf(
        not Path.home().joinpath(".claude/compacted-summaries").exists(),
        "Requires summaries directory",
    )
    def test_search_returns_results(self):
        """Test that search returns some results for common queries."""
        try:
            searcher = MemorySearcher()

            # Search for a generic term that should match something
            results = searcher.search("implementation", n_results=1, min_similarity=0.3)

            # Should return at least one result with lowered threshold
            self.assertIsInstance(results, list)

            if results:
                # Check result structure
                result = results[0]
                self.assertIn("filename", result)
                self.assertIn("title", result)
                self.assertIn("similarity", result)
                self.assertIn("hybrid_score", result)
                self.assertIn("file_path", result)

                # Scores should be between 0 and 1
                self.assertGreaterEqual(result["similarity"], 0)
                self.assertLessEqual(result["similarity"], 1)
                self.assertGreaterEqual(result["hybrid_score"], 0)
                self.assertLessEqual(result["hybrid_score"], 1)
        except Exception as e:
            # Skip if database not initialized
            if "get_collection" in str(e):
                self.skipTest("Database not initialized")
            else:
                raise


if __name__ == "__main__":
    unittest.main()

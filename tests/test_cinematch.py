"""
tests/test_cinematch.py
Comprehensive automated test suite for CineMatch:
- Database schema and integrity
- OOP models and validation
- DAA algorithms (QuickSort, MergeSort, BinarySearch, LinearSearch)
- Recommendation engine (Exact match, Partial match fallback, Filter relaxation)
- Evaluator system and arithmetic mean verification
"""

import os
import unittest
import numpy as np

from engine.models import Movie, RecommendationCriteria, MatchBreakdown, ScoredMovie
from engine.database import MovieDatabase
from engine.daa_algorithms import quick_sort_movies, merge_sort_movies, binary_search_by_rating, linear_search_by_title
from engine.recommender import RecommendationEngine
from engine.evaluator import EvaluationJudge


class TestCineMatchCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "movies.csv")
        cls.db = MovieDatabase(cls.csv_path)
        cls.recommender = RecommendationEngine(cls.db)
        cls.judge = EvaluationJudge(cls.db, cls.recommender)

    def test_database_loaded_and_valid(self):
        """Test dataset loading, schema verification, and indexing."""
        movies = self.db.movies
        self.assertGreaterEqual(len(movies), 50, "Dataset should have at least 50 movies.")
        
        # Test hash map O(1) retrieval
        movie_1 = self.db.get_by_id(1)
        self.assertIsNotNone(movie_1)
        self.assertTrue(len(movie_1.title) > 0)

        stats = self.db.get_stats()
        self.assertIn("total_movies", stats)
        self.assertIn("avg_rating", stats)
        self.assertGreater(stats["avg_rating"], 7.0)

    def test_movie_model_duration_category(self):
        """Test duration categorization."""
        short_m = Movie(1, "Short", "Comedy", "English", "Happy", 85, 8.0, "Netflix", 2020, "Desc")
        mid_m = Movie(2, "Mid", "Comedy", "English", "Happy", 100, 8.0, "Netflix", 2020, "Desc")
        long_m = Movie(3, "Long", "Comedy", "English", "Happy", 145, 8.0, "Netflix", 2020, "Desc")

        self.assertEqual(short_m.duration_category, "Under 90 minutes")
        self.assertEqual(mid_m.duration_category, "90–120 minutes")
        self.assertEqual(long_m.duration_category, "More than 120 minutes")

    def test_daa_quicksort_and_mergesort(self):
        """Test DAA sorting algorithms (QuickSort & MergeSort) maintain descending order."""
        crit = RecommendationCriteria(mood="Happy", genre="Comedy", duration_range="90–120 minutes", language="English")
        scored = [ScoredMovie(m, self.recommender.calculate_score(m, crit)) for m in self.db.movies[:15]]

        qs_sorted = quick_sort_movies(scored, reverse=True)
        ms_sorted = merge_sort_movies(scored, reverse=True)

        # Verify descending order
        for i in range(len(qs_sorted) - 1):
            self.assertGreaterEqual(qs_sorted[i].score, qs_sorted[i+1].score)

        for i in range(len(ms_sorted) - 1):
            self.assertGreaterEqual(ms_sorted[i].score, ms_sorted[i+1].score)

        # Verify both algorithms sort equivalent sets
        self.assertEqual(len(qs_sorted), len(ms_sorted))

    def test_daa_binary_and_linear_search(self):
        """Test Binary Search on sorted ratings and Linear Search on title."""
        sorted_by_rating = sorted(self.db.movies, key=lambda m: m.rating)
        results = binary_search_by_rating(sorted_by_rating, target_rating=8.4, tolerance=0.1)
        self.assertTrue(len(results) > 0)
        for r in results:
            self.assertAlmostEqual(r.rating, 8.4, delta=0.15)

        # Linear search
        found = linear_search_by_title(self.db.movies, "Spider-Verse")
        self.assertGreaterEqual(len(found), 1)
        self.assertIn("Spider-Man", found[0].title)

    def test_recommender_exact_match(self):
        """Test recommendation engine exact match with 100% adherence."""
        crit = RecommendationCriteria(
            mood="Thoughtful",
            genre="Sci-Fi",
            duration_range="More than 120 minutes",
            language="English"
        )
        res = self.recommender.recommend(crit)
        self.assertTrue(res["has_exact_matches"])
        self.assertGreaterEqual(len(res["exact_matches"]), 1)
        
        # Verify Interstellar or Inception matches
        top_movie = res["exact_matches"][0].movie
        self.assertIn("Sci-Fi", top_movie.genre)
        self.assertEqual(top_movie.language, "English")
        self.assertIn("Thoughtful", top_movie.mood)
        self.assertGreater(top_movie.duration, 120)

    def test_recommender_partial_match_and_relaxation(self):
        """Test zero-exact-match scenario: should NOT fabricate results, must offer relaxation suggestions."""
        # Unlikely exact combo: Emotional Action movie in French under 90 minutes
        crit = RecommendationCriteria(
            mood="Emotional",
            genre="Action",
            duration_range="Under 90 minutes",
            language="French"
        )
        res = self.recommender.recommend(crit)
        
        # Should gracefully report no exact matches
        self.assertFalse(res["has_exact_matches"])
        self.assertEqual(len(res["exact_matches"]), 0)
        
        # Should offer relaxation suggestions
        self.assertGreater(len(res["relaxation_suggestions"]), 0)

    def test_evaluator_judge_system(self):
        """Test judge evaluation criteria scoring and arithmetic mean."""
        evaluation = self.judge.run_full_evaluation()
        self.assertEqual(len(evaluation["evaluations"]), 10)
        self.assertGreaterEqual(evaluation["overall_score"], 8.5)
        self.assertEqual(evaluation["below_eight_count"], 0)

        # Generate scorecard chart test
        fig = self.judge.generate_scorecard_chart(evaluation)
        self.assertIsNotNone(fig)

    def test_sql_database_schema_and_crud(self):
        """Test SQLite RDBMS schema, constraints, B-Tree indexes, and full CRUD operations."""
        sql_db = self.db.sql_db
        self.assertIsNotNone(sql_db)

        # 1. Schema and table verification
        schema = sql_db.get_schema_info()
        self.assertIn("movies", schema)
        self.assertIn("ott_platforms", schema)
        self.assertIn("dbms_audit_log", schema)

        col_names = [c["name"] for c in schema["movies"]["columns"]]
        self.assertIn("movie_id", col_names)
        self.assertIn("rating", col_names)
        self.assertIn("ott_platform", col_names)

        # 2. Count verification
        count = sql_db.get_movie_count()
        self.assertGreaterEqual(count, 50)

        # 3. [C]REATE (INSERT)
        test_id, insert_sql = sql_db.create_movie(
            title="Unit Test SQLite Movie",
            genre="Sci-Fi",
            language="English",
            mood="Excited",
            duration=115,
            rating=8.9,
            ott_platform="Netflix",
            release_year=2025,
            description="Created during automated unit testing of DBMS CRUD.",
            poster_url="https://example.com/poster.jpg"
        )
        self.assertIsNotNone(test_id)
        self.assertIn("INSERT INTO movies", insert_sql)

        # 4. [R]EAD (SELECT)
        movie_row = sql_db.read_movie(test_id)
        self.assertIsNotNone(movie_row)
        self.assertEqual(movie_row["title"], "Unit Test SQLite Movie")
        self.assertEqual(movie_row["rating"], 8.9)

        # 5. [U]PDATE (UPDATE)
        updated, update_sql = sql_db.update_movie(
            movie_id=test_id,
            title="Unit Test SQLite Movie (Updated)",
            genre="Sci-Fi",
            language="English",
            mood="Excited",
            duration=120,
            rating=9.2,
            ott_platform="Prime Video",
            release_year=2025,
            description="Updated during automated unit testing.",
            poster_url="https://example.com/poster.jpg"
        )
        self.assertTrue(updated)
        self.assertIn("UPDATE movies", update_sql)

        movie_after_update = sql_db.read_movie(test_id)
        self.assertEqual(movie_after_update["rating"], 9.2)
        self.assertEqual(movie_after_update["ott_platform"], "Prime Video")

        # 6. [D]ELETE (DELETE)
        deleted, delete_sql = sql_db.delete_movie(test_id)
        self.assertTrue(deleted)
        self.assertIn("DELETE FROM movies", delete_sql)

        movie_after_delete = sql_db.read_movie(test_id)
        self.assertIsNone(movie_after_delete)

        # 7. Audit Log verification
        logs = sql_db.get_audit_logs(limit=10)
        self.assertFalse(logs.empty)
        operations = logs["operation"].tolist()
        self.assertIn("CREATE", operations)
        self.assertIn("UPDATE", operations)
        self.assertIn("DELETE", operations)

        # 8. Custom SQL Console execution
        df, duration_ms, err = sql_db.execute_custom_query(
            "SELECT ott_platform, COUNT(*) as count FROM movies GROUP BY ott_platform HAVING count > 1 ORDER BY count DESC;"
        )
        self.assertIsNone(err)
        self.assertFalse(df.empty)
        self.assertGreater(duration_ms, 0.0)


if __name__ == "__main__":
    unittest.main()


"""
engine/recommender.py
Core recommendation engine implementing multi-criteria filtering,
transparent weighted scoring, partial match fallback with filter relaxation,
and DAA sorting.
"""

import time
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import pandas as pd

from engine.models import Movie, RecommendationCriteria, MatchBreakdown, ScoredMovie
from engine.database import MovieDatabase
from engine.daa_algorithms import quick_sort_movies, merge_sort_movies


class RecommendationEngine:
    """
    Transparent, explainable recommendation engine.
    Applies multi-criteria matching, scoring formula, and DAA sorting algorithms.
    """

    def __init__(self, database: MovieDatabase):
        self.db = database

    @staticmethod
    def check_duration_match(movie_duration: int, duration_range: str) -> bool:
        """Evaluates whether movie duration falls into selected range."""
        range_clean = duration_range.strip().lower()
        if "under 90" in range_clean:
            return movie_duration < 90
        elif "90" in range_clean and "120" in range_clean:
            return 90 <= movie_duration <= 120
        elif "more than 120" in range_clean or ">120" in range_clean or "over 120" in range_clean:
            return movie_duration > 120
        return False

    def calculate_score(self, movie: Movie, criteria: RecommendationCriteria) -> MatchBreakdown:
        """
        Calculates transparent match score:
          - Weights:
            * Genre match: 25%
            * Mood match: 25%
            * Duration match: 25%
            * Language match: 25%
          - Total preference alignment: 0.0 to 1.0 (70% weight of final score)
          - Rating bonus: (rating / 10.0) (30% weight of final score)
          - Final score scaled to 0 - 100%
        """
        target_genre = criteria.genre.strip().lower()
        movie_genres = [g.strip().lower() for g in movie.genre.split(",")]
        genre_m = target_genre in movie_genres

        target_mood = criteria.mood.strip().lower()
        movie_moods = [m.strip().lower() for m in movie.mood.split(",")]
        mood_m = target_mood in movie_moods

        time_m = self.check_duration_match(movie.duration, criteria.duration_range)
        lang_m = (movie.language.strip().lower() == criteria.language.strip().lower())

        # Vectorized / NumPy calculation for weights
        weights = np.array([0.25, 0.25, 0.25, 0.25])
        matches = np.array([genre_m, mood_m, time_m, lang_m], dtype=float)
        pref_ratio = float(np.dot(weights, matches))  # 0.0 to 1.0

        # Weighted combination: 70% preference match + 30% normalized rating
        pref_points = pref_ratio * 70.0
        rating_points = (movie.rating / 10.0) * 30.0
        final_score = round(pref_points + rating_points, 1)

        # Build clear natural language explanation
        explanation_parts = []
        if genre_m and mood_m:
            explanation_parts.append(f"Matches your desired {movie.genre} genre and {movie.mood} mood.")
        elif genre_m:
            explanation_parts.append(f"Delivers on your {movie.genre} genre preference.")
        elif mood_m:
            explanation_parts.append(f"Evokes the {movie.mood} mood you're looking for.")

        if time_m:
            explanation_parts.append(f"Fits perfectly into your time budget ({movie.duration} min).")
        else:
            explanation_parts.append(f"Runs {movie.duration} min ({movie.duration_category}).")

        if lang_m:
            explanation_parts.append(f"Available in {movie.language}.")

        explanation_parts.append(f"Highly rated at {movie.rating}/10 on {movie.ott_platform}.")
        explanation = " ".join(explanation_parts)

        return MatchBreakdown(
            genre_matched=genre_m,
            mood_matched=mood_m,
            time_matched=time_m,
            language_matched=lang_m,
            preference_score=round(pref_points, 1),
            rating_bonus=round(rating_points, 1),
            final_score=final_score,
            explanation=explanation,
        )

    def recommend(
        self, 
        criteria: RecommendationCriteria, 
        sort_algorithm: str = "quick_sort"
    ) -> Dict[str, Any]:
        """
        Executes recommendations:
        1. Validates criteria.
        2. Evaluates all movies across matching dimensions.
        3. Separates exact matches (4/4 criteria) from partial matches.
        4. Sorts candidates using chosen DAA algorithm (quick_sort, merge_sort, or built_in).
        5. Computes filter relaxation suggestions if exact matches are empty.
        """
        start_time = time.perf_counter()

        if not criteria.is_valid():
            raise ValueError("All four preference fields (Mood, Genre, Time, Language) must be selected.")

        all_scored: List[ScoredMovie] = []
        for movie in self.db.movies:
            breakdown = self.calculate_score(movie, criteria)
            all_scored.append(ScoredMovie(movie=movie, breakdown=breakdown))

        # Partition into exact matches and partial matches
        exact_matches = [sm for sm in all_scored if sm.breakdown.is_exact_match]
        # Partial matches: at least 2 criteria match, but not all 4
        partial_candidates = [
            sm for sm in all_scored 
            if not sm.breakdown.is_exact_match and sm.breakdown.matched_count >= 2
        ]

        # Apply DAA sorting
        if sort_algorithm == "quick_sort":
            sorted_exact = quick_sort_movies(exact_matches, key_func=lambda sm: sm.score, reverse=True)
            sorted_partial = quick_sort_movies(partial_candidates, key_func=lambda sm: sm.score, reverse=True)
        elif sort_algorithm == "merge_sort":
            sorted_exact = merge_sort_movies(exact_matches, key_func=lambda sm: sm.score, reverse=True)
            sorted_partial = merge_sort_movies(partial_candidates, key_func=lambda sm: sm.score, reverse=True)
        else:
            sorted_exact = sorted(exact_matches, key=lambda sm: sm.score, reverse=True)
            sorted_partial = sorted(partial_candidates, key=lambda sm: sm.score, reverse=True)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)

        # Generate intelligent filter relaxation suggestions if 0 exact matches
        relaxation_suggestions = []
        if not sorted_exact:
            # Check how many match language alone
            lang_matches = [m for m in self.db.movies if m.language.lower() == criteria.language.lower()]
            genre_matches = [m for m in self.db.movies if m.genre.lower() == criteria.genre.lower()]
            time_matches = [m for m in self.db.movies if self.check_duration_match(m.duration, criteria.duration_range)]
            mood_matches = [m for m in self.db.movies if m.mood.lower() == criteria.mood.lower()]

            if len(time_matches) < 5:
                relaxation_suggestions.append(f"Consider selecting a different time bracket (only {len(time_matches)} movies fit '{criteria.duration_range}').")
            if len(lang_matches) < 5:
                relaxation_suggestions.append(f"Broaden your language selection (e.g., try 'English' which has {len([m for m in self.db.movies if m.language.lower() == 'english'])} titles).")
            if len(genre_matches) < 3:
                relaxation_suggestions.append(f"Try exploring related genres such as Drama or Comedy.")
            if not relaxation_suggestions:
                relaxation_suggestions.append("Try relaxing the duration constraint to '90–120 minutes' or switching mood.")

        # Curate a generous recommendations list:
        # All exact matches first, supplemented with top partial matches up to 8 movies
        curated_recommendations = list(sorted_exact)
        seen_ids = {sm.movie.movie_id for sm in curated_recommendations}
        for sm in sorted_partial:
            if len(curated_recommendations) >= 8:
                break
            if sm.movie.movie_id not in seen_ids:
                curated_recommendations.append(sm)
                seen_ids.add(sm.movie.movie_id)

        return {
            "criteria": criteria,
            "has_exact_matches": len(sorted_exact) > 0,
            "exact_matches": sorted_exact,
            "partial_matches": sorted_partial[:8],
            "curated_recommendations": curated_recommendations,
            "total_exact_count": len(sorted_exact),
            "total_partial_count": len(sorted_partial),
            "total_curated_count": len(curated_recommendations),
            "relaxation_suggestions": relaxation_suggestions,
            "execution_time_ms": elapsed_ms,
            "algorithm_used": sort_algorithm,
        }


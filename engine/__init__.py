"""
engine package initialization
"""
from engine.models import Movie, RecommendationCriteria, MatchBreakdown, ScoredMovie
from engine.database import MovieDatabase
from engine.daa_algorithms import quick_sort_movies, merge_sort_movies, binary_search_by_rating, linear_search_by_title
from engine.recommender import RecommendationEngine
from engine.evaluator import EvaluationJudge

__all__ = [
    "Movie",
    "RecommendationCriteria",
    "MatchBreakdown",
    "ScoredMovie",
    "MovieDatabase",
    "quick_sort_movies",
    "merge_sort_movies",
    "binary_search_by_rating",
    "linear_search_by_title",
    "RecommendationEngine",
    "EvaluationJudge",
]

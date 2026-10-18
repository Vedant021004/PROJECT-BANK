"""
engine/models.py
Object-Oriented Data Models for CineMatch
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class Movie:
    """
    Represents an individual movie record with complete metadata.
    """
    movie_id: int
    title: str
    genre: str
    language: str
    mood: str
    duration: int
    rating: float
    ott_platform: str
    release_year: int
    description: str

    @property
    def duration_category(self) -> str:
        """Categorizes duration into standard buckets."""
        if self.duration < 90:
            return "Under 90 minutes"
        elif 90 <= self.duration <= 120:
            return "90–120 minutes"
        else:
            return "More than 120 minutes"

    def to_dict(self) -> Dict[str, Any]:
        """Convert object to standard dictionary representation."""
        return {
            "movie_id": self.movie_id,
            "title": self.title,
            "genre": self.genre,
            "language": self.language,
            "mood": self.mood,
            "duration": self.duration,
            "rating": self.rating,
            "ott_platform": self.ott_platform,
            "release_year": self.release_year,
            "description": self.description,
            "duration_category": self.duration_category,
        }


@dataclass
class RecommendationCriteria:
    """
    Captures user preferences for filtering and ranking.
    """
    mood: str
    genre: str
    duration_range: str
    language: str

    def is_valid(self) -> bool:
        """Validates that all 4 preferences are populated."""
        return bool(
            self.mood and self.mood.strip() and
            self.genre and self.genre.strip() and
            self.duration_range and self.duration_range.strip() and
            self.language and self.language.strip()
        )


@dataclass
class MatchBreakdown:
    """
    Transparent breakdown of matching dimensions for explainable AI / viva defense.
    """
    genre_matched: bool
    mood_matched: bool
    time_matched: bool
    language_matched: bool
    preference_score: float
    rating_bonus: float
    final_score: float
    explanation: str

    @property
    def matched_count(self) -> int:
        return sum([self.genre_matched, self.mood_matched, self.time_matched, self.language_matched])

    @property
    def is_exact_match(self) -> bool:
        return self.matched_count == 4


@dataclass
class ScoredMovie:
    """
    Pairs a Movie instance with its calculated match breakdown and ranking.
    """
    movie: Movie
    breakdown: MatchBreakdown

    @property
    def score(self) -> float:
        return self.breakdown.final_score

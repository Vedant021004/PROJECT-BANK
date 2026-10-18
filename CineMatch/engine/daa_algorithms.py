"""
engine/daa_algorithms.py
Design and Analysis of Algorithms (DAA) implementations for CineMatch:
- QuickSort (Divide-and-Conquer)
- MergeSort (Stable Divide-and-Conquer)
- BinarySearch (O(log n) search on sorted arrays)
- LinearSearch (O(n) search on unsorted data)

Includes complexity analysis comments and tracking for viva demonstrations.
"""

from typing import List, Callable, Any, Optional, Tuple
from engine.models import ScoredMovie, Movie


def quick_sort_movies(movies: List[ScoredMovie], key_func: Optional[Callable[[ScoredMovie], Any]] = None, reverse: bool = True) -> List[ScoredMovie]:
    """
    DAA Algorithm: QuickSort
    Paradigm: Divide and Conquer
    Time Complexity:
      - Best Case: O(N log N)
      - Average Case: O(N log N)
      - Worst Case: O(N^2) (e.g. when pivot is constantly the minimum/maximum)
    Space Complexity: O(log N) auxiliary call stack

    Sorts a list of ScoredMovie objects using Lomuto partition scheme.
    """
    if key_func is None:
        key_func = lambda item: item.score

    arr = list(movies)
    if len(arr) <= 1:
        return arr

    def _quick_sort(low: int, high: int):
        if low < high:
            p_idx = _partition(low, high)
            _quick_sort(low, p_idx - 1)
            _quick_sort(p_idx + 1, high)

    def _partition(low: int, high: int) -> int:
        pivot_val = key_func(arr[high])
        i = low - 1
        for j in range(low, high):
            current_val = key_func(arr[j])
            condition = (current_val >= pivot_val) if reverse else (current_val <= pivot_val)
            if condition:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1

    _quick_sort(0, len(arr) - 1)
    return arr


def merge_sort_movies(movies: List[ScoredMovie], key_func: Optional[Callable[[ScoredMovie], Any]] = None, reverse: bool = True) -> List[ScoredMovie]:
    """
    DAA Algorithm: MergeSort
    Paradigm: Divide and Conquer (Stable Sort)
    Time Complexity:
      - Best Case: O(N log N)
      - Average Case: O(N log N)
      - Worst Case: O(N log N)
    Space Complexity: O(N) auxiliary memory
    """
    if key_func is None:
        key_func = lambda item: item.score

    if len(movies) <= 1:
        return movies

    mid = len(movies) // 2
    left = merge_sort_movies(movies[:mid], key_func, reverse)
    right = merge_sort_movies(movies[mid:], key_func, reverse)

    return _merge(left, right, key_func, reverse)


def _merge(left: List[ScoredMovie], right: List[ScoredMovie], key_func: Callable, reverse: bool) -> List[ScoredMovie]:
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        val_l = key_func(left[i])
        val_r = key_func(right[j])
        condition = (val_l >= val_r) if reverse else (val_l <= val_r)
        if condition:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def binary_search_by_rating(sorted_movies: List[Movie], target_rating: float, tolerance: float = 0.2) -> List[Movie]:
    """
    DAA Algorithm: Binary Search
    Paradigm: Decrease and Conquer
    Time Complexity: O(log N) to find boundary + O(K) to collect matches
    Space Complexity: O(1)
    
    Assumes sorted_movies is sorted ascending by movie.rating.
    Finds movies with rating in [target_rating - tolerance, target_rating + tolerance].
    """
    if not sorted_movies:
        return []

    low = 0
    high = len(sorted_movies) - 1
    found_idx = -1

    while low <= high:
        mid = (low + high) // 2
        rating = sorted_movies[mid].rating
        if abs(rating - target_rating) <= tolerance:
            found_idx = mid
            break
        elif rating < target_rating:
            low = mid + 1
        else:
            high = mid - 1

    if found_idx == -1:
        return []

    # Expand outward to collect all elements within tolerance
    results = [sorted_movies[found_idx]]
    # Left expansion
    l = found_idx - 1
    while l >= 0 and abs(sorted_movies[l].rating - target_rating) <= tolerance:
        results.append(sorted_movies[l])
        l -= 1
    # Right expansion
    r = found_idx + 1
    while r < len(sorted_movies) and abs(sorted_movies[r].rating - target_rating) <= tolerance:
        results.append(sorted_movies[r])
        r += 1

    return results


def linear_search_by_title(movies: List[Movie], query: str) -> List[Movie]:
    """
    DAA Algorithm: Linear Search
    Paradigm: Brute Force / Direct Scan
    Time Complexity: O(N * M) where N = number of movies, M = string length
    Space Complexity: O(1) auxiliary
    """
    q = query.strip().lower()
    if not q:
        return movies
    return [m for m in movies if q in m.title.lower()]

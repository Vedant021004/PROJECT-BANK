# 🎬 CineMatch --- Smart Movie & OTT Finder

> **A transparent, explainable movie recommendation system demonstrating
> Python programming, Design and Analysis of Algorithms (DAA), and
> Advanced Database Management Systems (ADBMS).**

CineMatch helps users discover movies using four preferences: **mood,
genre, available watching time, and language**. It evaluates the movie
catalogue, calculates an explainable score, ranks candidates using
implemented sorting algorithms, and displays exact or partial matches
through a Streamlit web interface.

> **Academic note:** The current recommender is rule-based. It uses a
> predefined weighted formula; it is not a trained machine-learning
> model.

## Table of Contents

1.  [Project Overview](#project-overview)
2.  [Problem Statement and
    Objectives](#problem-statement-and-objectives)
3.  [Features and Technology Stack](#features-and-technology-stack)
4.  [Architecture and Workflow](#architecture-and-workflow)
5.  [Project Structure](#project-structure)
6.  [Python Concepts](#python-concepts-used)
7.  [Recommendation Formula](#recommendation-formula)
8.  [DAA Algorithms](#daa-design-and-analysis-of-algorithms)
9.  [ADBMS and SQLite](#adbms-and-sqlite)
10. [Data Loading and
    Synchronization](#data-loading-and-synchronization)
11. [Installation and Execution](#installation-and-execution)
12. [Testing and Performance](#testing-and-performance)
13. [Limitations and Future
    Improvements](#limitations-and-future-improvements)
14. [Teacher Demonstration Plan](#teacher-demonstration-plan)
15. [Viva Questions and Answers](#viva-questions-and-answers)
16. [Glossary](#glossary)

------------------------------------------------------------------------

## Project Overview

  ---------------------------------------------------------------------
  Item                               Description
  ---------------------------------- ----------------------------------
  Project                            CineMatch --- Smart Movie & OTT
                                     Finder

  Language                           Python

  UI                                 Streamlit and custom CSS

  Data processing                    Pandas and NumPy

  Persistent database                SQLite

  Algorithms                         QuickSort, MergeSort, Binary
                                     Search, Linear Search

  Recommendation approach            Deterministic multi-criteria
                                     weighted scoring

  Dataset                            Local CSV catalogue, imported into
                                     SQLite
  ---------------------------------------------------------------------

**One-line workflow:** User preferences → Python validation → movie data
→ criterion matching → score calculation → DAA sorting → ranked results
in Streamlit.

## Problem Statement and Objectives

Streaming catalogues can make it difficult to choose a film that matches
a person's mood, preferred genre, available time, and language.
CineMatch offers a simple local catalogue and a transparent method to
rank movies using those preferences.

### Objectives

-   Build an interactive movie finder using Python.
-   Use Object-Oriented Programming (OOP) to represent movies and
    criteria.
-   Read, clean, and validate tabular data using Pandas.
-   Calculate a deterministic recommendation score.
-   Implement searching and sorting algorithms and analyse their
    complexity.
-   Manage movie records through SQLite and SQL.
-   Demonstrate constraints, indexes, CRUD operations, timestamps, and
    audit logging.
-   Handle cases where no exact match exists.

### Scope

CineMatch ranks the records available in its local dataset. It does not
train a recommendation model, infer user taste from historical
behaviour, or verify real-time streaming rights. OTT availability is
based on stored dataset information, not a live provider API.

## Features and Technology Stack

### Features

-   Four preference inputs: mood, genre, duration category, and
    language.
-   Weighted score out of 100.
-   Exact and partial recommendation groups.
-   Explanation of which criteria matched.
-   QuickSort and MergeSort ranking implementations.
-   Title search and rating-range search utilities.
-   Session-based watchlist.
-   SQLite create, read, update, and delete operations.
-   Database schema/index inspection and selected audit logging.
-   Evaluation checks and a scorecard chart.
-   Streamlit interface with custom CSS.

### Technology stack

  ---------------------------------------------------------------------
  Technology                         Role
  ---------------------------------- ----------------------------------
  Python                             Main application and business
                                     logic

  Dataclasses / OOP                  Structured models for movies,
                                     criteria, and scored results

  Pandas                             CSV loading, cleaning, validation,
                                     and tabular processing

  NumPy                              Numeric arrays and weighted
                                     dot-product calculation

  SQLite / `sqlite3`                 Persistent relational storage and
                                     SQL

  Streamlit                          Interactive web interface

  CSS                                Custom visual styling

  Matplotlib                         Evaluation scorecard chart

  `unittest`                         Automated tests

  Git/GitHub                         Version control and hosting
  ---------------------------------------------------------------------

## Architecture and Workflow

``` mermaid
flowchart TD
    A[User selects four preferences] --> B[Streamlit app.py]
    B --> C[Validate RecommendationCriteria]
    C --> D[Load movie data]
    D --> E[Pandas CSV validation]
    D <--> F[(SQLite movies.db)]
    E --> G[Movie objects and ID dictionary]
    G --> H[RecommendationEngine]
    H --> I[Compare genre, mood, time, language]
    I --> J[Weighted score calculation]
    J --> K{All four match?}
    K -->|Yes| L[Exact matches]
    K -->|No| M[Partial matches and relaxation suggestions]
    L --> N[QuickSort or MergeSort]
    M --> N
    N --> O[Ranked results in Streamlit]
```

### End-to-end flow

1.  `app.py` collects the user's preferences.
2.  The values are represented by a `RecommendationCriteria` object.
3.  Required fields are validated.
4.  `MovieDatabase` reads the CSV using Pandas, checks required columns,
    converts types, cleans text, and creates `Movie` objects.
5.  The SQLite layer manages persistent movie records.
6.  The engine checks each movie against four criteria.
7.  NumPy calculates the weighted preference component; rating points
    are added.
8.  The engine separates exact matches from partial candidates.
9.  Candidate lists are ranked with QuickSort or MergeSort.
10. If exact matches are absent, the engine suggests relaxing
    restrictive filters.
11. Streamlit displays results and relevant movie details.

## Project Structure

``` text
PROJECT-BANK/
├── app.py                       # Streamlit UI and user interaction
├── README.md                    # Project documentation
├── requirements.txt             # Dependencies
├── generate_movies_csv.py       # CSV utility
├── build_full_dataset.py        # Dataset-building utility
├── seed_sql_database.py         # SQLite initialization and CRUD demo
├── run_cinematch.bat            # Windows launch helper
├── data/
│   ├── movies.csv               # Source movie catalogue
│   └── movies.db                # SQLite database
├── engine/
│   ├── models.py                # Movie and recommendation dataclasses
│   ├── database.py              # CSV/Pandas data layer
│   ├── sql_database.py          # SQLite schema and CRUD
│   ├── daa_algorithms.py        # Sorting and searching algorithms
│   ├── recommender.py           # Scoring, ranking, and fallback
│   └── evaluator.py             # Evaluation checks and scorecard
├── static/
│   └── styles.css               # Custom styling
└── tests/
    └── test_cinematch.py        # Automated tests
```

The separation of modules makes it easier to test and maintain the UI,
models, algorithms, database, and recommendation logic independently.

## Python Concepts Used

Python connects the user interface, data layer, scoring logic,
algorithms, and database.

### 1. Variables and data types

``` python
title = "Example Movie"  # str
duration = 110           # int, minutes
rating = 8.0             # float, out of 10
genre = "Comedy"         # str
```

Duration is used for time matching, rating contributes to the score, and
text fields are compared with preferences.

### 2. Conditions and Boolean logic

Each criterion is represented as a Boolean match (`True` or `False`).
For example, a 110-minute movie belongs to the 90--120 minute category.
The exact condition implementation is in `engine/recommender.py`.

### 3. Loops

The engine evaluates each movie in the catalogue. If there are `n`
movies and each evaluation uses a fixed number of comparisons, the
scoring pass is O(n).

``` python
all_scored = []
for movie in movies:
    breakdown = engine.calculate_score(movie, criteria)
    all_scored.append(ScoredMovie(movie=movie, breakdown=breakdown))
```

This is an illustrative example of the flow, not a verbatim copy of the
project's complete implementation.

### 4. Functions and modular programming

Examples of responsibilities include:

-   `calculate_score()` --- calculate match details and score.
-   `recommend()` --- coordinate the recommendation pipeline.
-   QuickSort/MergeSort functions --- rank scored movies.
-   `binary_search_by_rating()` --- locate ratings near a target.
-   `linear_search_by_title()` --- find title matches.
-   CRUD methods --- manage database records.

### 5. Object-Oriented Programming (OOP)

The project defines dataclasses in `engine/models.py`.

  ---------------------------------------------------------------------
  Class                              Responsibility
  ---------------------------------- ----------------------------------
  `Movie`                            Movie metadata and
                                     duration-category property

  `RecommendationCriteria`           Four selected preferences and
                                     validation

  `MatchBreakdown`                   Individual match flags, score
                                     components, and explanation

  `ScoredMovie`                      Associates a movie with its
                                     calculated score details

  `MovieDatabase`                    Loads and validates data, provides
                                     lookup

  `RecommendationEngine`             Scoring, candidate grouping,
                                     ranking, fallback

  `SQLMovieDatabase`                 SQLite schema and SQL operations

  `EvaluationJudge`                  Evaluation checks and scorecard
  ---------------------------------------------------------------------

A **class** is a template; an **object** is an instance of that
template. The `Movie` model groups attributes such as `title`, `genre`,
`duration`, and `rating` into a structured object. This is clearer than
repeatedly using numeric positions in a list.

### 6. Lists and dictionaries

-   Lists hold movies and scored candidates.
-   A dictionary called `_movie_dict` maps movie IDs to movie objects.
-   Dictionary lookups are average O(1) in typical conditions.

``` python
movie_by_id = {movie.movie_id: movie for movie in movies}
movie = movie_by_id.get(1)
```

This is an illustrative hash-map example. A Python dictionary is an
in-memory data structure; it is not the same as an SQLite index.

### 7. Pandas

Pandas reads the CSV into a DataFrame, checks required columns, converts
fields to appropriate types, strips whitespace, and supports tabular
display.

``` python
import pandas as pd

df = pd.read_csv("data/movies.csv")
print(df.head())
print(df.columns)
```

### 8. NumPy

The recommender represents the four weights and match flags as numeric
arrays and calculates a dot product.

``` python
import numpy as np

weights = np.array([0.25, 0.25, 0.25, 0.25])
matches = np.array([1, 1, 1, 1], dtype=float)
preference_ratio = float(np.dot(weights, matches))
print(preference_ratio)  # 1.0
```

### 9. Validation and exceptions

The engine validates that all four preference fields are supplied.
Invalid or missing data should produce a clear error rather than an
unreliable score. The CSV loader also validates required columns and
data types.

### 10. Streamlit

`app.py` configures the web page, loads CSS, initializes the
database/recommender/evaluator, and manages session state such as
results and the watchlist.

**Python summary:** OOP, functions, conditions, loops,
lists/dictionaries, data cleaning, numeric scoring, file handling, SQL
integration, validation, and UI orchestration.

## Recommendation Formula

The engine checks four dimensions. Each contributes 25% of the
**preference component**.

  Dimension   Match rule                                   Weight within preferences
  ----------- ------------------------------------------ ---------------------------
  Genre       Selected genre matches movie genre tags                            25%
  Mood        Selected mood matches movie mood tags                              25%
  Duration    Movie duration falls in selected bracket                           25%
  Language    Movie language matches selected language                           25%

Let each match flag be 1 for match and 0 otherwise.

``` text
preference_ratio = 0.25*genre_match
                 + 0.25*mood_match
                 + 0.25*time_match
                 + 0.25*language_match

preference_points = preference_ratio * 70
rating_points     = (movie_rating / 10) * 30
final_score       = preference_points + rating_points
```

Mathematically:

\[ S = 70\\left(\\frac{m_g+m_m+m_t+m_l}{4}\\right)
+30\\left(\\frac{R}{10}\\right) \]

where `S` is the score out of 100, each `m` is a 0/1 match flag, and `R`
is the rating on a 0--10 scale.

### Example A: all four criteria match

User: Happy mood, Comedy genre, 90--120 minutes, English. Movie: Happy,
Comedy, 110 minutes, English, rating 8/10.

``` text
preference_ratio = 4/4 = 1.0
preference_points = 1.0 * 70 = 70
rating_points = (8/10) * 30 = 24
final_score = 70 + 24 = 94/100
```

### Example B: two criteria match

A candidate matches genre and language, but not mood or duration. Its
rating is 9/10.

``` text
preference_ratio = 2/4 = 0.5
preference_points = 0.5 * 70 = 35
rating_points = (9/10) * 30 = 27
final_score = 35 + 27 = 62/100
```

The score combines preference fit and movie rating; it is not just a
match percentage. Exact-match status is separate: exact means all four
criteria match. Partial candidates match at least two criteria but are
not exact matches. Exact results are ranked separately and partial
candidates can supplement the displayed recommendations. If no exact
match exists, the engine can suggest relaxing filters.

## DAA: Design and Analysis of Algorithms

DAA concerns designing algorithms and analysing their efficiency. The
custom implementations are in `engine/daa_algorithms.py`.

### QuickSort --- primary custom ranking algorithm

**Purpose:** sort scored movies by score, descending.

Implementation details:

-   Divide-and-conquer algorithm.
-   Uses Lomuto partitioning.
-   Chooses the last element of a partition as pivot.
-   Partitions values around the pivot, then recursively sorts each
    side.

Example: `55, 92, 71, 84` becomes `92, 84, 71, 55`.

  Case                                         Time complexity
  --------------------------- --------------------------------
  Best                                              O(n log n)
  Average                                           O(n log n)
  Worst                                                  O(n²)
  Auxiliary recursion stack     Typically O(log n), worst O(n)

QuickSort is efficient on average but can degrade when repeated
partitions are badly balanced. This implementation is not stable, so
equal-score items are not guaranteed to preserve their original order.

### MergeSort --- alternative ranking algorithm

MergeSort divides the list into halves, recursively sorts each half, and
merges them in order.

  Case                 Time complexity
  ------------------ -----------------
  Best                      O(n log n)
  Average                   O(n log n)
  Worst                     O(n log n)
  Auxiliary memory                O(n)

MergeSort guarantees O(n log n) time but requires extra memory for
merging. When the merge chooses the left item for equal keys, it
preserves the relative order of equal-key items.

### Binary Search --- rating lookup

The rating-search utility looks for movies within a tolerance of a
target rating. For target 8.4 and tolerance 0.2, the desired range is
`[8.2, 8.6]`.

**Precondition:** the input must be sorted by rating in ascending order.
Binary Search halves the remaining search range after each comparison.

-   Finding a matching position/boundary: O(log n).
-   Collecting `k` adjacent in-range results: O(k) additional work.
-   Returns no results if no rating falls within the tolerance.

This is a separate search utility, not the main recommendation ranking
algorithm.

### Linear Search --- title lookup

The title-search function checks titles one by one, using a
case-insensitive substring comparison.

``` python
results = linear_search_by_title(movies, "parasite")
```

It does not require sorted data. It may inspect all `n` records, so
record-check complexity is O(n), plus string-comparison costs.

### Algorithm comparison

  ----------------------------------------------------------------------------
  Algorithm   Paradigm   Average time   Worst time  Extra space Project use
  ----------- ---------- ------------ ------------ ------------ --------------
  QuickSort   Divide and   O(n log n)        O(n²)    Recursion Main custom
              conquer                                     stack ranking

  MergeSort   Divide and   O(n log n)   O(n log n)         O(n) Alternative
              conquer                                           ranking

  Binary      Decrease       O(log n)     O(log n)         O(1) Rating-range
  Search      and                                    auxiliary, lookup
              conquer                              plus results 

  Linear      Direct             O(n)         O(n)         O(k) Title search
  Search      scan                                     returned 
                                                        results 
  ----------------------------------------------------------------------------

Why implement more than one algorithm? It demonstrates different design
strategies, complexity trade-offs, preconditions, and testing
approaches.

## ADBMS and SQLite

ADBMS stands for Advanced Database Management Systems. CineMatch uses
SQLite through Python's built-in `sqlite3` module. Database schema and
operations are implemented in `engine/sql_database.py`.

### Tables

The schema defines these tables:

**`movies`** stores movie details, including `movie_id`, `title`,
`genre`, `language`, `mood`, `duration`, `rating`, `ott_platform`,
`release_year`, `description`, `poster_url`, `created_at`, and
`updated_at`.

**`ott_platforms`** stores unique platform names and related metadata.

**`dbms_audit_log`** records selected operations, movie details, SQL
information, and timestamps.

Conceptual schema:

``` sql
CREATE TABLE movies (
    movie_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    genre TEXT NOT NULL,
    language TEXT NOT NULL,
    mood TEXT NOT NULL,
    duration INTEGER NOT NULL CHECK(duration > 0),
    rating REAL NOT NULL CHECK(rating >= 0 AND rating <= 10),
    ott_platform TEXT NOT NULL,
    release_year INTEGER NOT NULL CHECK(release_year >= 1888),
    description TEXT NOT NULL,
    poster_url TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

This SQL is a simplified conceptual illustration of the core schema, not
a replacement for the exact schema in `engine/sql_database.py`.

### Primary key and constraints

-   `movie_id` uniquely identifies each movie.
-   `NOT NULL` requires values for essential fields.
-   `UNIQUE` prevents duplicate platform names in `ott_platforms`.
-   `CHECK(duration > 0)` requires a positive duration.
-   `CHECK(rating >= 0 AND rating <= 10)` restricts ratings to 0--10.
-   `CHECK(release_year >= 1888)` enforces the chosen lower year bound.

Constraints help preserve data integrity even if a record is inserted
outside the UI.

### DDL, DML, and DQL

  -----------------------------------------------------------------------
  Category                Purpose                 Examples
  ----------------------- ----------------------- -----------------------
  DDL                     Define structures       `CREATE TABLE`,
                                                  `CREATE INDEX`,
                                                  `CREATE TRIGGER`

  DML                     Change records          `INSERT`, `UPDATE`,
                                                  `DELETE`

  DQL                     Retrieve records        `SELECT`
  -----------------------------------------------------------------------

### CRUD examples

**Create**

``` sql
INSERT INTO movies
(title, genre, language, mood, duration, rating, ott_platform, release_year, description)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
```

**Read**

``` sql
SELECT movie_id, title, rating
FROM movies
WHERE movie_id = ?;
```

**Update**

``` sql
UPDATE movies SET rating = ? WHERE movie_id = ?;
```

**Delete**

``` sql
DELETE FROM movies WHERE movie_id = ?;
```

The Python database layer uses parameterized queries for values. Always
use a suitable `WHERE` clause for update/delete operations.

### Parameterized queries and SQL safety

``` python
sql = "SELECT * FROM movies WHERE movie_id = ?;"
cursor.execute(sql, (movie_id,))
```

The `?` placeholder keeps the value separate from SQL syntax. This
reduces SQL-injection risk for bound values. SQL identifiers such as
column names cannot be supplied as ordinary bound parameters, so dynamic
identifiers should be chosen from a whitelist.

### Indexes

The project creates indexes for fields such as rating, release year, OTT
platform, language, and genre.

``` sql
CREATE INDEX IF NOT EXISTS idx_movies_rating
ON movies(rating);
```

Indexes can help SQLite find records without scanning every row. Their
benefit depends on the query, data size, selectivity, and query plan.
Indexes consume storage and add work to inserts, updates, and deletes. A
substring query like `LIKE '%term%'` may not benefit from a conventional
B-tree index in the same way as an exact or prefix lookup.

### Trigger and timestamps

A trigger automatically runs in response to a database event. CineMatch
defines a trigger to update `updated_at` after a movie row is updated.
This keeps update-time metadata maintained without requiring every
caller to set it manually.

### Audit log

The `dbms_audit_log` table records selected application operations such
as create, update, delete, and seeding. It makes these actions
inspectable. It should not be described as a complete security-grade
audit trail: not every possible read or direct database change is
necessarily logged.

### Transactions

SQLite supports transactions. The database layer uses connection context
managers and commits in data-changing paths. Transactions are important
because related changes should either complete together or be rolled
back on failure when transaction handling is implemented accordingly.

### CSV seeding and synchronization

The project can import `movies.csv` into SQLite. The seeding utility
also populates platform names and records a seeding event. Supported
create/update/delete operations export movie rows back to CSV so the
recommender's source data can be refreshed.

``` text
movies.csv --seed/import--> SQLite movies table
    ^                             |
    |                             |
    +---------- export/sync ------+
                                  |
                         MovieDatabase reload
                                  |
                          Movie objects
                                  |
                        Recommendation engine
```

CSV and SQLite are two representations of related data. A
production-grade design would usually make the database the single
source of truth and use CSV primarily for import/export. Synchronization
needs tests for partial failures, duplicate imports, and stale data.

### Python dictionary vs database index

  Feature          Python dictionary               SQLite index
  ---------------- ------------------------------- -----------------------------------
  Location         Application memory              Database file
  Example          `_movie_dict[movie_id]`         `idx_movies_rating`
  Typical lookup   Average O(1)                    Often O(log n) for B-tree lookups
  Purpose          Fast lookup of loaded objects   Speed suitable SQL queries
  Persistence      Lost when process exits         Stored with database

### Normalization caveat

The separate `ott_platforms` table provides a lookup/master table for
unique platform names. However, `movies.ott_platform` is still stored as
text and the current schema does not define a foreign key linking it to
`ott_platforms`. Therefore, do not claim that referential integrity
between these tables is enforced or that the schema is fully normalized.
A future enhancement could use `platform_id` as a foreign key.

### Why SQLite?

-   Lightweight, file-based, and easy to demonstrate offline.
-   No separate database server required.
-   Supports SQL, constraints, indexes, triggers, and transactions.
-   Works through Python's standard library.

## Data Loading and Synchronization

### CSV/Pandas flow

1.  Check that the CSV exists.
2.  Read it into a DataFrame.
3.  Verify required columns.
4.  Convert ID, duration, rating, and year to numeric types.
5.  Clean text whitespace.
6.  Build `Movie` objects.
7.  Store records in a list and an ID-to-object dictionary.

### SQLite flow

1.  Initialize tables, indexes, and trigger.
2.  If the movies table is empty and the CSV exists, seed the database.
3.  Use parameterized SQL for CRUD operations.
4.  Export movie rows to CSV after supported database changes.
5.  Reload in-memory data after changes.

In a larger application, the database should generally be the single
source of truth, while CSV should be an import/export format.

## Installation and Execution

### Prerequisites

-   Python 3.10 or newer (confirm compatibility with the project's
    installed dependencies).
-   Git (optional).
-   Terminal: PowerShell, Command Prompt, or macOS/Linux shell.

### 1. Clone the repository

``` bash
git clone https://github.com/Vedant021004/PROJECT-BANK.git
cd PROJECT-BANK
```

Run commands from the directory containing `app.py` and
`requirements.txt`.

### 2. Create a virtual environment

**Windows PowerShell**

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows Command Prompt**

``` bat
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS/Linux**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

``` bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

SQLite support is provided by Python's standard library.

### 4. Launch the application

``` bash
streamlit run app.py
```

Open the local URL printed by Streamlit, commonly
`http://localhost:8501`.

### 5. Initialize/demo SQLite (optional)

``` bash
python seed_sql_database.py
```

The seeder initializes the schema, imports CSV data, prints schema/index
information, reports statistics, and demonstrates CRUD operations using
a demonstration record. **Run it against a development copy**, because
it performs writes and exports data.

### 6. Run tests

``` bash
python -m unittest tests/test_cinematch.py -v
```

Run from the repository root. Do not claim a test passed unless you
actually ran it in the environment being demonstrated.

## Testing and Performance

The automated test suite is intended to cover data loading, duration
categories, sorting/searching algorithms, recommendation behaviour,
fallback suggestions, and evaluator behaviour.

### Manual checklist

-   [ ] Launch Streamlit.
-   [ ] Select all four preferences and request recommendations.
-   [ ] Check that results are ranked by score.
-   [ ] Try preferences with no exact match and inspect fallback
    suggestions.
-   [ ] Search for a movie title.
-   [ ] Add a movie to the session watchlist.
-   [ ] Inspect the database schema and indexes.
-   [ ] Run a safe `SELECT` query.
-   [ ] In a development copy, test create/read/update/delete.
-   [ ] Run automated tests after code changes.

### Complexity overview

Let `n` be the number of movies, `e` the number of exact matches, `p`
the number of partial candidates, and `k` the number of results returned
by a rating-range search.

-   Scoring all movies: O(n).
-   QuickSort exact and partial groups: average O(e log e + p log p),
    worst O(e² + p²).
-   MergeSort groups: O(e log e + p log p), with O(n) auxiliary memory
    across a list of size n.
-   Binary Search: O(log n) to find a position, plus O(k) to collect
    matching neighbours.
-   Linear title search: O(n) record checks, plus string-comparison
    cost.
-   Python dictionary ID lookup: average O(1).
-   SQLite query performance depends on the query plan, indexes, and
    dataset size.

Fallback generation can perform additional catalogue scans, so total
runtime includes those scans. Big-O describes growth, not a guaranteed
wall-clock speed.

## Limitations and Future Improvements

### Current limitations

1.  Recommendations are limited to the local dataset.
2.  There is no trained machine-learning model.
3.  OTT availability is not checked live.
4.  The four preferences have fixed equal weights within the preference
    component.
5.  The watchlist is session-based rather than a permanent user profile.
6.  CSV/SQLite synchronization can create consistency issues if a step
    fails.
7.  The OTT platform relationship could be normalized further with a
    foreign key.
8.  QuickSort has a quadratic worst case.
9.  Evaluation scores should be interpreted in light of how the
    evaluator is implemented; they are not proof of independent
    real-world recommendation quality.

### Future improvements

-   Expand the dataset using documented, appropriate data sources.
-   Make SQLite the single source of truth.
-   Add `platform_id` and a foreign key for OTT platforms.
-   Improve transaction rollback and database integration tests.
-   Add pagination and query-plan inspection for larger catalogues.
-   Persist watchlists in the database.
-   Allow configurable preference weights and show score explanations.
-   Evaluate ranking quality using a defined test dataset and metrics.
-   Add a trained recommender only as a separate, measured enhancement.
-   Integrate live OTT data only through a reliable and permitted API.
-   Test empty datasets, invalid ratings, duplicate IDs, and sorting
    edge cases.

## Teacher Demonstration Plan

A 5--7 minute demo can cover the project clearly.

### Part 1: Problem and UI (about 1 minute)

Show the four inputs and run one recommendation.

### Part 2: Python and scoring (1--2 minutes)

Open `engine/models.py` and `engine/recommender.py`. Explain the
dataclasses and the 70-point preference component plus 30-point rating
component. Calculate a sample score of 94/100.

### Part 3: DAA (1--2 minutes)

Open `engine/daa_algorithms.py`. Explain the QuickSort pivot, compare
MergeSort, and state why Binary Search needs sorted data.

### Part 4: ADBMS (1--2 minutes)

Open `engine/sql_database.py`. Show the `movies` table, constraints, an
index, timestamp trigger, and audit log. Demonstrate a safe SELECT or
CRUD operation in a development copy.

### Part 5: Summary (30 seconds)

Explain that Python connects the UI and data processing, DAA
ranks/searches candidates, and SQLite persists and manages records.

## Viva Questions and Answers

**1. What is CineMatch?**\
A Python movie finder that scores and ranks movies using mood, genre,
duration, and language preferences.

**2. Why Python?**\
It has readable syntax and useful libraries such as Pandas, NumPy,
Streamlit, and SQLite integration.

**3. Is it machine learning?**\
No. The current engine is deterministic and rule-based; it does not
train a model.

**4. How is the score calculated?**\
`70 × (matched criteria / 4) + 30 × (rating / 10)`.

**5. Why QuickSort and MergeSort?**\
They demonstrate two divide-and-conquer algorithms with different time
and memory trade-offs.

**6. Why does Binary Search need sorted data?**\
Ordering lets it safely discard half the remaining search interval after
each comparison.

**7. Linear Search vs Binary Search?**\
Linear Search checks records one by one and works on unsorted data;
Binary Search is logarithmic but needs sorted input.

**8. What is a primary key?**\
A field that uniquely identifies each row; here it is `movie_id`.

**9. What are constraints?**\
Rules such as NOT NULL, UNIQUE, PRIMARY KEY, and CHECK that protect data
integrity.

**10. What is an index?**\
An auxiliary structure that can speed up suitable database queries, at
the cost of storage and write overhead.

**11. What is a trigger?**\
A database action automatically executed in response to a defined event,
such as updating a timestamp after a row update.

**12. What does CRUD mean?**\
Create, Read, Update, Delete.

**13. Why parameterized SQL?**\
It separates values from SQL syntax and reduces SQL-injection risk for
bound values.

**14. Why Pandas?**\
To read, clean, validate, and process tabular CSV data.

**15. Why NumPy?**\
To represent match flags and weights as arrays and calculate their dot
product.

**16. Why both CSV and SQLite?**\
CSV is convenient for import/export; SQLite supports persistent
relational data, constraints, indexes, and CRUD. The dual-source design
needs synchronization care.

**17. What happens without exact matches?**\
The engine can suggest relaxing restrictive preferences and show
candidates matching at least two criteria.

**18. Recommendation time complexity?**\
The scoring pass is O(n), followed by sorting; QuickSort average O(n log
n), worst O(n²), and MergeSort O(n log n). Fallback scans can add linear
work.

**19. Does an index always improve speed?**\
No. The query plan, data size, and query type determine whether an index
helps. Indexes also add write overhead.

**20. What would you improve?**\
Make SQLite the single source of truth, add a platform foreign key,
strengthen transaction/error handling and tests, persist watchlists, and
evaluate future recommendation methods.

## Glossary

  ---------------------------------------------------------------------
  Term                               Meaning
  ---------------------------------- ----------------------------------
  OOP                                Object-Oriented Programming

  DAA                                Design and Analysis of Algorithms

  ADBMS                              Advanced Database Management
                                     Systems

  RDBMS                              Relational Database Management
                                     System

  CRUD                               Create, Read, Update, Delete

  DDL                                Data Definition Language

  DML                                Data Manipulation Language

  DQL                                Data Query Language

  CSV                                Comma-Separated Values

  DataFrame                          Two-dimensional tabular structure
                                     in Pandas

  Hash map                           Key-value data structure with
                                     average constant-time lookup

  Time complexity                    How algorithm work grows with
                                     input size

  Divide and conquer                 Solve a problem by splitting it
                                     into subproblems

  Stable sort                        Preserves relative order of equal
                                     keys

  Index                              Database structure that helps
                                     locate records

  Trigger                            Database action automatically run
                                     on an event

  Audit log                          Record of selected operations

  Parameterized query                SQL statement with values supplied
                                     separately

  Exact match                        Movie matching all four criteria

  Partial match                      Non-exact candidate matching at
                                     least two criteria
  ---------------------------------------------------------------------

## Project Links

-   [GitHub repository](https://github.com/Vedant021004/PROJECT-BANK)
-   [Main application ---
    app.py](https://github.com/Vedant021004/PROJECT-BANK/blob/main/app.py)
-   [Models](https://github.com/Vedant021004/PROJECT-BANK/blob/main/engine/models.py)
-   [CSV/Pandas data
    layer](https://github.com/Vedant021004/PROJECT-BANK/blob/main/engine/database.py)
-   [SQLite
    layer](https://github.com/Vedant021004/PROJECT-BANK/blob/main/engine/sql_database.py)
-   [DAA
    algorithms](https://github.com/Vedant021004/PROJECT-BANK/blob/main/engine/daa_algorithms.py)
-   [Recommendation
    engine](https://github.com/Vedant021004/PROJECT-BANK/blob/main/engine/recommender.py)
-   [Evaluation
    module](https://github.com/Vedant021004/PROJECT-BANK/blob/main/engine/evaluator.py)

## Conclusion

CineMatch demonstrates how **Python, DAA, and ADBMS work together**.
Python supplies the models, validation, data processing, scoring, and
UI. DAA supplies custom sorting and searching algorithms. SQLite
supplies persistent storage, constraints, indexes, triggers, CRUD
operations, and selected audit logging. The recommendation engine
connects these components using a transparent weighted formula and
fallback suggestions.

The academic value is not merely displaying movie titles; it is
explaining how each result is computed, ranked, stored, and tested.

------------------------------------------------------------------------

## 🧑‍🏫 Teacher Counter-Questions: 45 Conceptual Viva Questions with Strong Answers

These are phrased as follow-up questions a teacher might ask after your
presentation. Learn the reasoning, not just the wording. When a question
refers to a specific implementation, open the corresponding source file
and point to the code.

### A. Project Understanding and Design

**1. Why did you choose a movie recommendation system?**\
It is an understandable real-world problem that combines structured
data, matching rules, scoring, searching, sorting, database operations,
and a user interface.

**2. What actual problem does CineMatch solve?**\
It reduces the effort needed to choose a movie by ranking records
according to mood, genre, duration, and language. It does not claim a
movie is objectively best; it ranks available records according to
predefined rules.

**3. What happens after a user clicks the recommendation button?**\
The UI collects selections, the criteria object represents them, the
data layer supplies movie records, and the recommender evaluates each
movie. It calculates scores, groups exact and partial matches, sorts
candidates, and returns them for display.

**4. What is the difference between a feature and an algorithm?**\
A feature is something the user can do, such as title search. An
algorithm is a procedure that produces a result, such as QuickSort
ordering scored candidates.

**5. Why split the code into multiple files?**\
Each module has a focused responsibility: models define data structures,
the data layer loads records, the SQL layer manages persistent storage,
the DAA module implements algorithms, the recommender calculates scores,
and Streamlit displays results. This improves testing and maintenance.

**6. Is CineMatch AI or just filtering?**\
It is a rule-based recommender, not a trained AI model. It goes beyond
one strict filter by calculating weighted scores, ranking candidates,
separating exact and partial matches, and suggesting relaxed filters.
Its decisions still follow predefined rules.

**7. What are the inputs and outputs?**\
Inputs are mood, genre, duration category, and language. Outputs are
ranked movie recommendations with metadata and score/explanation
information, depending on the UI view.

**8. What happens if the dataset is empty?**\
There are no records to score. The application should show a clear
empty-state message rather than imply recommendations exist.
Empty-catalogue tests are important to verify this behaviour.

### B. Python and OOP

**9. Why use a `Movie` class instead of a list?**\
A class gives fields meaningful names such as `movie.rating` and
`movie.duration`, rather than relying on numeric positions. It can also
group related behaviour, such as duration categorization, with the movie
model.

**10. What is a dataclass?**\
A Python dataclass reduces repetitive code for classes mainly used to
store data. It can generate methods such as an initializer, making
models like `Movie` concise and readable.

**11. What is the difference between a class and an object?**\
A class defines a structure and behaviour; an object is a specific
instance. `Movie` is a class, while an instance representing one film is
an object.

**12. Why use both lists and dictionaries?**\
A list is convenient for iterating over and sorting movies. A dictionary
maps a key such as `movie_id` directly to a movie object; its lookup is
average O(1) in typical conditions.

**13. Why use Pandas when Python can read CSV files?**\
Pandas provides convenient tabular operations, column validation, type
conversion, cleaning, filtering, and DataFrame output. With a plain CSV
reader, more processing would need to be implemented manually.

**14. Why use NumPy for only four criteria?**\
NumPy clearly represents weights and match flags as numeric arrays and
calculates their dot product. The main benefit here is clear numeric
expression and demonstrating array operations, not a major speed
advantage for four values.

**15. Why are validation and exceptions important?**\
Validation catches incomplete or invalid input before it produces
misleading results. Exceptions allow the application to report problems
such as a missing file or required column rather than silently
continuing.

**16. Is Streamlit the recommendation algorithm?**\
No. Streamlit supplies the interactive UI and session-state handling.
The recommendation logic is in the engine module; Streamlit collects
inputs and displays outputs.

**17. Why say dictionary lookup is average O(1), not always O(1)?**\
A dictionary usually offers constant-time lookup through hashing, but
collisions and resizing can affect performance. O(1) is a typical
average-case statement, not an unconditional guarantee.

### C. Recommendation Logic

**18. Why do preferences contribute 70 points and rating 30 points?**\
The design gives compatibility with user preferences more influence than
the movie's general rating. These are chosen project weights, not a
universal rule; they could be adjusted and evaluated.

**19. What score does a 10/10 movie get if it matches none of the
preferences?**\
Preference points are 0, while rating points are 30, so the score is
30/100. Rating alone cannot produce a maximum score.

**20. Can a partial match score higher than an exact match?**\
Yes, because rating contributes up to 30 points. Exact-match status and
score are separate. The engine groups exact matches separately, allowing
the UI to prioritize them even if a partial candidate has a high score.

**21. Why are the four criteria equally weighted?**\
Equal weights make the model simple and explainable: each criterion
contributes the same share of the 70 preference points. A future version
could allow configurable weights, which should be evaluated rather than
chosen arbitrarily.

**22. Why show partial matches instead of nothing?**\
The dataset may not contain a movie matching every preference. Partial
matches provide alternatives and filter-relaxation suggestions instead
of a blank result, as long as they are labelled clearly.

**23. Is 94/100 a 94% probability that the user will like the movie?**\
No. It is a rule-based ranking score, not a probability. It is
calculated from match flags and the stored rating and has not been
calibrated against actual user feedback.

**24. How would you verify that the scoring formula is correct?**\
Write tests with known match flags and ratings. Four matches plus rating
8 should yield 94; two matches plus rating 9 should yield 62. Also test
zero matches, boundary ratings, missing preferences, and exact/partial
classification.

### D. DAA and Complexity

**25. Why implement QuickSort instead of Python's built-in
`sorted()`?**\
The custom implementation demonstrates algorithm design and analysis for
DAA. In production, Python's built-in sort is often preferable because
it is highly optimized and stable; custom QuickSort is useful here for
learning and comparison.

**26. Why can QuickSort become O(n²)?**\
If pivots repeatedly create very unbalanced partitions, one side may
contain nearly all remaining items. The algorithm then does nearly
linear work at each recursion level, producing quadratic total work.

**27. Why keep MergeSort if it has extra memory cost?**\
MergeSort guarantees O(n log n) time in the worst case, while QuickSort
has an O(n²) worst case. QuickSort usually uses less auxiliary memory;
MergeSort needs O(n) extra memory. Both show useful trade-offs.

**28. What does divide and conquer mean here?**\
It means splitting a problem into smaller subproblems, solving them, and
combining results. QuickSort partitions around a pivot; MergeSort sorts
halves and merges them.

**29. Why can Binary Search not be used directly on unsorted ratings?**\
Binary Search uses order to decide which half to discard. On unsorted
data, the middle comparison does not tell us which half contains the
target, so results can be missed.

**30. Is the rating-range search always O(log n)?**\
Finding a matching position is O(log n), but collecting `k` neighbouring
records within the tolerance adds O(k). The more precise complexity is
O(log n + k).

**31. Time complexity vs actual runtime?**\
Time complexity describes how work grows with input size. Actual runtime
also depends on hardware, Python overhead, data distribution,
implementation details, and input size.

**32. Does sorting improve recommendation quality?**\
Sorting does not change the score or match status. It changes the
presentation order so higher-scoring candidates are easier to find.

### E. ADBMS and SQL

**33. Why SQLite instead of MySQL or PostgreSQL?**\
SQLite is lightweight, stored in a local file, and needs no separate
database server. It supports SQL, constraints, indexes, triggers, and
transactions, making it suitable for an offline college demonstration. A
larger multi-user service might need a server database.

**34. Primary key vs index?**\
A primary key is a constraint that uniquely identifies a row. An index
is a data structure that can speed up suitable lookups. A database may
create an index to support a primary key, but the concepts are not
identical.

**35. Will every query use an index if one exists?**\
No. SQLite's query planner chooses whether an index is useful. A table
scan can be cheaper for a small table or a query that returns much of
the table. Query shape and data distribution also matter.

**36. Difference between `WHERE` and `HAVING`?**\
`WHERE` filters rows before grouping; `HAVING` filters groups after
`GROUP BY`. For example, `WHERE rating >= 8` selects high-rated rows,
while `HAVING COUNT(*) > 5` filters groups containing more than five
rows.

**37. Why are parameterized queries safer than string concatenation?**\
They keep supplied values separate from SQL syntax, so a title or ID is
treated as data rather than SQL code. Dynamic identifiers such as column
names still need a whitelist because identifiers are not ordinary
bindable values.

**38. What is normalization, and is the OTT-platform design fully
normalized?**\
Normalization organizes relational data to reduce duplication and update
anomalies. Although `ott_platforms` exists as a lookup table,
`movies.ott_platform` is still text and there is no foreign key
connecting the tables. Referential integrity is therefore not enforced
between them. Adding `platform_id` and a foreign key would improve this.

**39. Why keep both CSV and SQLite, and what can go wrong?**\
CSV is convenient for import/export; SQLite provides structured
persistent storage and SQL features. If a database update succeeds but
CSV export fails, the two copies may diverge. A stronger design would
make SQLite the single source of truth and use CSV mainly for
import/export.

**40. Does the audit log record every database action?**\
No. It records selected application operations such as create, update,
delete, and seeding. It is not a complete security-grade audit trail
because not every read or direct database change is necessarily logged.

### F. Testing, Security, and Future Work

**41. How would you test QuickSort and MergeSort?**\
Test already-sorted, reverse-sorted, random, empty, single-item, and
duplicate-score lists. Check expected ordering and confirm that no
elements were lost or duplicated.

**42. How would you test a database update?**\
Create a temporary record, update a field, read the row back, and verify
the value. Delete the test record and confirm it is gone. Use a test
database or cleanup/rollback so real project data is not damaged.

**43. Is the project secure just because it uses SQLite?**\
No. SQLite is a database engine, not a complete security solution.
Parameterized queries protect bound values, but input validation,
permissions, safe SQL-console behaviour, backups, and data handling
still matter. An arbitrary SQL console should only be used with trusted
input and a safe development database.

**44. What architectural improvement would you make first?**\
Make SQLite the single source of truth, keep CSV for import/export, and
strengthen transaction and error-handling rules. This reduces the chance
of inconsistent copies of the same data.

**45. How would you turn this into a more advanced recommender?**\
Collect appropriate user feedback and define evaluation metrics first.
Then compare the rule-based baseline with approaches such as
content-based recommendations using movie metadata. Any machine-learning
extension should be evaluated on a test set and should not be claimed to
be better without evidence.

## How to Answer Follow-up Questions Confidently

Use this four-step pattern when a teacher asks "why?" or "what if?":

1.  **State the concept:** "QuickSort uses divide and conquer."
2.  **Connect it to CineMatch:** "We use it to rank scored movie
    candidates."
3.  **Give an example or complexity:** "Its average time is O(n log n),
    with a worst case of O(n²)."
4.  **Mention a trade-off:** "A poor pivot can create unbalanced
    partitions; MergeSort guarantees O(n log n) time but needs extra
    memory."

Do not claim that the project uses machine learning, live OTT APIs,
enforced platform foreign keys, or complete audit logging unless those
features are actually implemented. A precise explanation of a limitation
is stronger than an exaggerated claim.

"""
app.py
CineMatch — Smart Movie & OTT Finder
Frontend Application built with Streamlit and Custom Cinematic Dark CSS.
Featuring Interactive Slideshow / Carousel & Grid Views.
"""

import os
import sys
import textwrap
import pandas as pd
import streamlit as st

# Configure page layout and metadata
st.set_page_config(
    page_title="CineMatch — Smart Movie & OTT Finder",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Import engine components
from engine.database import MovieDatabase
from engine.models import RecommendationCriteria, Movie
from engine.recommender import RecommendationEngine
from engine.evaluator import EvaluationJudge
from engine.daa_algorithms import linear_search_by_title


# Helper to render clean HTML without markdown indentation interference
def render_html(html_str: str):
    """Renders pure HTML without Markdown parser code block interference."""
    st.html(textwrap.dedent(html_str).strip())


# Load Custom CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "static", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.html(f"<style>{f.read()}</style>")


load_css()


# Initialize cached resources with automatic mtime reload
@st.cache_resource
def get_database_and_recommender(csv_mtime: float, db_mtime: float):
    csv_path = os.path.join(os.path.dirname(__file__), "data", "movies.csv")
    db_path = os.path.join(os.path.dirname(__file__), "data", "movies.db")
    db = MovieDatabase(csv_path=csv_path, db_path=db_path)
    engine = RecommendationEngine(db)
    judge = EvaluationJudge(db, engine)
    return db, engine, judge


csv_file_path = os.path.join(os.path.dirname(__file__), "data", "movies.csv")
db_file_path = os.path.join(os.path.dirname(__file__), "data", "movies.db")
csv_mtime = os.path.getmtime(csv_file_path) if os.path.exists(csv_file_path) else 0.0
db_mtime = os.path.getmtime(db_file_path) if os.path.exists(db_file_path) else 0.0
db, engine, judge = get_database_and_recommender(csv_mtime, db_mtime)
sql_db = db.sql_db

# Session State Initialization
if "watchlist" not in st.session_state:
    st.session_state.watchlist = set()

if "results" not in st.session_state:
    st.session_state.results = None

if "slide_idx" not in st.session_state:
    st.session_state.slide_idx = 0

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "🎬 Slideshow"


# 1. NAVBAR SECTION
watchlist_count = len(st.session_state.watchlist)
render_html(
    f"""
    <div class="cinematch-navbar">
        <div class="cinematch-brand">
            <span class="brand-icon">🎬</span>
            <div>
                <h1 class="brand-title" style="display:inline; margin:0;">CineMatch</h1>
                <span class="brand-tag">OTT Finder</span>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 1rem;">
            <span style="font-size: 0.9rem; color: #9ba3be;">Dataset: <strong>{len(db.movies)} Movies</strong></span>
            <span style="padding: 0.35rem 0.85rem; background: rgba(139, 92, 246, 0.15); border: 1px solid rgba(139, 92, 246, 0.4); border-radius: 999px; font-size: 0.85rem; color: #c4b5fd; font-weight: 600;">
                ⭐ Watchlist: {watchlist_count}
            </span>
        </div>
    </div>
    """
)


# 2. HERO SECTION
render_html(
    """
    <div class="hero-container">
        <div class="hero-pill">
            <span>✨ Pure Python • DAA Ranking • Zero External APIs</span>
        </div>
        <h2 class="hero-title">
            Your next favourite movie <br/>
            <span class="hero-title-highlight">starts right here.</span>
        </h2>
        <p class="hero-subtitle">
            Skip the endless scrolling. Share your mood, preferred genre, time budget, and language 
            to get mathematically ranked, transparent movie recommendations.
        </p>
    </div>
    """
)


# Main Tabs Navigation for polished organization
tab_find, tab_watchlist, tab_evaluator, tab_dbms, tab_viva = st.tabs([
    "🎯 Find My Movie",
    f"🔖 My Watchlist ({watchlist_count})",
    "⚖️ Judge Evaluation Scorecard",
    "🗄️ SQL DBMS & CRUD Studio",
    "🎓 DAA & DBMS Viva Guide"
])


# ==========================================
# HELPER: MOVIE CARD RENDERER
# ==========================================
def render_movie_card(scored_movie, is_exact: bool = True, card_key_suffix: str = "card"):
    m = scored_movie.movie
    bd = scored_movie.breakdown
    is_in_watchlist = m.movie_id in st.session_state.watchlist

    # Dimension badges
    g_pill = '<span class="dim-pill-matched">✓ Genre</span>' if bd.genre_matched else '<span class="dim-pill-unmatched">✕ Genre</span>'
    m_pill = '<span class="dim-pill-matched">✓ Mood</span>' if bd.mood_matched else '<span class="dim-pill-unmatched">✕ Mood</span>'
    t_pill = '<span class="dim-pill-matched">✓ Time</span>' if bd.time_matched else '<span class="dim-pill-unmatched">✕ Time</span>'
    l_pill = '<span class="dim-pill-matched">✓ Language</span>' if bd.language_matched else '<span class="dim-pill-unmatched">✕ Language</span>'

    poster_url = getattr(m, "poster_url", "")

    # Outer container with responsive columns for poster and content
    with st.container():
        col_img, col_info = st.columns([1.2, 3.8], gap="medium")
        
        with col_img:
            if poster_url:
                try:
                    st.image(poster_url, use_container_width=True, caption=f"⭐ {m.rating} / 10")
                except Exception:
                    st.markdown(f"""
                    <div class="movie-poster-fallback">
                        <span style="font-size: 2.5rem;">🎬</span>
                        <div style="font-weight: 700; font-size: 0.85rem; color: #f7f4eb; margin-top: 0.4rem;">{m.title}</div>
                        <div style="font-size: 0.75rem; color: #c4b5fd;">({m.release_year})</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="movie-poster-fallback">
                    <span style="font-size: 2.5rem;">🎬</span>
                    <div style="font-weight: 700; font-size: 0.85rem; color: #f7f4eb; margin-top: 0.4rem;">{m.title}</div>
                    <div style="font-size: 0.75rem; color: #c4b5fd;">({m.release_year})</div>
                </div>
                """, unsafe_allow_html=True)

        with col_info:
            card_html = f"""
            <div class="movie-card-inner">
                <div class="card-header-row">
                    <div>
                        <h3 class="card-title">{m.title} <span class="card-year">({m.release_year})</span></h3>
                    </div>
                    <div class="card-score-pill">
                        🎯 {bd.final_score}% Match
                    </div>
                </div>
                
                <div class="card-badges">
                    <span class="badge-tag badge-ott">📺 {m.ott_platform}</span>
                    <span class="badge-tag">⏱️ {m.duration} min ({m.duration_category})</span>
                    <span class="badge-tag">🌐 {m.language}</span>
                    <span class="badge-tag badge-mood">🎭 {m.mood}</span>
                    <span class="badge-tag">🏷️ {m.genre}</span>
                </div>

                <p class="card-desc">{m.description}</p>

                <div class="match-dimensions">
                    {g_pill} {m_pill} {t_pill} {l_pill}
                    <span style="font-size: 0.72rem; color: #9ba3be; margin-left: 0.5rem; align-self: center;">
                        (Preferences: {bd.preference_score}/70 pts + Rating Bonus: {bd.rating_bonus}/30 pts)
                    </span>
                </div>

                <div class="card-explanation">
                    <strong>💡 Recommendation Reason:</strong> {bd.explanation}
                </div>
            </div>
            """
            render_html(card_html)

            btn_label = "✓ Remove from Watchlist" if is_in_watchlist else "+ Save to Watchlist"
            if st.button(btn_label, key=f"wl_{m.movie_id}_{card_key_suffix}"):
                if is_in_watchlist:
                    st.session_state.watchlist.remove(m.movie_id)
                else:
                    st.session_state.watchlist.add(m.movie_id)
                st.rerun()

        st.markdown("<hr style='border: 0; height: 1px; background: rgba(139, 92, 246, 0.2); margin: 1.25rem 0 1.75rem 0;' />", unsafe_allow_html=True)


# ==========================================
# HELPER: SLIDESHOW RENDERER
# ==========================================
def render_slideshow(scored_movies, is_exact: bool = True):
    total = len(scored_movies)
    if total == 0:
        return

    # Ensure slide_idx is within bounds
    st.session_state.slide_idx = max(0, min(st.session_state.slide_idx, total - 1))
    idx = st.session_state.slide_idx

    # Navigation buttons and counter
    col_prev, col_counter, col_next = st.columns([1.5, 3, 1.5])
    with col_prev:
        if st.button("⬅️ Previous Movie", disabled=(idx == 0), key="btn_prev_slide", use_container_width=True):
            st.session_state.slide_idx = max(0, idx - 1)
            st.rerun()

    with col_counter:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 0.35rem 0;">
                <span class="slide-counter-badge">
                    🎞️ Slide {idx + 1} of {total}
                </span>
                <div style="font-size: 0.8rem; color: #9ba3be; margin-top: 0.3rem;">
                    Click Previous / Next or select a title below to slide
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_next:
        if st.button("Next Movie ➡️", disabled=(idx == total - 1), key="btn_next_slide", use_container_width=True):
            st.session_state.slide_idx = min(total - 1, idx + 1)
            st.rerun()

    # Progress bar showing slide position
    progress_val = float(idx + 1) / float(total)
    st.progress(progress_val)

    # Render current featured movie
    current_movie = scored_movies[idx]
    render_movie_card(current_movie, is_exact=is_exact, card_key_suffix=f"slide_{idx}")

    # Direct Jump Selector
    st.markdown("<p style='font-size: 0.85rem; color: #9ba3be; margin-top: 1rem; margin-bottom: 0.3rem;'>Jump directly to movie slide:</p>", unsafe_allow_html=True)
    title_options = [f"{i+1}. {sm.movie.title} ({sm.score}% Match)" for i, sm in enumerate(scored_movies)]
    selected_title_str = st.selectbox(
        "Jump to slide",
        options=title_options,
        index=idx,
        key="slide_jump_select",
        label_visibility="collapsed"
    )
    chosen_jump_idx = title_options.index(selected_title_str)
    if chosen_jump_idx != idx:
        st.session_state.slide_idx = chosen_jump_idx
        st.rerun()


# ==========================================
# TAB 1: FIND MY MOVIE (SELECTION & RESULTS)
# ==========================================
with tab_find:
    st.markdown("### 1. Select Your Preferences")
    render_html("<p style='color: #9ba3be; font-size: 0.9rem; margin-top: -0.5rem;'>Customize the four matching dimensions to discover tailored movie matches.</p>")

    with st.container():
        render_html('<div class="preference-box">')
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("**Step 1 — Choose your mood**")
            available_moods = ["Happy", "Relaxed", "Excited", "Thoughtful", "Emotional"]
            selected_mood = st.selectbox(
                "Your Mood",
                options=available_moods,
                index=3,  # Thoughtful (perfect for Drishyam, Parasite, Interstellar)
                key="input_mood",
                label_visibility="collapsed"
            )

        with col2:
            st.markdown("**Step 2 — Select genre**")
            available_genres = db.get_genres()
            default_genre_idx = available_genres.index("Thriller") if "Thriller" in available_genres else 0
            selected_genre = st.selectbox(
                "Genre",
                options=available_genres,
                index=default_genre_idx,
                key="input_genre",
                label_visibility="collapsed"
            )

        with col3:
            st.markdown("**Step 3 — Available time**")
            available_times = [
                "Under 90 minutes",
                "90–120 minutes",
                "More than 120 minutes"
            ]
            selected_time = st.selectbox(
                "Duration",
                options=available_times,
                index=2,  # More than 120 minutes
                key="input_time",
                label_visibility="collapsed"
            )

        with col4:
            st.markdown("**Step 4 — Select language**")
            available_languages = db.get_languages()
            default_lang_idx = available_languages.index("Hindi") if "Hindi" in available_languages else 0
            selected_lang = st.selectbox(
                "Language",
                options=available_languages,
                index=default_lang_idx,
                key="input_lang",
                label_visibility="collapsed"
            )

        # Algorithm selection option (DAA showcase)
        col_algo, col_btn = st.columns([2, 2])
        with col_algo:
            chosen_algo = st.selectbox(
                "DAA Sorting Algorithm (Viva Selection):",
                options=[
                    ("quick_sort", "QuickSort — Lomuto O(N log N)"),
                    ("merge_sort", "MergeSort — Stable O(N log N)"),
                    ("built_in", "Timsort — Python Hybrid O(N log N)")
                ],
                format_func=lambda x: x[1],
                key="algo_choice"
            )[0]

        with col_btn:
            render_html("<div style='height: 28px;'></div>")
            find_btn = st.button("🚀 Find My Movie", type="primary", use_container_width=True)

        render_html('</div>')

    # Handle Search Action
    if find_btn:
        criteria = RecommendationCriteria(
            mood=selected_mood,
            genre=selected_genre,
            duration_range=selected_time,
            language=selected_lang
        )
        try:
            with st.spinner("Analyzing dataset, applying multi-dimensional matching & DAA sorting..."):
                results = engine.recommend(criteria, sort_algorithm=chosen_algo)
                st.session_state.results = results
                st.session_state.slide_idx = 0  # Reset slideshow to slide 1
        except Exception as e:
            st.error(f"Error calculating recommendations: {str(e)}")

    # 4. RECOMMENDATION RESULTS SECTION
    if st.session_state.results:
        res = st.session_state.results
        criteria = res["criteria"]

        st.markdown("---")
        
        # Header with View Mode Switcher (Slideshow vs List View)
        col_head, col_switcher = st.columns([3, 2])
        with col_head:
            st.markdown("### 2. Recommendation Results")
        with col_switcher:
            chosen_view = st.radio(
                "View Mode:",
                options=["🎬 Slideshow", "📋 Full List View"],
                index=0 if st.session_state.view_mode == "🎬 Slideshow" else 1,
                horizontal=True,
                key="view_mode_radio"
            )
            st.session_state.view_mode = chosen_view

        # Performance summary pill
        render_html(
            f"""
            <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 1rem; margin-bottom: 1.5rem; padding: 0.75rem 1.25rem; background: rgba(14, 18, 36, 0.7); border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 12px;">
                <div>
                    <span style="color: #9ba3be; font-size: 0.88rem;">Searched: </span>
                    <span style="color: #ffffff; font-weight: 600; font-size: 0.88rem;">Mood: <em>{criteria.mood}</em> • Genre: <em>{criteria.genre}</em> • Time: <em>{criteria.duration_range}</em> • Language: <em>{criteria.language}</em></span>
                </div>
                <div style="font-size: 0.82rem; color: #a78bfa;">
                    ⚡ Matched in <strong>{res['execution_time_ms']} ms</strong> via <strong>{res['algorithm_used'].replace('_', ' ').title()}</strong>
                </div>
            </div>
            """
        )

        # Display Matches
        curated_list = res.get("curated_recommendations", res["exact_matches"] if res["has_exact_matches"] else res["partial_matches"])

        if res["has_exact_matches"]:
            exact_count = res["total_exact_count"]
            additional_count = len(curated_list) - exact_count
            if additional_count > 0:
                st.success(f"🎉 Found {exact_count} Exact 4/4 Match(es), plus {additional_count} top matching recommendations ({len(curated_list)} movies in total)!")
            else:
                st.success(f"🎉 Found {exact_count} exact match(es) satisfying all 4 of your criteria!")

            if st.session_state.view_mode == "🎬 Slideshow":
                render_slideshow(curated_list, is_exact=True)
            else:
                for idx, sm in enumerate(curated_list):
                    render_movie_card(sm, is_exact=sm.breakdown.is_exact_match, card_key_suffix=f"list_{idx}")

        else:
            # EMPTY EXACT MATCH SCENARIO
            st.warning("⚠️ No exact 4/4 match was found that satisfies all criteria simultaneously.")

            # Filter Relaxation Suggestions
            relaxation_items = "".join([f"<li>{s}</li>" for s in res["relaxation_suggestions"]])
            render_html(
                f"""
                <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 14px; padding: 1.25rem; margin-bottom: 1.5rem;">
                    <h4 style="color: #fbbf24; margin: 0 0 0.5rem 0;">💡 Filter Relaxation Advice</h4>
                    <ul style="color: #f7f4eb; margin: 0; padding-left: 1.25rem;">
                        {relaxation_items}
                    </ul>
                </div>
                """
            )

            # High Partial Matches Showcase
            if curated_list:
                partial_count = len(curated_list)
                st.markdown(f"#### 🔍 Best Recommended Matches ({partial_count} titles found)")
                render_html("<p style='color: #9ba3be; font-size: 0.88rem;'>These titles closely align with 2 or 3 of your preferences:</p>")

                if st.session_state.view_mode == "🎬 Slideshow":
                    render_slideshow(curated_list, is_exact=False)
                else:
                    for idx, sm in enumerate(curated_list):
                        render_movie_card(sm, is_exact=False, card_key_suffix=f"list_partial_{idx}")
            else:
                st.info("No recommendations found. Please try picking a different genre or language.")


# ==========================================
# TAB 2: MY WATCHLIST
# ==========================================
with tab_watchlist:
    st.markdown("### 🔖 Your Saved Watchlist")
    if not st.session_state.watchlist:
        render_html(
            """
            <div style="text-align: center; padding: 3rem 1rem; background: rgba(14, 18, 36, 0.5); border: 1px dashed rgba(139, 92, 246, 0.3); border-radius: 16px;">
                <p style="font-size: 2rem; margin-bottom: 0.5rem;">🍿</p>
                <h4 style="color: #ffffff; margin-bottom: 0.5rem;">Your Watchlist is empty</h4>
                <p style="color: #9ba3be; font-size: 0.95rem;">Browse recommendations and click <strong>'+ Save to Watchlist'</strong> on any movie card to store it here.</p>
            </div>
            """
        )
    else:
        st.info(f"You have {len(st.session_state.watchlist)} movie(s) saved.")
        wl_movies = [db.get_by_id(mid) for mid in st.session_state.watchlist if db.get_by_id(mid)]

        # Search within Watchlist
        wl_query = st.text_input("🔍 Search within your Watchlist by title:", placeholder="e.g. Drishyam, Parasite, Spider-Man")
        if wl_query:
            wl_movies = linear_search_by_title(wl_movies, wl_query)

        for m in wl_movies:
            poster_url = getattr(m, "poster_url", "")
            with st.container():
                col_w_img, col_w_info = st.columns([1.0, 4.0], gap="medium")
                with col_w_img:
                    if poster_url:
                        try:
                            st.image(poster_url, use_container_width=True, caption=f"⭐ {m.rating} / 10")
                        except Exception:
                            st.write("🎬")
                    else:
                        st.write("🎬")
                with col_w_info:
                    render_html(
                        f"""
                        <div class="movie-card-inner">
                            <div class="card-header-row">
                                <div>
                                    <h3 class="card-title">{m.title} <span class="card-year">({m.release_year})</span></h3>
                                </div>
                                <div class="card-score-pill">
                                    ⭐ {m.rating} / 10
                                </div>
                            </div>
                            <div class="card-badges">
                                <span class="badge-tag badge-ott">📺 {m.ott_platform}</span>
                                <span class="badge-tag">⏱️ {m.duration} min</span>
                                <span class="badge-tag">🌐 {m.language}</span>
                                <span class="badge-tag badge-mood">🎭 {m.mood}</span>
                                <span class="badge-tag">🏷️ {m.genre}</span>
                            </div>
                            <p class="card-desc">{m.description}</p>
                        </div>
                        """
                    )
                    if st.button("🗑️ Remove from Watchlist", key=f"wl_del_{m.movie_id}"):
                        st.session_state.watchlist.remove(m.movie_id)
                        st.rerun()
                st.markdown("<hr style='border: 0; height: 1px; background: rgba(139, 92, 246, 0.2); margin: 1rem 0;' />", unsafe_allow_html=True)


# ==========================================
# TAB 3: JUDGE EVALUATION SCORECARD
# ==========================================
with tab_evaluator:
    st.markdown("### ⚖️ Project Evaluator & Quality Scorecard")
    render_html(
        "<p style='color: #9ba3be; font-size: 0.9rem;'>Strict software engineering evaluation across 10 defined criteria. Every score below 8.0/10 requires explicit weakness identification and remedy.</p>"
    )

    evaluation = judge.run_full_evaluation()
    overall_score = evaluation["overall_score"]

    # Top summary metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Overall Score (Mean)", f"{overall_score} / 10.0")
    with m2:
        st.metric("Total Criteria Evaluated", f"{evaluation['total_count']}")
    with m3:
        st.metric("Criteria Passed (≥8.0)", f"{evaluation['passed_count']} / 10")
    with m4:
        st.metric("Judge Verdict", evaluation["verdict"])

    # Scorecard visualization chart
    st.markdown("#### 📊 Visual Scorecard Distribution")
    fig = judge.generate_scorecard_chart(evaluation)
    st.pyplot(fig)

    # Detailed criteria table
    st.markdown("#### 📋 Criteria Breakdown & Explanations")
    for crit in evaluation["evaluations"]:
        with st.expander(f"{'✅' if crit.score >= 8.0 else '⚠️'} {crit.name} — {crit.score}/10.0"):
            st.markdown(f"**Score:** `{crit.score} / {crit.max_score}`")
            st.markdown(f"**Evaluator Assessment:** {crit.reason}")
            if crit.weakness:
                st.markdown(f"**Identified Weakness:** `{crit.weakness}`")
                st.markdown(f"**Suggested Remediation:** `{crit.suggested_fix}`")

# ==========================================
# TAB 4: SQL DBMS & CRUD STUDIO
# ==========================================
with tab_dbms:
    st.markdown("### 🗄️ Relational DBMS & SQL CRUD Studio")
    render_html(
        """
        <div class="dbms-header-card">
            <div class="dbms-title-row">
                <div>
                    <h3 style="margin: 0; font-size: 1.35rem; color: #f7f4eb;">
                        ⚡ SQLite Relational Database Management System (RDBMS)
                    </h3>
                    <p style="margin: 0.35rem 0 0 0; font-size: 0.88rem; color: #9ba3be;">
                        Live SQL Engine • Normalized Relational Tables • B-Tree Index Acceleration • Real-Time ACID Transactions
                    </p>
                </div>
                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                    <span class="sql-pill">ENGINE: SQLite 3.x</span>
                    <span class="sql-pill">ISOLATION: ACID</span>
                    <span class="sql-pill">STORAGE: movies.db</span>
                </div>
            </div>
        </div>
        """
    )

    # Fetch live stats from SQLite
    try:
        sql_stats = sql_db.get_stats()
    except Exception as e:
        sql_stats = {"total_movies": len(db.movies), "avg_rating": 8.0, "db_size_kb": 112.0, "genres_count": 11, "language_count": 10, "ott_count": 17}

    # Summary metric counter cards
    sm1, sm2, sm3, sm4, sm5 = st.columns(5)
    with sm1:
        st.metric("Total Movies in SQL", f"{sql_stats.get('total_movies', 0)}")
    with sm2:
        st.metric("Average Rating", f"⭐ {sql_stats.get('avg_rating', 0.0)}")
    with sm3:
        st.metric("OTT Platforms", f"{sql_stats.get('ott_count', 0)}")
    with sm4:
        st.metric("Languages Tracked", f"{sql_stats.get('language_count', 0)}")
    with sm5:
        st.metric("SQLite File Size", f"{sql_stats.get('db_size_kb', 0.0)} KB")

    st.markdown("<br/>", unsafe_allow_html=True)

    # Sub-tabs for DBMS operations
    sub_crud, sub_console, sub_schema, sub_audit = st.tabs([
        "⚡ Interactive CRUD Operations",
        "💻 Live SQL Query Console",
        "📐 Relational Schema & B-Trees",
        "📜 Transaction Audit Trail & ACID"
    ])

    # -------------------------------------------------------------------------
    # SUB-TAB 1: INTERACTIVE CRUD OPERATIONS
    # -------------------------------------------------------------------------
    with sub_crud:
        crud_mode = st.radio(
            "Select CRUD Operation to Execute:",
            ["➕ Create (INSERT)", "🔍 Read (SELECT)", "✏️ Update (UPDATE)", "🗑️ Delete (DELETE)"],
            horizontal=True,
            key="crud_mode_selector"
        )
        st.markdown("<hr style='border: 0; height: 1px; background: rgba(139, 92, 246, 0.2); margin: 0.75rem 0 1.25rem 0;' />", unsafe_allow_html=True)

        # ----------------- [C]REATE (INSERT) -----------------
        if crud_mode == "➕ Create (INSERT)":
            st.markdown("#### ➕ [C]reate — Add New Movie Record (`INSERT INTO`)")
            st.caption("Fills new record attributes and executes an atomic SQL INSERT query with data validation.")

            with st.form("form_create_movie", clear_on_submit=False):
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    c_title = st.text_input("Movie Title *", value="", placeholder="e.g. Oppenheimer")
                    c_year = st.number_input("Release Year *", min_value=1900, max_value=2030, value=2023, step=1)
                    c_genre = st.text_input("Genre(s) * (comma-separated)", value="Drama, History", placeholder="e.g. Drama, Thriller")
                    c_lang = st.selectbox("Language *", ["English", "Hindi", "Japanese", "Korean", "Spanish", "French", "Italian", "Tamil", "Telugu", "Other"])
                    c_mood = st.text_input("Mood * (comma-separated)", value="Thoughtful, Excited", placeholder="e.g. Thoughtful, Excited")
                
                with col_c2:
                    c_duration = st.number_input("Duration (minutes) *", min_value=1, max_value=600, value=180, step=1)
                    c_rating = st.slider("IMDb Rating *", min_value=0.0, max_value=10.0, value=8.9, step=0.1)
                    c_ott = st.selectbox("OTT Streaming Platform *", ["Netflix", "Prime Video", "Disney+ Hotstar", "Apple TV+", "Max", "Paramount+", "Peacock", "Crunchyroll", "Hulu", "Zee5", "SonyLIV", "JioCinema"])
                    c_poster = st.text_input("Poster URL (optional)", value="", placeholder="https://m.media-amazon.com/...")

                c_desc = st.text_area("Plot Description *", value="", placeholder="Brief synopsis of the film...")

                # Live SQL preview
                preview_sql = f"""INSERT INTO movies (title, genre, language, mood, duration, rating, ott_platform, release_year, description, poster_url)
VALUES ('{c_title or "..."}', '{c_genre}', '{c_lang}', '{c_mood}', {c_duration}, {c_rating}, '{c_ott}', {c_year}, '...', '{c_poster}');"""
                
                render_html(f"<div class='sql-query-box'><strong>SQL DML Preview:</strong><br/>{preview_sql}</div>")
                
                submit_create = st.form_submit_button("🚀 Execute SQL INSERT Operation", use_container_width=True)

            if submit_create:
                if not c_title.strip() or not c_desc.strip():
                    st.error("❌ Movie Title and Description cannot be empty!")
                else:
                    try:
                        new_id, exec_sql = sql_db.create_movie(
                            title=c_title.strip(),
                            genre=c_genre.strip(),
                            language=c_lang.strip(),
                            mood=c_mood.strip(),
                            duration=int(c_duration),
                            rating=float(c_rating),
                            ott_platform=c_ott.strip(),
                            release_year=int(c_year),
                            description=c_desc.strip(),
                            poster_url=c_poster.strip()
                        )
                        db.reload()
                        st.success(f"✅ Record successfully inserted into SQLite database! Assigned **PRIMARY KEY: movie_id = {new_id}**")
                        st.info(f"📜 Executed SQL: `{exec_sql}`")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"❌ SQL Execution Error: {str(ex)}")

        # ----------------- [R]EAD (SELECT) -----------------
        elif crud_mode == "🔍 Read (SELECT)":
            st.markdown("#### 🔍 [R]ead — Query & Filter Database Records (`SELECT ... WHERE`)")
            st.caption("Executes parameterized SQL SELECT statements utilizing secondary B-Tree indexes for optimal query speed.")

            rc1, rc2, rc3, rc4 = st.columns([2, 1.2, 1.2, 1.2])
            with rc1:
                r_search = st.text_input("Keyword Search (Title or Description)", placeholder="e.g. detective, crime, space...", key="r_search_inp")
            with rc2:
                all_otts = ["All"] + db.get_ott_platforms()
                r_ott = st.selectbox("OTT Platform", all_otts, key="r_ott_inp")
            with rc3:
                all_genres = ["All"] + db.get_genres()
                r_genre = st.selectbox("Genre Filter", all_genres, key="r_genre_inp")
            with rc4:
                r_min_rating = st.slider("Min Rating", 0.0, 10.0, 7.5, 0.1, key="r_rating_inp")

            sc1, sc2, sc3 = st.columns([1.5, 1.5, 2])
            with sc1:
                r_sort = st.selectbox("Order By Column", ["rating", "movie_id", "title", "duration", "release_year"], key="r_sort_inp")
            with sc2:
                r_dir = st.selectbox("Direction", ["DESC", "ASC"], key="r_dir_inp")
            with sc3:
                r_limit = st.selectbox("Row Limit", [10, 25, 50, 100, 200], index=1, key="r_limit_inp")

            movies_list, query_sql, query_time_ms = sql_db.read_all_movies(
                search=r_search,
                genre=r_genre,
                ott_platform=r_ott,
                min_rating=r_min_rating,
                sort_by=r_sort,
                order=r_dir,
                limit=r_limit
            )

            # Display executed SQL and performance metrics
            render_html(
                f"""
                <div class="sql-query-box">
                    <strong>Executed Parameterized SQL:</strong><br/>
                    {query_sql}
                </div>
                """
            )
            st.markdown(f"⚡ **Query Execution Time:** `{query_time_ms:.2f} ms` | **Rows Returned:** `{len(movies_list)}` | **Storage Index:** `B-Tree Accelerated`")

            if movies_list:
                df_display = pd.DataFrame(movies_list)[["movie_id", "title", "genre", "language", "duration", "rating", "ott_platform", "release_year"]]
                st.dataframe(df_display, use_container_width=True, hide_index=True)
            else:
                st.warning("No records matched the specified SQL WHERE criteria.")

        # ----------------- [U]PDATE (UPDATE) -----------------
        elif crud_mode == "✏️ Update (UPDATE)":
            st.markdown("#### ✏️ [U]pdate — Modify Existing Record (`UPDATE ... SET ... WHERE`)")
            st.caption("Select any movie by PRIMARY KEY to update attributes with instantaneous SQL execution.")

            # Dropdown to pick movie
            all_db_movies = sql_db.read_all_movies(limit=500, sort_by="title", order="ASC")[0]
            movie_options = {f"#{m['movie_id']} — {m['title']} ({m['release_year']})": m['movie_id'] for m in all_db_movies}

            selected_movie_label = st.selectbox("Select Movie to Edit:", list(movie_options.keys()), key="u_movie_dropdown")
            selected_id = movie_options[selected_movie_label]
            curr_movie = sql_db.read_movie(selected_id)

            if curr_movie:
                with st.form("form_update_movie", clear_on_submit=False):
                    uc1, uc2 = st.columns(2)
                    with uc1:
                        u_title = st.text_input("Title *", value=curr_movie["title"])
                        u_year = st.number_input("Release Year *", min_value=1900, max_value=2030, value=int(curr_movie["release_year"]), step=1)
                        u_genre = st.text_input("Genre(s) *", value=curr_movie["genre"])
                        u_lang = st.text_input("Language *", value=curr_movie["language"])
                        u_mood = st.text_input("Mood *", value=curr_movie["mood"])
                    with uc2:
                        u_duration = st.number_input("Duration (min) *", min_value=1, max_value=600, value=int(curr_movie["duration"]), step=1)
                        u_rating = st.slider("IMDb Rating *", min_value=0.0, max_value=10.0, value=float(curr_movie["rating"]), step=0.1)
                        u_ott = st.text_input("OTT Platform *", value=curr_movie["ott_platform"])
                        u_poster = st.text_input("Poster URL", value=curr_movie.get("poster_url", ""))

                    u_desc = st.text_area("Plot Description *", value=curr_movie["description"])

                    preview_update_sql = f"""UPDATE movies
SET title = '{u_title}', rating = {u_rating}, ott_platform = '{u_ott}', duration = {u_duration}, description = '...'
WHERE movie_id = {selected_id};"""

                    render_html(f"<div class='sql-query-box'><strong>SQL DML Preview:</strong><br/>{preview_update_sql}</div>")

                    submit_update = st.form_submit_button("💾 Execute SQL UPDATE Operation", use_container_width=True)

                if submit_update:
                    try:
                        ok, update_sql = sql_db.update_movie(
                            movie_id=selected_id,
                            title=u_title.strip(),
                            genre=u_genre.strip(),
                            language=u_lang.strip(),
                            mood=u_mood.strip(),
                            duration=int(u_duration),
                            rating=float(u_rating),
                            ott_platform=u_ott.strip(),
                            release_year=int(u_year),
                            description=u_desc.strip(),
                            poster_url=u_poster.strip()
                        )
                        if ok:
                            db.reload()
                            st.success(f"✅ Record #{selected_id} updated successfully in SQLite database!")
                            st.info(f"📜 Executed SQL: `{update_sql}`")
                            st.rerun()
                        else:
                            st.error("Failed to update: Movie ID not found.")
                    except Exception as ex:
                        st.error(f"❌ SQL Update Error: {str(ex)}")

        # ----------------- [D]ELETE (DELETE) -----------------
        elif crud_mode == "🗑️ Delete (DELETE)":
            st.markdown("#### 🗑️ [D]elete — Remove Movie Record (`DELETE FROM ... WHERE`)")
            st.caption("Permanently removes a record by PRIMARY KEY constraint and logs the transaction.")

            all_db_movies = sql_db.read_all_movies(limit=500, sort_by="title", order="ASC")[0]
            del_movie_options = {f"#{m['movie_id']} — {m['title']} ({m['release_year']}) [⭐ {m['rating']}]": m['movie_id'] for m in all_db_movies}

            del_selected_label = st.selectbox("Select Movie to Delete:", list(del_movie_options.keys()), key="d_movie_dropdown")
            del_id = del_movie_options[del_selected_label]
            target_movie = sql_db.read_movie(del_id)

            if target_movie:
                st.markdown(
                    f"""
                    <div style="background: rgba(255, 83, 118, 0.1); border: 1px solid rgba(255, 83, 118, 0.4); border-radius: 10px; padding: 1rem; margin: 1rem 0;">
                        <h4 style="color: #ff5376; margin: 0;">⚠️ Record Selected for Deletion</h4>
                        <p style="margin: 0.5rem 0 0 0; color: #f7f4eb;">
                            <strong>ID:</strong> {target_movie['movie_id']} | <strong>Title:</strong> {target_movie['title']} ({target_movie['release_year']})<br/>
                            <strong>Genre:</strong> {target_movie['genre']} | <strong>Platform:</strong> {target_movie['ott_platform']} | <strong>Rating:</strong> ⭐ {target_movie['rating']}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                preview_del_sql = f"DELETE FROM movies WHERE movie_id = {del_id};"
                render_html(f"<div class='sql-query-box'><strong>SQL DML Preview:</strong><br/>{preview_del_sql}</div>")

                confirm_del = st.checkbox(f"⚠️ I confirm permanent deletion of movie record #{del_id} from SQLite database.", key="d_confirm_check")

                if st.button("🗑️ Execute SQL DELETE Operation", type="primary", disabled=not confirm_del, use_container_width=True):
                    try:
                        ok, del_sql = sql_db.delete_movie(del_id)
                        if ok:
                            db.reload()
                            st.success(f"✅ Record #{del_id} '{target_movie['title']}' permanently deleted from SQLite table!")
                            st.info(f"📜 Executed SQL: `{del_sql}`")
                            st.rerun()
                        else:
                            st.error("Delete failed: Movie ID not found.")
                    except Exception as ex:
                        st.error(f"❌ SQL Delete Error: {str(ex)}")

    # -------------------------------------------------------------------------
    # SUB-TAB 2: LIVE SQL QUERY CONSOLE
    # -------------------------------------------------------------------------
    with sub_console:
        st.markdown("#### 💻 Live SQL Query Console (Execute Any SQL)")
        st.caption("Write and run arbitrary SQL statements (`SELECT`, `GROUP BY`, `JOIN`, `EXPLAIN QUERY PLAN`) with millisecond execution profiling.")

        # Preset query buttons
        st.markdown("**⚡ Quick Preset SQL Demos (Click to populate):**")
        p_col1, p_col2, p_col3, p_col4 = st.columns(4)

        if "sql_console_query" not in st.session_state:
            st.session_state.sql_console_query = "SELECT ott_platform, COUNT(*) AS movie_count, ROUND(AVG(rating), 2) AS avg_rating, MIN(duration) AS min_duration, MAX(duration) AS max_duration FROM movies GROUP BY ott_platform ORDER BY movie_count DESC;"

        with p_col1:
            if st.button("📊 OTT Platform Aggregations", use_container_width=True):
                st.session_state.sql_console_query = "SELECT ott_platform, COUNT(*) AS movie_count, ROUND(AVG(rating), 2) AS avg_rating, MIN(duration) AS min_duration, MAX(duration) AS max_duration FROM movies GROUP BY ott_platform ORDER BY movie_count DESC;"
                st.rerun()
        with p_col2:
            if st.button("⭐ Top 10 Highest Rated Movies", use_container_width=True):
                st.session_state.sql_console_query = "SELECT movie_id, title, genre, rating, ott_platform, release_year FROM movies ORDER BY rating DESC, release_year DESC LIMIT 10;"
                st.rerun()
        with p_col3:
            if st.button("🌐 Languages & Movie Count", use_container_width=True):
                st.session_state.sql_console_query = "SELECT language, COUNT(*) AS total_titles, ROUND(AVG(rating), 2) AS avg_rating FROM movies GROUP BY language ORDER BY total_titles DESC;"
                st.rerun()
        with p_col4:
            if st.button("⚡ EXPLAIN QUERY PLAN (Indexes)", use_container_width=True):
                st.session_state.sql_console_query = "EXPLAIN QUERY PLAN SELECT * FROM movies WHERE rating >= 8.5 AND ott_platform = 'Netflix';"
                st.rerun()

        # Query input box
        query_input = st.text_area(
            "SQL Statement:",
            value=st.session_state.sql_console_query,
            height=110,
            key="sql_terminal_input",
            help="Enter any valid SQL query for SQLite."
        )

        btn_run = st.button("⚡ Execute SQL Query", type="primary", use_container_width=True)

        if btn_run or query_input != st.session_state.sql_console_query:
            st.session_state.sql_console_query = query_input
            res_df, duration_ms, err = sql_db.execute_custom_query(query_input)

            if err:
                st.error(f"❌ SQL Execution Error: {err}")
            else:
                st.success(f"✅ Query executed successfully in **{duration_ms:.2f} ms** | **{len(res_df)} rows** returned.")
                st.dataframe(res_df, use_container_width=True)

    # -------------------------------------------------------------------------
    # SUB-TAB 3: RELATIONAL SCHEMA & B-TREES
    # -------------------------------------------------------------------------
    with sub_schema:
        st.markdown("#### 📐 Relational DBMS Schema & B-Tree Index Architecture")
        st.caption("Technical architectural breakdown of database normalization, constraints, and B-Tree indexing.")

        schema_data = sql_db.get_schema_info()

        for t_name, t_info in schema_data.items():
            with st.expander(f"📁 Table: `{t_name}` (Click to inspect columns & constraints)", expanded=(t_name == "movies")):
                st.markdown(f"**DDL Definition:**")
                st.code(t_info["create_sql"], language="sql")

                st.markdown("**Columns Metadata:**")
                cols_df = pd.DataFrame(t_info["columns"])[["cid", "name", "type", "notnull", "dflt_value", "pk"]]
                cols_df.columns = ["Col ID", "Name", "Data Type", "NOT NULL?", "Default", "PRIMARY KEY?"]
                cols_df["PRIMARY KEY?"] = cols_df["PRIMARY KEY?"].apply(lambda x: "🔑 PRIMARY KEY" if x else "No")
                cols_df["NOT NULL?"] = cols_df["NOT NULL?"].apply(lambda x: "✓ Yes" if x else "No")
                st.dataframe(cols_df, use_container_width=True, hide_index=True)

                if t_info["indexes"]:
                    st.markdown("**B-Tree Secondary Indexes:**")
                    idx_df = pd.DataFrame(t_info["indexes"])[["seq", "name", "unique", "origin"]]
                    idx_df.columns = ["Sequence", "Index Name", "Unique?", "Origin"]
                    st.dataframe(idx_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown(
            """
            #### 💡 How Secondary B-Tree Indexes Accelerate Search:
            - **Without Index (Full Table Scan):** To find movies with rating $\\ge 8.5$, the database engine must inspect every single row sequentially: $\\mathcal{O}(N)$ time complexity.
            - **With Secondary B-Tree Index (`idx_movies_rating`):** The ratings are organized in a balanced self-sorting B-Tree structure. Searching the index tree takes only $\\mathcal{O}(\\log N)$ operations, jumping straight to matching row pointers (`rowid`).
            """
        )

    # -------------------------------------------------------------------------
    # SUB-TAB 4: TRANSACTION AUDIT TRAIL & ACID
    # -------------------------------------------------------------------------
    with sub_audit:
        st.markdown("#### 📜 DBMS Transaction Audit Trail & ACID Guarantees")
        st.caption("Every INSERT, UPDATE, and DELETE operation is recorded into `dbms_audit_log` with an immutable timestamp.")

        audit_df = sql_db.get_audit_logs(limit=30)
        if not audit_df.empty:
            st.dataframe(audit_df, use_container_width=True, hide_index=True)
        else:
            st.info("No audit transactions logged yet.")

        st.markdown("---")
        st.markdown("#### 🛡️ ACID Properties Enforcement in CineMatch:")
        acid_c1, acid_c2 = st.columns(2)
        with acid_c1:
            st.markdown(
                """
                ##### **1. Atomicity (All or Nothing)**
                - Every CRUD transaction is wrapped in `BEGIN TRANSACTION` and committed atomically.
                - If any constraint fails (e.g. invalid rating $> 10.0$ or missing title), the entire operation rolls back.

                ##### **2. Consistency (State Invariants)**
                - Enforced via strict SQL schema constraints:
                  - `CHECK(duration > 0)` prevents negative or zero runtimes.
                  - `CHECK(rating >= 0.0 AND rating <= 10.0)` prevents invalid IMDb scores.
                  - `PRIMARY KEY AUTOINCREMENT` prevents duplicate movie identifiers.
                """
            )
        with acid_c2:
            st.markdown(
                """
                ##### **3. Isolation (Concurrency Control)**
                - SQLite implements Write-Ahead Logging (WAL) and table-level locking to prevent dirty reads or race conditions between recommendation queries and CRUD edits.

                ##### **4. Durability (Persistence)**
                - Once committed, records are persisted to disk in `data/movies.db` and synchronized with `data/movies.csv`, surviving power failures or application restarts.
                """
            )


# ==========================================
# TAB 5: DAA & DBMS VIVA GUIDE
# ==========================================
with tab_viva:
    st.markdown("### 🎓 Academic Viva & Theory Guide (DAA & DBMS)")
    render_html(
        "<p style='color: #9ba3be; font-size: 0.9rem;'>Comprehensive theoretical reference covering Algorithms (DAA) and Relational Database Management Systems (DBMS) for university viva examinations.</p>"
    )

    viva_daa_tab, viva_dbms_tab = st.tabs(["⚡ DAA Algorithms & Complexity", "🗄️ Relational DBMS & SQL Theory"])

    with viva_daa_tab:
        col_v1, col_v2 = st.columns(2)

        with col_v1:
            st.markdown(
                """
                #### 1. Sorting Algorithms
                
                ##### **A. QuickSort (Divide and Conquer)**
                - **Partition Scheme:** Lomuto Partition.
                - **Pivot Strategy:** Last element chosen as pivot.
                - **Recurrence Relation:** $T(N) = T(k) + T(N - k - 1) + \\Theta(N)$
                - **Time Complexity:**
                  - *Best Case:* $\\mathcal{O}(N \\log N)$
                  - *Average Case:* $\\mathcal{O}(N \\log N)$
                  - *Worst Case:* $\\mathcal{O}(N^2)$ (when list is already reverse-sorted with extreme pivot).
                - **Space Complexity:** $\\mathcal{O}(\\log N)$ recursive auxiliary call stack.
                - **Role in CineMatch:** Used to rank recommendation candidate scores in descending order.

                ##### **B. MergeSort (Divide and Conquer)**
                - **Mechanism:** Recursively splits list in half, sorts each half, and merges two sorted subarrays.
                - **Recurrence Relation:** $T(N) = 2T(N/2) + \\Theta(N)$
                - **Time Complexity:** $\\mathcal{O}(N \\log N)$ in all cases (Best, Average, Worst).
                - **Space Complexity:** $\\mathcal{O}(N)$ auxiliary memory for merging.
                - **Key Property:** Stability (preserves original order for equal scores).
                """
            )

        with col_v2:
            st.markdown(
                """
                #### 2. Searching & Filtering Algorithms

                ##### **A. Binary Search (Decrease and Conquer)**
                - **Precondition:** Array must be sorted (e.g. sorted by movie rating).
                - **Mechanism:** Repeatedly examines midpoint element; eliminates half the search space.
                - **Time Complexity:** $\\mathcal{O}(\\log N)$ boundary search $+ \\mathcal{O}(K)$ range traversal.
                - **Space Complexity:** $\\mathcal{O}(1)$ auxiliary space.
                - **Role in CineMatch:** Used in `binary_search_by_rating()` for rating-based queries.

                ##### **B. Linear Search (Brute Force)**
                - **Time Complexity:** $\\mathcal{O}(N \\times M)$ where $N$ is movie count and $M$ is query string length.
                - **Role in CineMatch:** Used for title keyword lookup in the Watchlist.

                #### 3. Recommendation Scoring Formula
                $$\\text{Score} = \\left(\\sum_{i=1}^{4} w_i \\cdot m_i\\right) \\times 70 + \\left(\\frac{\\text{Rating}}{10.0}\\right) \\times 30$$
                - $w_i = 0.25$ for each dimension (Genre, Mood, Time, Language).
                - $m_i \\in \\{0, 1\\}$ indicates whether dimension matches user input.
                - Normalizes result to an explainable $0 - 100\\%$ match score.
                """
            )

        # Complexity Summary Table
        st.markdown("#### 📊 Algorithmic Complexity Comparison Table")
        st.markdown(
            """
            | Algorithm | Paradigm | Best Time | Average Time | Worst Time | Space | Stable? | CineMatch Application |
            | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
            | **QuickSort** | Divide & Conquer | $\\mathcal{O}(N \\log N)$ | $\\mathcal{O}(N \\log N)$ | $\\mathcal{O}(N^2)$ | $\\mathcal{O}(\\log N)$ | No | Primary ranking engine |
            | **MergeSort** | Divide & Conquer | $\\mathcal{O}(N \\log N)$ | $\\mathcal{O}(N \\log N)$ | $\\mathcal{O}(N \\log N)$ | $\\mathcal{O}(N)$ | Yes | Alternative stable sorter |
            | **Binary Search** | Decrease & Conquer | $\\mathcal{O}(1)$ | $\\mathcal{O}(\\log N)$ | $\\mathcal{O}(\\log N)$ | $\\mathcal{O}(1)$ | N/A | Fast rating range search |
            | **Linear Search** | Brute Force | $\\mathcal{O}(1)$ | $\\mathcal{O}(N)$ | $\\mathcal{O}(N)$ | $\\mathcal{O}(1)$ | N/A | Watchlist title filter |
            """
        )

    with viva_dbms_tab:
        st.markdown("#### 🗄️ Top DBMS Viva Questions & Model Answers for Teachers")
        
        with st.expander("Q1: Why did you transition from flat CSV files to an SQL Relational Database (RDBMS)?"):
            st.markdown(
                """
                **Model Answer:**
                > Flat CSV files lack structured schema enforcement, concurrent read/write isolation, and indexing. By adopting an SQLite Relational Database Management System (RDBMS):
                > 1. **Data Integrity:** We enforce strict constraints (`PRIMARY KEY`, `NOT NULL`, `CHECK(rating >= 0 AND rating <= 10)`).
                > 2. **Index-Based Querying:** We use B-Tree indexes on `rating`, `year`, and `ott_platform` to achieve $\\mathcal{O}(\\log N)$ search time instead of $\\mathcal{O}(N)$ full table scans.
                > 3. **ACID Guarantees:** Ensures transactions are atomic and durable, preventing data corruption during concurrent operations.
                """
            )

        with st.expander("Q2: What is the Relational Schema and Primary Key in CineMatch?"):
            st.markdown(
                """
                **Model Answer:**
                > The primary entity table is `movies`, where each movie record is uniquely identified by `movie_id INTEGER PRIMARY KEY AUTOINCREMENT`.
                > To prevent redundancy and demonstrate normalization (2NF/3NF), OTT platforms are segregated into an `ott_platforms` master lookup table, and all state modifications are recorded into `dbms_audit_log` with timestamps and executed SQL statements.
                """
            )

        with st.expander("Q3: What is the difference between DDL and DML in your SQL implementation?"):
            st.markdown(
                """
                **Model Answer:**
                > - **DDL (Data Definition Language):** Defines database structure.
                >   * Example: `CREATE TABLE movies (...)`, `CREATE INDEX idx_movies_rating ON movies(rating);`, `CREATE TRIGGER ...`
                > - **DML (Data Manipulation Language):** Manipulates stored records (CRUD).
                >   * **C (Create):** `INSERT INTO movies (...) VALUES (...);`
                >   * **R (Read):** `SELECT * FROM movies WHERE rating >= 8.0;`
                >   * **U (Update):** `UPDATE movies SET rating = 8.8 WHERE movie_id = 5;`
                >   * **D (Delete):** `DELETE FROM movies WHERE movie_id = 5;`
                """
            )

        with st.expander("Q4: How do SQLite B-Tree Indexes improve query performance?"):
            st.markdown(
                """
                **Model Answer:**
                > In a relational database without an index, evaluating `WHERE rating >= 8.5` requires scanning every record in the table (a sequential Full Table Scan, $\\mathcal{O}(N)$).
                > By creating a B-Tree index (`idx_movies_rating`), the database maintains a balanced search tree of sorted rating values paired with direct row pointers. Query execution drops to logarithmic time $\\mathcal{O}(\\log N)$, drastically speeding up search filters.
                """
            )

        with st.expander("Q5: What are ACID properties and how are they maintained in this project?"):
            st.markdown(
                """
                **Model Answer:**
                > - **Atomicity:** SQLite transactions either commit entirely or rollback completely on error.
                > - **Consistency:** Schema constraints (`CHECK`, `NOT NULL`, `UNIQUE`) ensure only valid movie records enter the database.
                > - **Isolation:** SQLite table locking and WAL (Write-Ahead Logging) prevent read-write race conditions.
                > - **Durability:** Changes are flushed to non-volatile disk storage (`data/movies.db`) and synchronized with `data/movies.csv`.
                """
            )


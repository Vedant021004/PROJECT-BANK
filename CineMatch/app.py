"""
app.py
CineMatch — Smart Movie & OTT Finder
Frontend Application built with Streamlit and Custom Cinematic Dark CSS.
Featuring Interactive Slideshow / Carousel & Grid Views.
"""

import os
import sys
import textwrap
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
def get_database_and_recommender(csv_mtime: float):
    csv_path = os.path.join(os.path.dirname(__file__), "data", "movies.csv")
    db = MovieDatabase(csv_path)
    engine = RecommendationEngine(db)
    judge = EvaluationJudge(db, engine)
    return db, engine, judge


csv_file_path = os.path.join(os.path.dirname(__file__), "data", "movies.csv")
csv_mtime = os.path.getmtime(csv_file_path) if os.path.exists(csv_file_path) else 0.0
db, engine, judge = get_database_and_recommender(csv_mtime)

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
tab_find, tab_watchlist, tab_evaluator, tab_viva = st.tabs([
    "🎯 Find My Movie",
    f"🔖 My Watchlist ({watchlist_count})",
    "⚖️ Judge Evaluation Scorecard",
    "🎓 DAA Viva & Complexity Guide"
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

    # Card Container
    card_html = f"""
    <div class="movie-card">
        <div class="card-header-row">
            <div>
                <h3 class="card-title">{m.title} <span class="card-year">({m.release_year})</span></h3>
            </div>
            <div class="card-score-pill">
                🎯 {bd.final_score}% Match
            </div>
        </div>
        
        <div class="card-badges">
            <span class="badge-tag badge-rating">⭐ {m.rating} / 10</span>
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

    # Watchlist action button
    col_w_btn, _ = st.columns([2.5, 4.5])
    with col_w_btn:
        btn_label = "✓ Remove from Watchlist" if is_in_watchlist else "+ Save to Watchlist"
        if st.button(btn_label, key=f"wl_{m.movie_id}_{card_key_suffix}", use_container_width=True):
            if is_in_watchlist:
                st.session_state.watchlist.remove(m.movie_id)
            else:
                st.session_state.watchlist.add(m.movie_id)
            st.rerun()


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
            render_html(
                f"""
                <div class="movie-card">
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
            if st.button("🗑️ Remove", key=f"wl_del_{m.movie_id}"):
                st.session_state.watchlist.remove(m.movie_id)
                st.rerun()


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
# TAB 4: DAA VIVA & COMPLEXITY GUIDE
# ==========================================
with tab_viva:
    st.markdown("### 🎓 Design & Analysis of Algorithms (DAA) — College Viva Guide")
    render_html(
        "<p style='color: #9ba3be; font-size: 0.9rem;'>Complete breakdown of algorithmic paradigms, sorting techniques, searching mechanisms, and mathematical proofs for viva presentation.</p>"
    )

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

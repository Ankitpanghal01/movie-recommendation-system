import hashlib
import html
import random
import re

import streamlit as st

from recommend import MovieRecommender

# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="CineMatch",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { padding-top: 1.5rem; padding-bottom: 4rem; max-width: 1280px; }

/* Background glow */
.stApp {
    background:
        radial-gradient(1000px 500px at 85% -10%, rgba(229, 9, 20, 0.18), transparent 60%),
        radial-gradient(800px 500px at -10% 10%, rgba(99, 102, 241, 0.16), transparent 60%),
        #0b0b12;
}

/* Hero */
.hero { text-align: center; padding: 2.5rem 1rem 1.5rem; }
.hero .badge {
    display: inline-block; padding: 6px 14px; border-radius: 999px;
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
    color: #c9c9d6; font-size: 0.8rem; font-weight: 500; letter-spacing: .04em;
    margin-bottom: 1.1rem;
}
.hero h1 {
    font-size: clamp(2.6rem, 6vw, 4.4rem); font-weight: 800; margin: 0;
    letter-spacing: -0.03em; line-height: 1.05;
    background: linear-gradient(90deg, #ffffff 0%, #ff4d5a 55%, #818cf8 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero p { color: #a1a1b5; font-size: 1.1rem; max-width: 620px; margin: 1rem auto 0; }

/* Inputs */
div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 14px !important; min-height: 52px;
}
div[data-baseweb="select"] > div:hover { border-color: #e50914 !important; }
.stButton > button {
    width: 100%; height: 52px; border-radius: 14px; font-weight: 600;
    border: 1px solid rgba(255,255,255,0.14); background: rgba(255,255,255,0.06);
    color: #fff; transition: all .2s ease;
}
.stButton > button:hover {
    border-color: #e50914; background: rgba(229,9,20,0.15); transform: translateY(-1px);
}

/* Section title */
.section-title {
    font-size: 1.35rem; font-weight: 700; color: #fff; margin: 2.2rem 0 1rem;
    display: flex; align-items: center; gap: 10px;
}
.section-title span { color: #ff4d5a; }

/* Selected movie banner */
.picked {
    display: flex; gap: 22px; align-items: center; padding: 22px;
    border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);
    background: linear-gradient(135deg, rgba(255,255,255,0.07), rgba(255,255,255,0.02));
    backdrop-filter: blur(8px); margin-top: 1.4rem;
}
.picked .mini-poster {
    flex: 0 0 90px; height: 130px; border-radius: 12px; display: flex;
    align-items: center; justify-content: center; font-size: 2.6rem; font-weight: 800;
    color: rgba(255,255,255,0.92); box-shadow: 0 10px 30px rgba(0,0,0,.45);
}
.picked h3 { margin: 0 0 6px; font-size: 1.6rem; font-weight: 700; color: #fff; }
.picked p { margin: 10px 0 0; color: #b4b4c6; line-height: 1.55; font-size: .95rem; }
.picked .label { color: #ff4d5a; font-size: .75rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }

/* Movie cards */
.card {
    position: relative; border-radius: 18px; overflow: hidden; height: 100%;
    min-height: 430px; display: flex; flex-direction: column;
    background: #141420; border: 1px solid rgba(255,255,255,0.08);
    transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}
.card:hover {
    transform: translateY(-6px); border-color: rgba(229,9,20,0.6);
    box-shadow: 0 18px 40px rgba(229,9,20,0.18);
}
.poster {
    height: 170px; display: flex; align-items: center; justify-content: center;
    font-size: 3.6rem; font-weight: 800; color: rgba(255,255,255,0.9);
    position: relative;
}
.poster::after {
    content: ""; position: absolute; inset: 0;
    background: linear-gradient(to top, #141420 0%, transparent 55%);
}
.rank {
    position: absolute; top: 12px; left: 12px; z-index: 2;
    background: rgba(0,0,0,0.55); backdrop-filter: blur(6px);
    padding: 4px 10px; border-radius: 999px; font-size: .75rem; font-weight: 700; color: #fff;
}
.card-body { padding: 4px 18px 18px; display: flex; flex-direction: column; flex: 1; }
.card-title { font-size: 1.08rem; font-weight: 700; color: #fff; margin: 0 0 10px; line-height: 1.25; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
.chip {
    font-size: .7rem; font-weight: 600; padding: 3px 10px; border-radius: 999px;
    background: rgba(129,140,248,0.14); color: #a5b4fc; border: 1px solid rgba(129,140,248,0.25);
}
.desc { color: #a1a1b5; font-size: .85rem; line-height: 1.55; flex: 1; }
.match { margin-top: 14px; }
.match-row { display: flex; justify-content: space-between; font-size: .75rem; color: #c9c9d6; margin-bottom: 6px; font-weight: 600; }
.bar { height: 6px; border-radius: 999px; background: rgba(255,255,255,0.08); overflow: hidden; }
.bar > div { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #e50914, #ff7a45); }

/* Empty state */
.empty { text-align: center; color: #8a8aa0; padding: 3rem 1rem; }
.empty .big { font-size: 3rem; }

.footer { text-align: center; color: #6b6b80; font-size: .8rem; margin-top: 4rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
GRADIENTS = [
    ("#e50914", "#7f1d1d"), ("#6366f1", "#312e81"), ("#06b6d4", "#164e63"),
    ("#f59e0b", "#78350f"), ("#10b981", "#064e3b"), ("#ec4899", "#831843"),
    ("#8b5cf6", "#4c1d95"), ("#f97316", "#7c2d12"),
]


def poster_style(title: str) -> str:
    """Deterministic gradient 'poster' per title (dataset has no images)."""
    idx = int(hashlib.md5(title.encode()).hexdigest(), 16) % len(GRADIENTS)
    a, b = GRADIENTS[idx]
    return f"background: linear-gradient(145deg, {a}, {b});"


def initials(title: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", title)
    return "".join(w[0] for w in words[:2]).upper() or "🎬"


def split_genres(genres: str):
    parts = [g.strip() for g in re.split(r"[|,/]", str(genres)) if g.strip()]
    return parts[:4]


def truncate(text: str, limit: int = 170) -> str:
    text = str(text).strip()
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "…"


def chips_html(genres: str) -> str:
    return "".join(f'<span class="chip">{html.escape(g)}</span>' for g in split_genres(genres))


def movie_card(rank: int, movie) -> str:
    title = html.escape(str(movie["title"]))
    score = float(movie["similarity_score"])
    width = max(4.0, min(score, 100.0))
    return f"""
    <div class="card">
        <div class="poster" style="{poster_style(str(movie['title']))}">
            <div class="rank">#{rank}</div>
            {html.escape(initials(str(movie['title'])))}
        </div>
        <div class="card-body">
            <div class="card-title">{title}</div>
            <div class="chips">{chips_html(movie['genres'])}</div>
            <div class="desc">{html.escape(truncate(movie['description']))}</div>
            <div class="match">
                <div class="match-row"><span>Match</span><span>{score:.1f}%</span></div>
                <div class="bar"><div style="width:{width}%"></div></div>
            </div>
        </div>
    </div>
    """


# ----------------------------------------------------------------------------
# Data / model
# ----------------------------------------------------------------------------
@st.cache_resource(show_spinner="Loading CineMatch engine…")
def load_recommender():
    return MovieRecommender("dataset/movies.csv")


recommender = load_recommender()
movie_list = recommender.movies["title"].tolist()

if "movie_choice" not in st.session_state:
    st.session_state.movie_choice = movie_list[0]


def surprise_me():
    st.session_state.movie_choice = random.choice(movie_list)


# ----------------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="badge">🎬 AI-POWERED MOVIE DISCOVERY</div>
        <h1>CineMatch</h1>
        <p>Pick a movie you love and we'll find your next favourite using
        machine learning on genres and plot descriptions.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Controls
# ----------------------------------------------------------------------------
c1, c2, c3 = st.columns([5, 2, 2], vertical_alignment="bottom")
with c1:
    st.selectbox(
        "Search or choose a movie",
        movie_list,
        key="movie_choice",
        help="Click and start typing to search.",
    )
with c2:
    top_n = st.select_slider("Recommendations", options=[5, 10, 15], value=5)
with c3:
    st.button("🎲 Surprise me", on_click=surprise_me)

selected_movie = st.session_state.movie_choice

# ----------------------------------------------------------------------------
# Selected movie banner
# ----------------------------------------------------------------------------
row = recommender.movies[recommender.movies["title"] == selected_movie].iloc[0]
st.markdown(
    f"""
    <div class="picked">
        <div class="mini-poster" style="{poster_style(selected_movie)}">
            {html.escape(initials(selected_movie))}
        </div>
        <div>
            <div class="label">Your pick</div>
            <h3>{html.escape(selected_movie)}</h3>
            <div class="chips">{chips_html(row['genres'])}</div>
            <p>{html.escape(truncate(row['description'], 260))}</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Recommendations
# ----------------------------------------------------------------------------
with st.spinner("Finding your matches…"):
    recommendations = recommender.recommend(selected_movie, top_n=top_n)

if recommendations.empty:
    st.markdown(
        '<div class="empty"><div class="big">🍿</div>No recommendations found for this movie.</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="section-title"><span>▶</span> Because you liked '
        f"{html.escape(selected_movie)}</div>",
        unsafe_allow_html=True,
    )

    records = list(recommendations.to_dict("records"))
    PER_ROW = 5
    for start in range(0, len(records), PER_ROW):
        chunk = records[start:start + PER_ROW]
        cols = st.columns(PER_ROW)
        for offset, movie in enumerate(chunk):
            with cols[offset]:
                st.markdown(movie_card(start + offset + 1, movie), unsafe_allow_html=True)
        st.write("")

st.markdown(
    '<div class="footer">CineMatch · TF-IDF + Cosine Similarity · Built with Streamlit</div>',
    unsafe_allow_html=True,
)

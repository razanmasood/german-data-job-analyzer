import json
import pathlib
import sys
import plotly.graph_objects as go
import streamlit as st

# Make src/ importable when running via `streamlit run app/dashboard.py`
_SRC = pathlib.Path(__file__).parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from ner.predict import load_pipeline, extract_entities  # noqa: E402

DATA_DIR = pathlib.Path(__file__).parent.parent / "data"
RESULTS_PATH = DATA_DIR / "analyzed" / "results.json"
EXP_LEVEL_PATH = DATA_DIR / "processed" / "experience_level_analysis.json"


@st.cache_data
def load_data():
    with open(RESULTS_PATH) as f:
        results = json.load(f)
    with open(EXP_LEVEL_PATH) as f:
        exp_analysis = json.load(f)
    return results, exp_analysis


def filter_noise(items: list[dict], min_len: int = 3) -> list[dict]:
    """Remove entries whose name is shorter than min_len characters."""
    return [item for item in items if len(item["name"]) >= min_len]


def make_bar(names, values, bar_color, font_color, x_title="", height=420, horizontal=False):
    """Build a themed plotly bar chart."""
    if horizontal:
        trace = go.Bar(x=values, y=names, orientation="h", marker_color=bar_color)
    else:
        trace = go.Bar(x=names, y=values, marker_color=bar_color)
    fig = go.Figure(trace)
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": font_color},
        xaxis_title=x_title,
        margin={"l": 10, "r": 10, "t": 10, "b": 120 if not horizontal else 10},
        xaxis={"tickangle": -40, "tickfont": {"color": font_color}} if not horizontal else {"tickfont": {"color": font_color}},
        yaxis={"autorange": "reversed", "tickfont": {"color": font_color}} if horizontal else {"tickfont": {"color": font_color}},
    )
    return fig


# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="German Data Science Job Market Analyzer",
    layout="wide",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────

results, exp_analysis = load_data()

exp_levels = list(results["skills_by_experience_level"].keys())
selected_level = st.sidebar.selectbox(
    "Experience level",
    options=["All"] + exp_levels,
)
st.sidebar.caption("Filter applies to Skills and Tools charts only")

st.sidebar.divider()

dark_mode = st.sidebar.toggle("🌙 Dark mode", value=False)

# ── Theme ─────────────────────────────────────────────────────────────────────

if dark_mode:
    theme = {
        "bg": "#1a1a2e",
        "bar": "#7c83fd",
        "accent": "#e94560",
        "text": "#f0f0f0",
    }
else:
    theme = {
        "bg": "#f8f9fa",
        "bar": "#6c63ff",
        "accent": "#ff6584",
        "text": "#1a1a2e",
    }

_TEXT  = "#f0f0f0" if dark_mode else "#1a1a2e"
_BG    = "#1a1a2e" if dark_mode else "#f8f9fa"
_SIDE  = "#16213e" if dark_mode else "#e9ecef"
_INPUT = "#2a2a4a" if dark_mode else "#ffffff"
_BTN_BG = "#7c83fd" if dark_mode else "#6c63ff"

st.markdown(f"""
    <style>
        /* Page & sidebar backgrounds */
        .stApp {{ background-color: {_BG} !important; }}
        [data-testid="stSidebar"] {{ background-color: {_SIDE} !important; }}

        /* Text — target semantic elements, not the universal * */
        .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
        .stApp label, .stApp span, .stApp caption,
        .stApp li, .stApp ul, .stApp ol,
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span {{ color: {_TEXT} !important; }}

        /* Metrics */
        [data-testid="stMetricLabel"] p,
        [data-testid="stMetricValue"],
        [data-testid="stMetricDelta"] {{ color: {_TEXT} !important; }}

        /* Text area */
        [data-testid="stTextArea"] textarea {{
            background-color: {_INPUT} !important;
            color: {_TEXT} !important;
        }}
        [data-testid="stTextArea"] textarea::placeholder {{
            color: {"#aaaaaa" if dark_mode else "#999999"} !important;
            opacity: 1 !important;
        }}

        /* Button */
        [data-testid="stButton"] > button {{
            background-color: {_BTN_BG} !important;
            color: #ffffff !important;
            border: none !important;
        }}

        /* Selectbox */
        [data-testid="stSelectbox"] > div > div {{
            background-color: {_INPUT} !important;
            color: {_TEXT} !important;
        }}
    </style>
""", unsafe_allow_html=True)

# ── Title ─────────────────────────────────────────────────────────────────────

st.title("German Data Science Job Market Analyzer")
st.write("Analyzing 1,240 German data science job postings from LinkedIn (January 2026)")

summary = results["summary"]

# ── Summary metrics ───────────────────────────────────────────────────────────

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Jobs", f"{summary['total_jobs']:,}")
col2.metric("Unique Skills", f"{summary['total_unique_skills']:,}")
col3.metric("Unique Tools", f"{summary['total_unique_tools']:,}")
col4.metric("Avg Skills / Job", f"{summary['avg_skills_per_job']:.1f}")

st.divider()

# ── Top 20 skills ─────────────────────────────────────────────────────────────

level_label = f" — {selected_level}" if selected_level != "All" else ""

col_skills, col_tools = st.columns(2)

raw_skills = (
    results["skills_by_experience_level"][selected_level]
    if selected_level != "All"
    else results["top_skills"]
)
skills_clean = filter_noise(raw_skills)[:20]

raw_tools = (
    results["tools_by_experience_level"][selected_level]
    if selected_level != "All"
    else results["top_tools"]
)
tools_clean = filter_noise(raw_tools)[:20]

with col_skills:
    st.subheader(f"Top 20 Skills{level_label}")
    st.plotly_chart(
        make_bar([r["name"] for r in skills_clean], [r["count"] for r in skills_clean], theme["bar"], theme["text"]),
        use_container_width=True,
    )
    st.caption("Based on NER extraction from job descriptions using a fine-tuned xlm-roberta-large model")

with col_tools:
    st.subheader(f"Top 20 Tools{level_label}")
    st.plotly_chart(
        make_bar([r["name"] for r in tools_clean], [r["count"] for r in tools_clean], theme["bar"], theme["text"]),
        use_container_width=True,
    )
    st.caption("Based on NER extraction from job descriptions using a fine-tuned xlm-roberta-large model")

st.divider()

# ── Seniority distribution ────────────────────────────────────────────────────

st.subheader("Jobs by Experience Level")

value_dist = exp_analysis["value_distribution"]
seniority = sorted(value_dist.items(), key=lambda x: x[1]["count"], reverse=True)
st.plotly_chart(
    make_bar([k for k, _ in seniority], [v["count"] for _, v in seniority], theme["bar"], theme["text"]),
    use_container_width=True,
)
st.caption("Source: LinkedIn experienceLevel field (100% complete)")

st.divider()

# ── Skill co-occurrence ───────────────────────────────────────────────────────

st.subheader("Skill Co-occurrence (Top 15 Pairs)")
st.caption("Skills that most frequently appear together in the same job posting")


def _pair_is_valid(pair):
    a, b = pair
    return len(a) >= 3 and len(b) >= 3 and a not in b and b not in a


top_pairs = sorted(
    [item for item in results["skill_cooccurrence"] if _pair_is_valid(item["pair"])],
    key=lambda x: x["count"],
    reverse=True,
)[:15]
co_labels = [f"{item['pair'][0]} + {item['pair'][1]}" for item in top_pairs]
co_counts = [item["count"] for item in top_pairs]

st.plotly_chart(
    make_bar(co_labels, co_counts, theme["bar"], theme["text"], x_title="Co-occurrence count", height=500, horizontal=True),
    use_container_width=True,
)

st.divider()

# ── Analyze a Job Posting ─────────────────────────────────────────────────────

st.subheader("Analyze a Job Posting")

job_text = st.text_area(
    "Paste a job posting here",
    height=250,
    placeholder="Paste any German or English job posting text…",
)

if st.button("Extract Skills & Tools"):
    if not job_text.strip():
        st.warning("Please paste some job posting text first.")
    else:
        with st.spinner("Analyzing…"):
            ner_pipe = load_pipeline()
            skills, tools = extract_entities(job_text, ner_pipe)

        _WHITELIST = {
            "sql", "aws", "gcp", "nlp", "api", "r", "go", "java", "rust",
            "bert", "llm", "git", "ci", "cd", "etl",
        }
        _BLACKLIST = {"iert", "informati", "automat"}

        def _clean(entities):
            seen = set()
            out = []
            for e in entities:
                key = e.lower()
                if key in _BLACKLIST or key in seen:
                    continue
                if key in _WHITELIST or len(key) > 4:
                    seen.add(key)
                    out.append(e)
            return sorted(out, key=str.lower)

        skills = _clean(skills)
        tools = _clean(tools)

        col_s, col_t = st.columns(2)

        with col_s:
            st.markdown("**Skills**")
            if skills:
                for s in skills:
                    st.write(f"- {s}")
            else:
                st.write("No skills found.")

        with col_t:
            st.markdown("**Tools**")
            if tools:
                for t in tools:
                    st.write(f"- {t}")
            else:
                st.write("No tools found.")

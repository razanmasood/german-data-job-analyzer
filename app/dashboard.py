import json
import os
import pathlib
import sys
import textwrap
from collections import Counter

import pandas as pd

import langextract as lx
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

DATA_DIR           = pathlib.Path(__file__).parent.parent / "data"
RESULTS_PATH       = DATA_DIR / "analysis" / "langextract_results.json"
EXP_LEVEL_PATH     = DATA_DIR / "processed" / "experience_level_analysis.json"
LANG_COMPARE_PATH  = DATA_DIR / "processed" / "language_comparison.json"
SENIORITY_PATH     = DATA_DIR / "processed" / "seniority_analysis.json"
CODEP_PATH         = DATA_DIR / "processed" / "tool_skill_codependency.json"
EXCL_PATH          = DATA_DIR / "processed" / "skill_exclusivity.json"
CONC_PATH          = DATA_DIR / "processed" / "company_concentration.json"

# ---------------------------------------------------------------------------
# LangExtract prompt + examples  (same as 10b_run_langextract_inference.py)
# ---------------------------------------------------------------------------

_PROMPT = textwrap.dedent("""
    Extract SKILL and TOOL entities from job posting requirements sections.

    SKILL: A technical competency, methodology, or domain knowledge.
    Examples: machine learning, NLP, deep learning, statistical modeling, MLOps, data engineering, CI/CD

    TOOL: A specific technology, programming language, framework, platform, or library.
    Examples: Python, PyTorch, TensorFlow, Docker, AWS, SQL, Kubernetes, scikit-learn

    Rules:
    - Use EXACT text from the source. Do not translate or paraphrase.
    - Do not extract soft skills (teamwork, communication).
    - Do not extract job titles or degree names.
    - Works in both German and English.
""")

_EXAMPLES = [
    lx.data.ExampleData(
        text="Experience with Python and machine learning. Familiarity with Docker and AWS.",
        extractions=[
            lx.data.Extraction(extraction_class="TOOL",  extraction_text="Python"),
            lx.data.Extraction(extraction_class="SKILL", extraction_text="machine learning"),
            lx.data.Extraction(extraction_class="TOOL",  extraction_text="Docker"),
            lx.data.Extraction(extraction_class="TOOL",  extraction_text="AWS"),
        ],
    ),
    lx.data.ExampleData(
        text="Kenntnisse in Deep Learning und Datenanalyse. Erfahrung mit PyTorch und Kubernetes.",
        extractions=[
            lx.data.Extraction(extraction_class="SKILL", extraction_text="Deep Learning"),
            lx.data.Extraction(extraction_class="SKILL", extraction_text="Datenanalyse"),
            lx.data.Extraction(extraction_class="TOOL",  extraction_text="PyTorch"),
            lx.data.Extraction(extraction_class="TOOL",  extraction_text="Kubernetes"),
        ],
    ),
]

LANGEXTRACT_MODEL = "gemini-2.5-flash-lite"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

@st.cache_data
def load_data():
    with open(RESULTS_PATH) as f:
        results = json.load(f)
    with open(EXP_LEVEL_PATH) as f:
        exp_analysis = json.load(f)
    with open(SENIORITY_PATH) as f:
        seniority_analysis = json.load(f)
    with open(CODEP_PATH) as f:
        codep = json.load(f)
    with open(EXCL_PATH) as f:
        excl = json.load(f)
    with open(CONC_PATH) as f:
        conc = json.load(f)
    return results, exp_analysis, seniority_analysis, codep, excl, conc


@st.cache_data
def load_language_comparison():
    with open(LANG_COMPARE_PATH) as f:
        return json.load(f)


@st.cache_data
def load_german_level_by_seniority():
    """Return a dict {experienceLevel: {german_level: count}} from jobs_combined_clean.json."""
    with open(DATA_DIR / "processed" / "jobs_combined_clean.json", encoding="utf-8") as f:
        jobs = json.load(f)
    matrix: dict[str, dict[str, int]] = {}
    for job in jobs:
        exp = job.get("experienceLevel", "Unknown")
        gl  = job.get("german_level", "not_mentioned")
        if exp not in matrix:
            matrix[exp] = {}
        matrix[exp][gl] = matrix[exp].get(gl, 0) + 1
    return matrix


def _setup_api_key() -> bool:
    """Load LANGEXTRACT_API_KEY from .env and expose it as GOOGLE_API_KEY.
    Returns True if key is available, False otherwise.
    """
    load_dotenv(pathlib.Path(__file__).parent.parent / ".env")
    key = os.environ.get("LANGEXTRACT_API_KEY")
    if key:
        os.environ["GOOGLE_API_KEY"] = key
        return True
    return False


# ---------------------------------------------------------------------------
# Chart helper
# ---------------------------------------------------------------------------

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


def filter_noise(items: list[dict], min_len: int = 3) -> list[dict]:
    return [item for item in items if len(item["name"]) >= min_len]


def normalize_and_merge(items: list[dict], top_n: int = 20) -> list[dict]:
    """Merge entity counts whose .lower().strip() form is identical, keeping
    the most-common original casing as the display label."""
    merged: Counter = Counter()
    canonical: dict[str, str] = {}
    for item in items:
        key = item["entity"].lower().strip()
        merged[key] += item["count"]
        if key not in canonical:
            canonical[key] = item["entity"]
    return [{"entity": canonical[k], "count": v} for k, v in merged.most_common(top_n)]


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="German Data Science Job Market — LangExtract",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Check that inference results exist
# ---------------------------------------------------------------------------

if not RESULTS_PATH.exists():
    st.error(
        f"**Results file not found:** `{RESULTS_PATH}`\n\n"
        "Run the inference script first:\n"
        "```\npython scripts/10b_run_langextract_inference.py\n```"
    )
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

results, exp_analysis, seniority_analysis, codep, excl, conc = load_data()

exp_levels = list(results["skills_by_experience_level"].keys())
selected_level = st.sidebar.selectbox(
    "Experience level",
    options=["All"] + exp_levels,
)
st.sidebar.caption("Filter applies to Skills and Tools charts only")

st.sidebar.divider()

dark_mode = st.sidebar.toggle("🌙 Dark mode", value=True)

st.sidebar.divider()
st.sidebar.caption("Extraction model: **gemini-2.5-flash-lite** via LangExtract (few-shot, no fine-tuning)")

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

if dark_mode:
    theme   = {"bg": "#1a1a2e", "bar": "#7c83fd", "accent": "#e94560", "text": "#f0f0f0"}
else:
    theme   = {"bg": "#f8f9fa", "bar": "#6c63ff", "accent": "#ff6584", "text": "#1a1a2e"}

_TEXT   = "#f0f0f0" if dark_mode else "#1a1a2e"
_BG     = "#1a1a2e" if dark_mode else "#f8f9fa"
_SIDE   = "#16213e" if dark_mode else "#e9ecef"
_INPUT  = "#2a2a4a" if dark_mode else "#ffffff"
_BTN_BG = "#7c83fd" if dark_mode else "#6c63ff"

st.markdown(f"""
    <style>
        .stApp {{ background-color: {_BG} !important; }}
        [data-testid="stSidebar"] {{ background-color: {_SIDE} !important; }}
        .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
        .stApp label, .stApp span, .stApp caption,
        .stApp li, .stApp ul, .stApp ol,
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span {{ color: {_TEXT} !important; }}
        [data-testid="stMetricLabel"] p,
        [data-testid="stMetricValue"],
        [data-testid="stMetricDelta"] {{ color: {_TEXT} !important; }}
        [data-testid="stTextArea"] textarea {{
            background-color: {_INPUT} !important;
            color: {_TEXT} !important;
        }}
        [data-testid="stTextArea"] textarea::placeholder {{
            color: {"#aaaaaa" if dark_mode else "#999999"} !important;
            opacity: 1 !important;
        }}
        [data-testid="stButton"] > button {{
            background-color: {_BTN_BG} !important;
            color: #ffffff !important;
            border: none !important;
        }}
        [data-testid="stSelectbox"] > div > div {{
            background-color: {_INPUT} !important;
            color: {_TEXT} !important;
        }}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------

st.title("German Data Science Job Market Analyzer")
st.write("Analyzing 1,240 German data science job postings from LinkedIn (January 2026)")
st.caption("Entity extraction via **LangExtract** (gemini-2.5-flash-lite, few-shot) — no fine-tuning required")

summary = results["summary"]

# ---------------------------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Jobs",       f"{summary['total_jobs']:,}")
col2.metric("Unique Skills",    f"{summary['total_unique_skills']:,}")
col3.metric("Unique Tools",     f"{summary['total_unique_tools']:,}")
col4.metric("Avg Skills / Job", f"{summary['avg_skills_per_job']:.1f}")

st.divider()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_overview, tab_lang, tab_gap, tab_codep, tab_excl, tab_conc = st.tabs(["Overview", "Language Comparison", "Skill Gap by Seniority", "Tool-Skill Co-dependency", "Skill Exclusivity Index", "Company Concentration"])

# ===========================================================================
# Tab: Overview  (all original sections)
# ===========================================================================

with tab_overview:

    # -----------------------------------------------------------------------
    # Top 20 skills and tools
    # -----------------------------------------------------------------------

    level_label = f" — {selected_level}" if selected_level != "All" else ""

    col_skills, col_tools = st.columns(2)

    raw_skills   = (
        results["skills_by_experience_level"][selected_level]
        if selected_level != "All"
        else results["top_skills"]
    )
    skills_clean = filter_noise(raw_skills)[:20]

    raw_tools    = (
        results["tools_by_experience_level"][selected_level]
        if selected_level != "All"
        else results["top_tools"]
    )
    tools_clean  = filter_noise(raw_tools)[:20]

    with col_skills:
        st.subheader(f"Top 20 Skills{level_label}")
        st.plotly_chart(
            make_bar([r["name"] for r in skills_clean], [r["count"] for r in skills_clean], theme["bar"], theme["text"]),
            use_container_width=True,
        )
        st.caption("Extracted by LangExtract (gemini-2.5-flash-lite) with 2 few-shot examples")

    with col_tools:
        st.subheader(f"Top 20 Tools{level_label}")
        st.plotly_chart(
            make_bar([r["name"] for r in tools_clean], [r["count"] for r in tools_clean], theme["bar"], theme["text"]),
            use_container_width=True,
        )
        st.caption("Extracted by LangExtract (gemini-2.5-flash-lite) with 2 few-shot examples")

    st.divider()

    # -----------------------------------------------------------------------
    # Seniority distribution
    # -----------------------------------------------------------------------

    st.subheader("Jobs by Experience Level")

    value_dist = exp_analysis["value_distribution"]
    seniority  = sorted(value_dist.items(), key=lambda x: x[1]["count"], reverse=True)
    st.plotly_chart(
        make_bar([k for k, _ in seniority], [v["count"] for _, v in seniority], theme["bar"], theme["text"]),
        use_container_width=True,
    )
    st.caption("Source: LinkedIn experienceLevel field (100% complete)")

    st.divider()

    # -----------------------------------------------------------------------
    # Skill co-occurrence
    # -----------------------------------------------------------------------

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

    # -----------------------------------------------------------------------
    # Live: Analyze a Job Posting
    # -----------------------------------------------------------------------

    st.subheader("Analyze a Job Posting")

    api_key_ok = _setup_api_key()
    if not api_key_ok:
        st.warning("LANGEXTRACT_API_KEY not found in .env — live analysis unavailable.")

    job_text = st.text_area(
        "Paste a job posting here",
        height=250,
        placeholder="Paste any German or English job posting text…",
        disabled=not api_key_ok,
    )

    if st.button("Extract Skills & Tools", disabled=not api_key_ok):
        if not job_text.strip():
            st.warning("Please paste some job posting text first.")
        else:
            with st.spinner("Calling LangExtract (gemini-2.5-flash-lite)…"):
                try:
                    result = lx.extract(
                        text_or_documents=job_text,
                        prompt_description=_PROMPT,
                        examples=_EXAMPLES,
                        model_id=LANGEXTRACT_MODEL,
                        fence_output=True,
                        use_schema_constraints=True,
                    )
                    skills = sorted(
                        {e.extraction_text for e in result.extractions if e.extraction_class == "SKILL"},
                        key=str.lower,
                    )
                    tools = sorted(
                        {e.extraction_text for e in result.extractions if e.extraction_class == "TOOL"},
                        key=str.lower,
                    )
                    error = None
                except Exception as exc:
                    skills, tools, error = [], [], str(exc)

            if error:
                st.error(f"LangExtract failed: {error}")
            else:
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

# ===========================================================================
# Tab: Language Comparison
# ===========================================================================

with tab_lang:
    st.subheader("Skills & Tools by Posting Language")
    # Entities are normalized with .lower().strip() so variants like
    # 'Machine Learning' and 'machine learning' merge into one bar.
    if not LANG_COMPARE_PATH.exists():
        st.error(
            f"**Language comparison file not found:** `{LANG_COMPARE_PATH}`\n\n"
            "Run the script first:\n"
            "```\npython scripts/12_language_comparison.py\n```"
        )
    else:
        lang_data = load_language_comparison()

        german_skills  = normalize_and_merge(lang_data["german"]["skills"])
        german_tools   = normalize_and_merge(lang_data["german"]["tools"])
        english_skills = normalize_and_merge(lang_data["english"]["skills"])
        english_tools  = normalize_and_merge(lang_data["english"]["tools"])

        col_de, col_en = st.columns(2)

        with col_de:
            st.markdown("### 🇩🇪 German postings (550 jobs)")

            st.subheader("Top 20 Skills")
            st.plotly_chart(
                make_bar(
                    [r["entity"] for r in german_skills],
                    [r["count"]  for r in german_skills],
                    theme["bar"], theme["text"],
                ),
                use_container_width=True,
            )

            st.subheader("Top 20 Tools")
            st.plotly_chart(
                make_bar(
                    [r["entity"] for r in german_tools],
                    [r["count"]  for r in german_tools],
                    theme["bar"], theme["text"],
                ),
                use_container_width=True,
            )

        with col_en:
            st.markdown("### 🇬🇧 English postings (690 jobs)")

            st.subheader("Top 20 Skills")
            st.plotly_chart(
                make_bar(
                    [r["entity"] for r in english_skills],
                    [r["count"]  for r in english_skills],
                    theme["bar"], theme["text"],
                ),
                use_container_width=True,
            )

            st.subheader("Top 20 Tools")
            st.plotly_chart(
                make_bar(
                    [r["entity"] for r in english_tools],
                    [r["count"]  for r in english_tools],
                    theme["bar"], theme["text"],
                ),
                use_container_width=True,
            )

    st.divider()

    # -----------------------------------------------------------------------
    # German Language Requirements by Seniority
    # -----------------------------------------------------------------------

    st.subheader("German Language Requirements by Seniority")

    SENIORITY_ORDER = [
        "Entry level", "Internship", "Associate",
        "Mid-Senior level", "Director", "Executive", "Not Applicable",
    ]
    GERMAN_LEVEL_COLS = [
        ("C1/C2",                "C1/C2 Fluent/Native"),
        ("B2",                   "B2 Upper Intermediate"),
        ("B1",                   "B1 Intermediate"),
        ("nice_to_have",         "Nice to have"),
        ("mentioned_unspecified","Mentioned unspecified"),
        ("not_mentioned",        "Not mentioned"),
    ]

    matrix = load_german_level_by_seniority()

    col_keys   = [k for k, _ in GERMAN_LEVEL_COLS]
    col_labels = [l for _, l in GERMAN_LEVEL_COLS]

    GERMAN_KEYS = {"C1/C2", "B2", "B1", "nice_to_have", "mentioned_unspecified"}

    # Build pct matrix: rows=seniority, cols=german_level + separator + summary
    z_vals  = []
    z_text  = []
    for exp in SENIORITY_ORDER:
        total = sum(matrix.get(exp, {}).values()) or 1
        row_vals = [matrix.get(exp, {}).get(k, 0) / total * 100 for k in col_keys]
        any_german = sum(matrix.get(exp, {}).get(k, 0) for k in GERMAN_KEYS) / total * 100
        # Insert a NaN separator then the summary column
        row_vals  = row_vals + [float("nan"), any_german]
        z_vals.append(row_vals)
        z_text.append([f"{v:.1f}%" if not (v != v) else "" for v in row_vals])

    x_labels = col_labels + ["", "Any German Mentioned"]

    heatmap_fig = go.Figure(go.Heatmap(
        z=z_vals,
        x=x_labels,
        y=SENIORITY_ORDER,
        text=z_text,
        texttemplate="%{text}",
        textfont={"size": 12},
        colorscale="Blues",
        showscale=True,
        colorbar={"ticksuffix": "%", "tickfont": {"color": theme["text"]}},
    ))
    heatmap_fig.update_layout(
        title={"text": "German Language Requirements by Seniority (%)", "font": {"color": theme["text"]}},
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": theme["text"]},
        xaxis={"tickfont": {"color": theme["text"]}, "side": "bottom"},
        yaxis={"tickfont": {"color": theme["text"]}, "autorange": "reversed"},
        margin={"l": 10, "r": 10, "t": 40, "b": 10},
    )
    st.plotly_chart(heatmap_fig, use_container_width=True)

    # Insight callouts
    ins1, ins2, ins3 = st.columns(3)
    with ins1:
        st.info("**Associate and Mid-Senior roles** have the highest German language exposure — 65% and 62% mention it in some form")
    with ins2:
        st.info("**Director roles** are the exception: only 42% mention German, the lowest of any level")
    with ins3:
        st.info("**Executive roles** show 71% German mention — but with only 7 postings, treat this with caution")

# ===========================================================================
# Tab: Skill Gap by Seniority
# ===========================================================================

with tab_gap:

    sen_levels = seniority_analysis["levels"]
    available_levels = [
        lvl for lvl in ["Internship", "Entry level", "Associate", "Mid-Senior level", "Director"]
        if lvl in sen_levels
    ]

    # -----------------------------------------------------------------------
    # Section 1: Top Skills & Tools by Level
    # -----------------------------------------------------------------------

    st.subheader("Top Skills & Tools by Level")

    selected_sen_level = st.selectbox(
        "Experience level",
        options=available_levels,
        key="seniority_level_select",
    )

    level_data = sen_levels[selected_sen_level]
    total_jobs = level_data["total_jobs"]
    st.caption(f"{total_jobs:,} job postings at {selected_sen_level} level")

    top_skills_10 = level_data["top_skills"][:10]
    top_tools_10  = level_data["top_tools"][:10]

    col_s, col_t = st.columns(2)

    with col_s:
        st.markdown("**Top 10 Skills**")
        fig_skills = make_bar(
            [r["name"] for r in reversed(top_skills_10)],
            [r["pct"]  for r in reversed(top_skills_10)],
            theme["bar"], theme["text"],
            x_title="% of job postings",
            height=380,
            horizontal=True,
        )
        fig_skills.update_layout(yaxis={"autorange": True, "tickfont": {"color": theme["text"]}})
        st.plotly_chart(fig_skills, use_container_width=True)

    with col_t:
        st.markdown("**Top 10 Tools**")
        fig_tools = make_bar(
            [r["name"] for r in reversed(top_tools_10)],
            [r["pct"]  for r in reversed(top_tools_10)],
            theme["accent"], theme["text"],
            x_title="% of job postings",
            height=380,
            horizontal=True,
        )
        fig_tools.update_layout(yaxis={"autorange": True, "tickfont": {"color": theme["text"]}})
        st.plotly_chart(fig_tools, use_container_width=True)

    st.divider()

    # -----------------------------------------------------------------------
    # Section 2: Evergreen Skills & Tools
    # -----------------------------------------------------------------------

    st.subheader("Required at Every Seniority Level")
    st.caption("Skills and tools in the top 20 for all qualifying experience levels (≥ 10 jobs)")

    qualifying_levels = [lvl for lvl in available_levels if sen_levels[lvl]["total_jobs"] >= 10]

    def _avg_pct(name, key):
        pcts = []
        for lvl in qualifying_levels:
            for entry in sen_levels[lvl][key]:
                if entry["name"] == name:
                    pcts.append(entry["pct"])
                    break
        return sum(pcts) / len(pcts) if pcts else 0

    eg_skills_pct = sorted(
        [{"name": s, "pct": _avg_pct(s, "top_skills")} for s in seniority_analysis["evergreen_skills"]],
        key=lambda x: x["pct"],
    )
    eg_tools_pct = sorted(
        [{"name": t, "pct": _avg_pct(t, "top_tools")} for t in seniority_analysis["evergreen_tools"]],
        key=lambda x: x["pct"],
    )

    col_eg_s, col_eg_t = st.columns(2)

    with col_eg_s:
        st.markdown("**Evergreen Skills**")
        fig_eg_s = make_bar(
            [r["name"] for r in eg_skills_pct],
            [r["pct"]  for r in eg_skills_pct],
            theme["bar"], theme["text"],
            x_title="avg % of job postings",
            height=300,
            horizontal=True,
        )
        fig_eg_s.update_layout(yaxis={"autorange": True, "tickfont": {"color": theme["text"]}})
        st.plotly_chart(fig_eg_s, use_container_width=True)

    with col_eg_t:
        st.markdown("**Evergreen Tools**")
        fig_eg_t = make_bar(
            [r["name"] for r in eg_tools_pct],
            [r["pct"]  for r in eg_tools_pct],
            theme["accent"], theme["text"],
            x_title="avg % of job postings",
            height=300,
            horizontal=True,
        )
        fig_eg_t.update_layout(yaxis={"autorange": True, "tickfont": {"color": theme["text"]}})
        st.plotly_chart(fig_eg_t, use_container_width=True)

    st.divider()

    # -----------------------------------------------------------------------
    # Section 3: Entry vs Senior Contrast
    # -----------------------------------------------------------------------

    st.subheader("Entry vs Senior Contrast")

    col_entry, col_senior = st.columns(2)

    with col_entry:
        st.markdown("**Entry / Internship Only**")
        st.caption("In top 20 for Internship or Entry level — not for Director or Executive")
        entry_only = seniority_analysis["entry_only_skills"]
        if entry_only:
            st.dataframe({"Skill": entry_only}, use_container_width=True, hide_index=True)
        else:
            st.write("None found.")

    with col_senior:
        st.markdown("**Director Only**")
        st.caption("In top 20 for Director or Executive — not for Internship or Entry level")
        senior_only = seniority_analysis["senior_only_skills"]
        if senior_only:
            st.dataframe({"Skill": senior_only}, use_container_width=True, hide_index=True)
        else:
            st.write("None found.")

# ===========================================================================
# Tab: Tool-Skill Co-dependency
# ===========================================================================

with tab_codep:

    # -----------------------------------------------------------------------
    # Section 1: Top Tool-Skill Pairs
    # -----------------------------------------------------------------------

    st.subheader("Top Tool-Skill Pairs")
    st.caption("Pairs ranked by how often both appear in the same job posting")

    top20 = codep["top_pairs_by_co_count"][:20]
    pair_labels = [f"{p['tool']} + {p['skill']}" for p in reversed(top20)]
    pair_counts = [p["co_count"] for p in reversed(top20)]

    fig_pairs = make_bar(
        pair_labels, pair_counts,
        theme["bar"], theme["text"],
        x_title="Jobs where both appear",
        height=560,
        horizontal=True,
    )
    fig_pairs.update_layout(yaxis={"autorange": True, "tickfont": {"color": theme["text"]}})
    st.plotly_chart(fig_pairs, use_container_width=True)

    st.divider()

    # -----------------------------------------------------------------------
    # Section 2: Explore by Tool
    # -----------------------------------------------------------------------

    st.subheader("Explore by Tool")
    st.caption("Jaccard score measures how often this skill appears *only* alongside this tool.")

    tool_list = sorted(codep["by_tool"].keys())
    selected_tool = st.selectbox("Select a tool", options=tool_list, key="codep_tool_select")

    companions = codep["by_tool"][selected_tool]
    if companions:
        comp_labels  = [c["skill"]   for c in reversed(companions)]
        comp_jaccard = [c["jaccard"] for c in reversed(companions)]

        fig_comp = make_bar(
            comp_labels, comp_jaccard,
            theme["accent"], theme["text"],
            x_title="Jaccard score (how exclusively they appear together)",
            height=300,
            horizontal=True,
        )
        fig_comp.update_layout(yaxis={"autorange": True, "tickfont": {"color": theme["text"]}})
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.write("No companions found for this tool.")

# ===========================================================================
# Tab: Skill Exclusivity Index
# ===========================================================================

with tab_excl:

    # -----------------------------------------------------------------------
    # Section 1: Scatter plot
    # -----------------------------------------------------------------------

    st.subheader("Skill Exclusivity Index")
    st.caption("Rare skills score high; ubiquitous skills score low.")

    _COLOR_MAP = {
        "commodity": theme["accent"],
        "mid-range": theme["bar"],
        "niche":     "#888888",
    }

    _skills = excl["skills"]

    scatter_fig = go.Figure()
    for cat, cat_label in [("commodity", "Commodity"), ("mid-range", "Mid-Range"), ("niche", "Niche")]:
        pts = [s for s in _skills if s["category"] == cat]
        scatter_fig.add_trace(go.Scatter(
            x=[s["frequency"]   for s in pts],
            y=[s["exclusivity"] for s in pts],
            mode="markers",
            name=cat_label,
            marker={"color": _COLOR_MAP[cat], "size": 8, "opacity": 0.8},
            text=[s["name"] for s in pts],
            hovertemplate="<b>%{text}</b><br>Frequency: %{x:.1f}%<br>Exclusivity: %{y:.1f}<extra></extra>",
        ))

    # Boundary reference lines
    y_range = [85, 101]
    for x_val, label in [(2, "2% — niche boundary"), (10, "10% — commodity boundary")]:
        scatter_fig.add_vline(
            x=x_val,
            line_dash="dash",
            line_color="#aaaaaa",
            line_width=1,
            annotation_text=label,
            annotation_position="top",
            annotation_font={"color": theme["text"], "size": 11},
        )

    scatter_fig.update_layout(
        height=480,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": theme["text"]},
        xaxis={
            "title": "Frequency (% of job postings)",
            "tickfont": {"color": theme["text"]},
            "gridcolor": "#333333" if dark_mode else "#dddddd",
        },
        yaxis={
            "title": "Exclusivity score",
            "tickfont": {"color": theme["text"]},
            "gridcolor": "#333333" if dark_mode else "#dddddd",
        },
        legend={"font": {"color": theme["text"]}},
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
    )
    st.plotly_chart(scatter_fig, use_container_width=True)

    st.divider()

    # -----------------------------------------------------------------------
    # Section 2: Category breakdown
    # -----------------------------------------------------------------------

    st.subheader("Category Breakdown")

    col_com, col_mid, col_niche = st.columns(3)

    with col_com:
        st.markdown(f"**Commodity (≥10%)** — {len(excl['commodity'])} skills")
        st.dataframe(
            [{"Skill": s["name"], "Freq %": s["frequency"]} for s in excl["commodity"]],
            use_container_width=True,
            hide_index=True,
        )

    with col_mid:
        st.markdown(f"**Mid-Range (2–10%)** — top 15 of {len(excl['mid_range'])}")
        st.dataframe(
            [{"Skill": s["name"], "Freq %": s["frequency"]} for s in excl["mid_range"][:15]],
            use_container_width=True,
            hide_index=True,
        )

    with col_niche:
        st.markdown(f"**Niche (≤2%)** — top 15 of {len(excl['niche'])}")
        st.dataframe(
            [{"Skill": s["name"], "Freq %": s["frequency"]} for s in excl["niche"][:15]],
            use_container_width=True,
            hide_index=True,
        )

# ===========================================================================
# Tab: Company Concentration
# ===========================================================================

with tab_conc:

    # -----------------------------------------------------------------------
    # Section 1: Top 20 Companies by Posting Count
    # -----------------------------------------------------------------------

    st.subheader("Top 20 Companies by Posting Count")

    top_companies = conc["top_companies"]
    comp_names  = [c["company"] for c in reversed(top_companies)]
    comp_counts = [c["count"]   for c in reversed(top_companies)]

    fig_companies = make_bar(
        comp_names, comp_counts,
        theme["bar"], theme["text"],
        x_title="Number of job postings",
        height=560,
        horizontal=True,
    )
    fig_companies.update_layout(yaxis={"autorange": True, "tickfont": {"color": theme["text"]}})
    st.plotly_chart(fig_companies, use_container_width=True)

    st.divider()

    # -----------------------------------------------------------------------
    # Section 2 & 3: Skill & Tool Concentration Tables
    # -----------------------------------------------------------------------

    st.warning(
        "Skills or tools highlighted in red appear popular in aggregate but are heavily driven "
        "by a single company's hiring templates. Interpret with caution."
    )

    def _conc_table(rows, accent_hex):
        df = pd.DataFrame([
            {
                "Skill":       r["name"],
                "Jobs":        r["raw_count"],
                "Companies":   r["unique_companies"],
                "Top Company": r["top_company"],
                "Conc %":      round(r["concentration_pct"], 1),
            }
            for r in sorted(rows, key=lambda x: x["raw_count"], reverse=True)
        ])

        def _highlight(row):
            bg = f"background-color: {accent_hex}40" if row["Conc %"] > 30 else ""
            return [bg] * len(row)

        st.dataframe(
            df.style.apply(_highlight, axis=1).format({"Conc %": "{:.1f}"}),
            use_container_width=True,
            hide_index=True,
        )

    col_sc, col_tc = st.columns(2)

    with col_sc:
        st.markdown("**Skill Concentration**")
        _conc_table(conc["skill_concentration"], theme["accent"])

    with col_tc:
        st.markdown("**Tool Concentration**")
        _conc_table(conc["tool_concentration"], theme["accent"])

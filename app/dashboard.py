import json
import pathlib
import pandas as pd
import streamlit as st

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


# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="German Data Science Job Market Analyzer",
    layout="wide",
)

st.title("German Data Science Job Market Analyzer")

results, exp_analysis = load_data()
summary = results["summary"]

# ── Summary metrics ───────────────────────────────────────────────────────────

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Jobs", f"{summary['total_jobs']:,}")
col2.metric("Unique Skills", f"{summary['total_unique_skills']:,}")
col3.metric("Unique Tools", f"{summary['total_unique_tools']:,}")
col4.metric("Avg Skills / Job", f"{summary['avg_skills_per_job']:.1f}")

st.divider()

# ── Top 20 skills ─────────────────────────────────────────────────────────────

st.subheader("Top 20 Skills")

skills_df = (
    pd.DataFrame(filter_noise(results["top_skills"]))
    .head(20)
    .set_index("name")
)
st.bar_chart(skills_df, y="count", use_container_width=True)

st.divider()

# ── Top 20 tools ──────────────────────────────────────────────────────────────

st.subheader("Top 20 Tools")

tools_df = (
    pd.DataFrame(filter_noise(results["top_tools"]))
    .head(20)
    .set_index("name")
)
st.bar_chart(tools_df, y="count", use_container_width=True)

st.divider()

# ── Seniority distribution ────────────────────────────────────────────────────

st.subheader("Jobs by Experience Level")

value_dist = exp_analysis["value_distribution"]
seniority_df = pd.DataFrame(
    [
        {"level": level, "count": info["count"]}
        for level, info in sorted(
            value_dist.items(), key=lambda x: x[1]["count"], reverse=True
        )
    ]
).set_index("level")

st.bar_chart(seniority_df, y="count", use_container_width=True)

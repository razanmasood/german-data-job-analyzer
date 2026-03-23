import json
from collections import defaultdict
from itertools import product

INPUT_PATH = "data/processed/langextract_inference_results.json"
OUTPUT_PATH = "data/processed/tool_skill_codependency.json"

STOPLIST = {
    "data science", "data scientist", "machine learning", "ml", "ai",
    "artificial intelligence", "data analysis", "data analytics",
    "data engineer", "data engineering",
    "ki", "künstliche intelligenz", "maschinelles lernen",
    "computer science",
}

with open(INPUT_PATH) as f:
    jobs = json.load(f)

# Per-job normalized sets
job_tools = []
job_skills = []
for job in jobs:
    tools  = {t.lower().strip() for t in job.get("tools",  [])} - STOPLIST
    skills = {s.lower().strip() for s in job.get("skills", [])} - STOPLIST
    job_tools.append(tools)
    job_skills.append(skills)

# Individual occurrence counts
tool_counts  = defaultdict(int)
skill_counts = defaultdict(int)
for tools, skills in zip(job_tools, job_skills):
    for t in tools:
        tool_counts[t] += 1
    for s in skills:
        skill_counts[s] += 1

# Co-occurrence counts
co_counts = defaultdict(int)
for tools, skills in zip(job_tools, job_skills):
    for tool, skill in product(tools, skills):
        co_counts[(tool, skill)] += 1

# Build full pair list with jaccard
pairs = []
for (tool, skill), co_count in co_counts.items():
    jt = tool_counts[tool]
    js = skill_counts[skill]
    jaccard = co_count / (jt + js - co_count)
    pairs.append({
        "tool":     tool,
        "skill":    skill,
        "co_count": co_count,
        "jaccard":  round(jaccard, 4),
        "jobs_with_tool":  jt,
        "jobs_with_skill": js,
    })

# Filter to pairs with sufficient co-occurrence
filtered_pairs = [p for p in pairs if p["co_count"] >= 15]

# Top 50 by co_count
top_by_co = sorted(filtered_pairs, key=lambda x: x["co_count"], reverse=True)[:50]
top_by_co_out = [
    {"tool": p["tool"], "skill": p["skill"], "co_count": p["co_count"], "jaccard": p["jaccard"]}
    for p in top_by_co
]

# by_tool index: top 5 skill companions per tool by jaccard
by_tool_raw = defaultdict(list)
for p in filtered_pairs:
    by_tool_raw[p["tool"]].append(p)

by_tool = {
    tool: [
        {"skill": p["skill"], "co_count": p["co_count"], "jaccard": p["jaccard"]}
        for p in sorted(companions, key=lambda x: x["jaccard"], reverse=True)[:5]
    ]
    for tool, companions in by_tool_raw.items()
}

output = {
    "top_pairs_by_co_count": top_by_co_out,
    "by_tool": by_tool,
}

with open(OUTPUT_PATH, "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Saved to {OUTPUT_PATH}")
print(f"Total unique (tool, skill) pairs: {len(pairs):,}\n")

print("Top 15 by co_count:")
print(f"  {'Tool':<20} {'Skill':<30} {'Co-count':>8}  {'Jaccard':>7}")
print("  " + "-" * 70)
for p in sorted(pairs, key=lambda x: x["co_count"], reverse=True)[:15]:
    print(f"  {p['tool']:<20} {p['skill']:<30} {p['co_count']:>8}  {p['jaccard']:>7.3f}")

print("\nTop 15 by jaccard (min co_count >= 15):")
print(f"  {'Tool':<20} {'Skill':<30} {'Co-count':>8}  {'Jaccard':>7}")
print("  " + "-" * 70)
for p in sorted(filtered_pairs, key=lambda x: x["jaccard"], reverse=True)[:15]:
    print(f"  {p['tool']:<20} {p['skill']:<30} {p['co_count']:>8}  {p['jaccard']:>7.3f}")

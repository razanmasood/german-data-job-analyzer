import json
from collections import defaultdict

INPUT_PATH = "data/processed/langextract_inference_results.json"
OUTPUT_PATH = "data/processed/seniority_analysis.json"

STOPLIST = {
    "data science", "data scientist", "machine learning", "ml", "ai",
    "artificial intelligence", "data analysis", "data analytics",
    "data engineer", "data engineering",
    "ki", "künstliche intelligenz", "maschinelles lernen",
    "computer science",
}

LEVEL_ORDER = [
    "Internship",
    "Entry level",
    "Associate",
    "Mid-Senior level",
    "Director",
    "Executive",
]

with open(INPUT_PATH) as f:
    jobs = json.load(f)

# Aggregate per level
level_skill_counts = defaultdict(lambda: defaultdict(int))
level_tool_counts = defaultdict(lambda: defaultdict(int))
level_total = defaultdict(int)

for job in jobs:
    level = job.get("experience_level", "")
    if not level or level == "Not Applicable":
        continue

    level_total[level] += 1

    for skill in set(s.lower().strip() for s in job.get("skills", [])) - STOPLIST:
        level_skill_counts[level][skill] += 1

    for tool in set(t.lower().strip() for t in job.get("tools", [])) - STOPLIST:
        level_tool_counts[level][tool] += 1

# Build per-level results
levels_output = {}
level_top_skills = {}  # level -> set of top-20 skill names
level_top_tools = {}   # level -> set of top-20 tool names

for level in LEVEL_ORDER:
    total = level_total.get(level, 0)
    if total == 0:
        continue

    skill_counts = level_skill_counts[level]
    tool_counts = level_tool_counts[level]

    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    top_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:20]

    top_skills_out = [
        {"name": name, "count": count, "pct": round(count / total * 100, 1)}
        for name, count in top_skills
    ]
    top_tools_out = [
        {"name": name, "count": count, "pct": round(count / total * 100, 1)}
        for name, count in top_tools
    ]

    levels_output[level] = {
        "total_jobs": total,
        "top_skills": top_skills_out,
        "top_tools": top_tools_out,
    }

    level_top_skills[level] = {s["name"] for s in top_skills_out}
    level_top_tools[level] = {t["name"] for t in top_tools_out}

# Qualifying levels (>= 10 jobs)
qualifying = [lvl for lvl in LEVEL_ORDER if level_total.get(lvl, 0) >= 10 and lvl in levels_output]

# Evergreen: in top 20 for ALL qualifying levels
if qualifying:
    evergreen_skills = set(level_top_skills[qualifying[0]])
    evergreen_tools = set(level_top_tools[qualifying[0]])
    for lvl in qualifying[1:]:
        evergreen_skills &= level_top_skills[lvl]
        evergreen_tools &= level_top_tools[lvl]
else:
    evergreen_skills = set()
    evergreen_tools = set()

# Entry levels and senior levels (only those that qualify)
entry_levels = [lvl for lvl in ["Internship", "Entry level"] if lvl in level_top_skills]
senior_levels = [lvl for lvl in ["Director", "Executive"] if lvl in level_top_skills]

entry_skill_sets = [level_top_skills[lvl] for lvl in entry_levels]
senior_skill_sets = [level_top_skills[lvl] for lvl in senior_levels]

if entry_skill_sets:
    entry_union = set().union(*entry_skill_sets)
else:
    entry_union = set()

if senior_skill_sets:
    senior_union = set().union(*senior_skill_sets)
else:
    senior_union = set()

entry_only_skills = sorted(entry_union - senior_union)
senior_only_skills = sorted(senior_union - entry_union)

output = {
    "levels": levels_output,
    "evergreen_skills": sorted(evergreen_skills),
    "evergreen_tools": sorted(evergreen_tools),
    "entry_only_skills": entry_only_skills,
    "senior_only_skills": senior_only_skills,
}

with open(OUTPUT_PATH, "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Saved to {OUTPUT_PATH}\n")
print(f"{'Level':<20} {'Jobs':>6}  Top 5 skills")
print("-" * 80)
for level in LEVEL_ORDER:
    if level not in levels_output:
        continue
    data = levels_output[level]
    top5 = ", ".join(
        f"{s['name']} ({s['pct']}%)" for s in data["top_skills"][:5]
    )
    print(f"{level:<20} {data['total_jobs']:>6}  {top5}")

print()
print(f"Evergreen skills ({len(evergreen_skills)}): {', '.join(sorted(evergreen_skills)) or 'none'}")
print(f"Evergreen tools  ({len(evergreen_tools)}): {', '.join(sorted(evergreen_tools)) or 'none'}")
print(f"Entry-only skills ({len(entry_only_skills)}): {', '.join(entry_only_skills) or 'none'}")
print(f"Senior-only skills ({len(senior_only_skills)}): {', '.join(senior_only_skills) or 'none'}")

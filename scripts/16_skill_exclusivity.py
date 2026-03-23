import json
from collections import defaultdict

INPUT_PATH = "data/processed/langextract_inference_results.json"
OUTPUT_PATH = "data/processed/skill_exclusivity.json"

STOPLIST = {
    "data science", "data scientist", "machine learning", "ml", "ai",
    "artificial intelligence", "data analysis", "data analytics",
    "data engineer", "data engineering", "ki", "künstliche intelligenz",
    "maschinelles lernen", "computer science",
}

with open(INPUT_PATH) as f:
    jobs = json.load(f)

total_jobs = len(jobs)

skill_counts = defaultdict(int)
for job in jobs:
    for skill in set(s.lower().strip() for s in job.get("skills", [])) - STOPLIST:
        skill_counts[skill] += 1

# Build skill list (min 10 jobs)
skills = []
for name, count in skill_counts.items():
    if count < 10:
        continue
    frequency = round(count / total_jobs * 100, 2)
    exclusivity = round(100 - frequency, 2)
    if frequency >= 10:
        category = "commodity"
    elif frequency <= 2:
        category = "niche"
    else:
        category = "mid-range"
    skills.append({
        "name": name,
        "count": count,
        "frequency": frequency,
        "exclusivity": exclusivity,
        "category": category,
    })

skills.sort(key=lambda x: x["frequency"], reverse=True)

commodity = [s for s in skills if s["category"] == "commodity"]
niche     = [s for s in skills if s["category"] == "niche"]
mid_range = [s for s in skills if s["category"] == "mid-range"]

output = {
    "skills": skills,
    "commodity": commodity,
    "niche": niche,
    "mid_range": mid_range,
}

with open(OUTPUT_PATH, "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Saved to {OUTPUT_PATH}")
print(f"Total jobs: {total_jobs}  |  Skills with >= 10 mentions: {len(skills)}")
print(f"  Commodity (freq >= 10%): {len(commodity)}")
print(f"  Mid-range (2% < freq < 10%): {len(mid_range)}")
print(f"  Niche     (freq <= 2%): {len(niche)}")

print(f"\nTop 10 commodity skills:")
print(f"  {'Skill':<35} {'Count':>6}  {'Freq%':>6}")
print("  " + "-" * 52)
for s in commodity[:10]:
    print(f"  {s['name']:<35} {s['count']:>6}  {s['frequency']:>6.1f}%")

print(f"\nTop 10 niche skills (by frequency):")
print(f"  {'Skill':<35} {'Count':>6}  {'Freq%':>6}")
print("  " + "-" * 52)
for s in niche[:10]:
    print(f"  {s['name']:<35} {s['count']:>6}  {s['frequency']:>6.1f}%")

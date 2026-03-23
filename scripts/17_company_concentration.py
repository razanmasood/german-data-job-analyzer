import json
from collections import Counter, defaultdict

JOBS_PATH   = "data/processed/jobs_combined_clean.json"
NER_PATH    = "data/processed/langextract_inference_results.json"
OUTPUT_PATH = "data/processed/company_concentration.json"

STOPLIST = {
    "data science", "data scientist", "machine learning", "ml", "ai",
    "artificial intelligence", "data analysis", "data analytics",
    "data engineer", "data engineering", "ki", "künstliche intelligenz",
    "maschinelles lernen", "computer science",
}

with open(JOBS_PATH) as f:
    jobs_raw = json.load(f)

with open(NER_PATH) as f:
    ner_results = json.load(f)

# Build id -> companyName lookup
id_to_company = {job["id"]: job.get("companyName", "Unknown") for job in jobs_raw}

# Join and normalize
records = []
for ner in ner_results:
    job_id  = ner["id"]
    company = id_to_company.get(job_id, "Unknown")
    skills  = set(s.lower().strip() for s in ner.get("skills", [])) - STOPLIST
    tools   = set(t.lower().strip() for t in ner.get("tools",  [])) - STOPLIST
    records.append({"company": company, "skills": skills, "tools": tools})

# Top 20 companies by posting count
company_counts = Counter(r["company"] for r in records)
top_companies = [
    {"company": name, "count": count}
    for name, count in company_counts.most_common(20)
]

# Overall skill/tool counts to pick top 30
skill_total = Counter()
tool_total  = Counter()
for r in records:
    skill_total.update(r["skills"])
    tool_total.update(r["tools"])

top_skills_30 = [name for name, _ in skill_total.most_common(30)]
top_tools_30  = [name for name, _ in tool_total.most_common(30)]

def compute_concentration(entity_name, entity_key, records):
    # Per-job (not per-mention): one per job
    company_counter = Counter()
    unique_companies = set()
    raw_count = 0
    for r in records:
        if entity_name in r[entity_key]:
            raw_count += 1
            unique_companies.add(r["company"])
            company_counter[r["company"]] += 1
    top_company, top_company_count = company_counter.most_common(1)[0] if company_counter else ("", 0)
    concentration_pct = round(top_company_count / raw_count * 100, 1) if raw_count else 0
    return {
        "name":              entity_name,
        "raw_count":         raw_count,
        "unique_companies":  len(unique_companies),
        "top_company":       top_company,
        "top_company_count": top_company_count,
        "concentration_pct": concentration_pct,
        "concentrated":      concentration_pct > 30,
    }

skill_concentration = [compute_concentration(s, "skills", records) for s in top_skills_30]
tool_concentration  = [compute_concentration(t, "tools",  records) for t in top_tools_30]

output = {
    "top_companies":       top_companies,
    "skill_concentration": skill_concentration,
    "tool_concentration":  tool_concentration,
}

with open(OUTPUT_PATH, "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Saved to {OUTPUT_PATH}\n")

print("Top 10 companies by posting count:")
print(f"  {'Company':<40} {'Postings':>8}")
print("  " + "-" * 50)
for c in top_companies[:10]:
    print(f"  {c['company']:<40} {c['count']:>8}")

concentrated_skills = [s for s in skill_concentration if s["concentrated"]]
concentrated_tools  = [t for t in tool_concentration  if t["concentrated"]]

print(f"\nConcentrated skills (top_company > 30% of mentions): {len(concentrated_skills)}")
if concentrated_skills:
    print(f"  {'Skill':<30} {'Total':>6}  {'Top Company':<35} {'Count':>6}  {'Conc%':>6}")
    print("  " + "-" * 88)
    for s in sorted(concentrated_skills, key=lambda x: x["concentration_pct"], reverse=True):
        print(f"  {s['name']:<30} {s['raw_count']:>6}  {s['top_company']:<35} {s['top_company_count']:>6}  {s['concentration_pct']:>6.1f}%")

print(f"\nConcentrated tools (top_company > 30% of mentions): {len(concentrated_tools)}")
if concentrated_tools:
    print(f"  {'Tool':<30} {'Total':>6}  {'Top Company':<35} {'Count':>6}  {'Conc%':>6}")
    print("  " + "-" * 88)
    for t in sorted(concentrated_tools, key=lambda x: x["concentration_pct"], reverse=True):
        print(f"  {t['name']:<30} {t['raw_count']:>6}  {t['top_company']:<35} {t['top_company_count']:>6}  {t['concentration_pct']:>6.1f}%")

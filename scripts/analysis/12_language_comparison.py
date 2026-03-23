"""
Script: 12_language_comparison.py

Compares top skills and tools between German-language and English-language job postings.

Input:
    data/processed/jobs_combined_clean.json        (contains 'language' field per job)
    data/processed/langextract_inference_results.json  (contains 'skills' and 'tools' per job)

Output:
    data/processed/language_comparison.json
"""

import json
from collections import Counter
from pathlib import Path

JOBS_PATH       = Path("data/processed/jobs_combined_clean.json")
INFERENCE_PATH  = Path("data/processed/langextract_inference_results.json")
OUTPUT_PATH     = Path("data/processed/language_comparison.json")
TOP_N           = 20


def top_entities(counter, n=TOP_N):
    return [{"entity": name, "count": count} for name, count in counter.most_common(n)]


def main():
    # Load language labels
    with open(JOBS_PATH) as f:
        jobs = json.load(f)
    language_map = {job["id"]: job.get("language") for job in jobs}

    # Load inference results
    with open(INFERENCE_PATH) as f:
        inference = json.load(f)

    # Accumulate counts per language group
    skill_counters = {"German": Counter(), "English": Counter()}
    tool_counters  = {"German": Counter(), "English": Counter()}
    job_counts     = {"German": 0, "English": 0}

    for record in inference:
        lang = language_map.get(record["id"])
        if lang not in ("German", "English"):
            continue
        job_counts[lang] += 1
        skill_counters[lang].update(record.get("skills", []))
        tool_counters[lang].update(record.get("tools", []))

    results = {
        "german":  {"skills": top_entities(skill_counters["German"]),
                    "tools":  top_entities(tool_counters["German"])},
        "english": {"skills": top_entities(skill_counters["English"]),
                    "tools":  top_entities(tool_counters["English"])},
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Summary
    for lang_key, lang_label in [("german", "German"), ("english", "English")]:
        print(f"\n{lang_label}: {job_counts[lang_label]} jobs")
        print(f"  Top 5 skills: {[e['entity'] for e in results[lang_key]['skills'][:5]]}")
        print(f"  Top 5 tools:  {[e['entity'] for e in results[lang_key]['tools'][:5]]}")

    print(f"\nSaved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

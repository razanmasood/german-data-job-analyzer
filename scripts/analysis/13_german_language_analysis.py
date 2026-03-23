"""
Script: 13_german_language_analysis.py

Classifies each job posting by its German language requirement level and
adds two fields to data/processed/jobs_combined_clean.json in place:

    german_required  bool  — True if German is mentioned in any form
    german_level     str   — one of: C1/C2 | B2 | B1 | nice_to_have |
                                     mentioned_unspecified | not_mentioned

Priority order (first match wins):
    1. C1/C2              highest specificity
    2. B2
    3. B1
    4. nice_to_have
    5. mentioned_unspecified
    6. not_mentioned      fallback

Also prints a cross-tabulation of german_level × experienceLevel.

Input/Output:
    data/processed/jobs_combined_clean.json  (updated in place)
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

JOBS_PATH = Path("data/processed/jobs_combined_clean.json")

LEVELS = [
    ("C1/C2", [
        r"\bC2\b",
        r"\bC1\b",
        r"fließend",
        r"fluent.*german",
        r"german.*fluent",
        r"verhandlungssicher",
        r"muttersprachlich",
        r"native.*german",
    ]),
    ("B2", [r"\bB2\b"]),
    ("B1", [r"\bB1\b"]),
    ("nice_to_have", [
        r"von vorteil",
        r"advantageous",
        r"nice to have.*german",
        r"german.*nice to have",
        r"wünschenswert",
    ]),
    ("mentioned_unspecified", [
        r"\bgerman\b",
        r"\bdeutsch\b",
        r"deutschkenntnisse",
    ]),
]


def classify(job: dict) -> str:
    text = (job.get("description", "") + " " + job.get("title", "")).lower()
    for level, patterns in LEVELS:
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            return level
    return "not_mentioned"


def main():
    with open(JOBS_PATH, encoding="utf-8") as f:
        jobs = json.load(f)

    # --- 1. Classify and annotate ---
    for job in jobs:
        level = classify(job)
        job["german_level"] = level
        job["german_required"] = level != "not_mentioned"

    with open(JOBS_PATH, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

    level_order = [l for l, _ in LEVELS] + ["not_mentioned"]
    counts = Counter(j["german_level"] for j in jobs)

    print(f"Annotated {len(jobs)} jobs and saved to {JOBS_PATH}\n")
    print("german_level counts:")
    for level in level_order:
        print(f"  {level:<26} {counts[level]:>4}  ({counts[level]/len(jobs)*100:.1f}%)")

    # --- 2. Cross-tabulation ---
    exp_levels = sorted({j.get("experienceLevel", "Unknown") for j in jobs})
    matrix = defaultdict(Counter)
    for j in jobs:
        matrix[j["german_level"]][j.get("experienceLevel", "Unknown")] += 1

    col = 20
    row_w = 26
    print(f"\nCross-tabulation: german_level × experienceLevel\n")
    header = f"{'german_level':<{row_w}}" + "".join(f"{e[:col-2]:<{col}}" for e in exp_levels)
    print(header)
    print("-" * len(header))
    for gl in level_order:
        row = f"{gl:<{row_w}}" + "".join(f"{matrix[gl][e]:<{col}}" for e in exp_levels)
        print(row)


if __name__ == "__main__":
    main()

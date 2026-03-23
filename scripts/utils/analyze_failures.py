"""
Analyze the 7 job descriptions where requirements section extraction failed.

Input:  data/annotation/notfoundReqSec.txt  (7 failed job objects)
        data/annotation/sample_150.json     (original job data with description_clean)
Output: data/annotation/failure_analysis.txt
"""

import json
import re


def load_failed_jobs(path):
    """Load failed job objects from notfoundReqSec.txt."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # Try parsing as JSON array first
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Wrap bare objects in array brackets and strip trailing commas before ]
    wrapped = "[" + content.rstrip().rstrip(",") + "]"
    return json.loads(wrapped)


def load_sample_jobs(path):
    """Load original sample jobs and index by id."""
    with open(path, "r", encoding="utf-8") as f:
        jobs = json.load(f)
    return {job["id"]: job for job in jobs}


SECTION_HEADERS = [
    # English
    r"requirements",
    r"qualifications",
    r"skills",
    r"what you bring",
    r"your profile",
    r"what we are looking for",
    r"must have",
    r"nice to have",
    r"ideal candidate",
    # German
    r"anforderungen",
    r"qualifikationen",
    r"dein profil",
    r"das bringst du mit",
    r"was du mitbringst",
    r"was sie mitbringen",
    r"ihr profil",
]


def find_section_headers(text):
    """Return list of matching section header patterns found in the text."""
    text_lower = text.lower()
    return [h for h in SECTION_HEADERS if re.search(r"\b" + h + r"\b", text_lower)]


def analyze(failed_path, sample_path, output_path):
    failed_jobs = load_failed_jobs(failed_path)
    sample_index = load_sample_jobs(sample_path)

    lines = []

    def out(msg=""):
        print(msg)
        lines.append(msg)

    out("=" * 80)
    out("FAILURE ANALYSIS: Jobs with no requirements section detected")
    out(f"Total failed: {len(failed_jobs)}")
    out("=" * 80)

    for i, fj in enumerate(failed_jobs, 1):
        job_id = fj["id"]
        title = fj.get("jobTitle", "N/A")

        # Get description_clean from original sample data
        original = sample_index.get(job_id)
        if original:
            desc = original.get("description_clean", "")
        else:
            # Fall back to the description stored in the failed file
            desc = fj.get("description", "")

        num_paragraphs = len([p for p in desc.split("\n\n") if p.strip()])
        headers_found = find_section_headers(desc)
        first_200 = desc[:200].replace("\n", " ")

        out(f"\n{'─' * 80}")
        out(f"[{i}] Job ID:             {job_id}")
        out(f"    Title:              {title}")
        out(f"    Description length: {len(desc)} chars")
        out(f"    Paragraphs:         {num_paragraphs}")
        out(f"    Section headers:    {headers_found if headers_found else 'NONE FOUND'}")
        out(f"    First 200 chars:    {first_200}")

    out(f"\n{'=' * 80}")
    out("SUMMARY")
    out("=" * 80)

    has_headers = sum(1 for fj in failed_jobs if find_section_headers(
        sample_index.get(fj["id"], {}).get("description_clean", "")
        or fj.get("description", "")
    ))
    out(f"  Jobs with recognizable headers:    {has_headers}/{len(failed_jobs)}")
    out(f"  Jobs without any headers:          {len(failed_jobs) - has_headers}/{len(failed_jobs)}")

    lengths = []
    for fj in failed_jobs:
        original = sample_index.get(fj["id"])
        desc = (original.get("description_clean", "") if original
                else fj.get("description", ""))
        lengths.append(len(desc))
    out(f"  Avg description length:            {sum(lengths) / len(lengths):.0f} chars")
    out(f"  Min / Max length:                  {min(lengths)} / {max(lengths)} chars")
    out("=" * 80)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    analyze(
        failed_path="data/annotation/notfoundReqSec.txt",
        sample_path="data/annotation/sample_150.json",
        output_path="data/annotation/failure_analysis.txt",
    )

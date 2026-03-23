"""
Run LangExtract inference on all job postings to extract SKILL and TOOL entities.

Pipeline position: runs after 09b_extract_requirements_all.py (same input),
produces output consumed by app/dashboard_langextract.py.

For each job, calls LangExtract (gemini-2.5-flash-lite) with the same prompt
and few-shot examples used in the evaluation script. Uses requirements_section
when available, falls back to description_clean.

Saves per-job results and aggregated statistics in the same format as
10_run_inference.py so the LangExtract dashboard can reuse the same chart logic.

Usage:
    python scripts/pipeline/10b_run_langextract_inference.py               # full run
    python scripts/pipeline/10b_run_langextract_inference.py --retry-nulls # re-run empty results

Input:  data/processed/jobs_with_requirements.json
        .env  (LANGEXTRACT_API_KEY)
Output: data/processed/langextract_inference_results.json
        data/analysis/langextract_results.json
"""

import argparse
import contextlib
import io
import json
import os
import textwrap
import time
from collections import Counter
from itertools import combinations
from pathlib import Path

import langextract as lx
from dotenv import load_dotenv
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Paths and configuration
# ---------------------------------------------------------------------------

REPO_ROOT         = Path(__file__).resolve().parents[2]
JOBS_PATH         = REPO_ROOT / "data" / "processed" / "jobs_with_requirements.json"
INFERENCE_OUTPUT  = REPO_ROOT / "data" / "processed" / "langextract_inference_results.json"
ANALYZED_OUTPUT   = REPO_ROOT / "data" / "analysis" / "langextract_results.json"
CHECKPOINT_PATH   = REPO_ROOT / "data" / "processed" / "langextract_inference_checkpoint.json"

LANGEXTRACT_MODEL  = "gemini-2.5-flash-lite"
CHECKPOINT_INTERVAL = 50
SLEEP_BETWEEN_JOBS  = 2  # seconds

# ---------------------------------------------------------------------------
# Prompt and few-shot examples  (same as 02_langextract_eval.py)
# ---------------------------------------------------------------------------

PROMPT = textwrap.dedent("""
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

EXAMPLES = [
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

# ---------------------------------------------------------------------------
# Entity extraction
# ---------------------------------------------------------------------------

def extract_entities(text: str) -> tuple[list[str], list[str]]:
    """Run LangExtract on a single text and return (skills, tools).

    Retries up to 3 times on 503 errors with a 10-second delay.
    Returns ([], []) on unrecoverable failure.
    """
    for attempt in range(3):
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                result = lx.extract(
                    text_or_documents=text,
                    prompt_description=PROMPT,
                    examples=EXAMPLES,
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
            return skills, tools

        except Exception as exc:
            if "503" in str(exc) and attempt < 2:
                print(f"  503 error, retrying in 10s (attempt {attempt + 1}/3)...")
                time.sleep(10)
            else:
                print(f"  Extraction failed: {exc}")
                return [], []

    return [], []


# ---------------------------------------------------------------------------
# Aggregated statistics  (same format as 10_run_inference.py)
# ---------------------------------------------------------------------------

def compute_aggregated_stats(results: list[dict]) -> dict:
    """Compute aggregated statistics from per-job results."""
    skill_counter = Counter()
    tool_counter  = Counter()
    skills_by_level: dict[str, Counter] = {}
    tools_by_level:  dict[str, Counter] = {}
    skill_cooccurrence: Counter = Counter()

    for job in results:
        level       = job["experience_level"]
        skills_lower = [s.lower() for s in job["skills"]]
        tools_lower  = [t.lower() for t in job["tools"]]

        for s in skills_lower:
            skill_counter[s] += 1
        for t in tools_lower:
            tool_counter[t] += 1

        if level not in skills_by_level:
            skills_by_level[level] = Counter()
            tools_by_level[level]  = Counter()
        for s in skills_lower:
            skills_by_level[level][s] += 1
        for t in tools_lower:
            tools_by_level[level][t] += 1

        for a, b in combinations(sorted(set(skills_lower)), 2):
            skill_cooccurrence[(a, b)] += 1

    total_jobs   = len(results)
    total_skills = sum(len(j["skills"]) for j in results)
    total_tools  = sum(len(j["tools"])  for j in results)

    def counter_to_list(c: Counter) -> list[dict]:
        return [{"name": name, "count": count} for name, count in c.most_common()]

    return {
        "top_skills": counter_to_list(skill_counter),
        "top_tools":  counter_to_list(tool_counter),
        "skills_by_experience_level": {
            level: counter_to_list(c) for level, c in skills_by_level.items()
        },
        "tools_by_experience_level": {
            level: counter_to_list(c) for level, c in tools_by_level.items()
        },
        "skill_cooccurrence": [
            {"pair": list(pair), "count": count}
            for pair, count in skill_cooccurrence.most_common(50)
        ],
        "summary": {
            "total_jobs":          total_jobs,
            "total_unique_skills": len(skill_counter),
            "total_unique_tools":  len(tool_counter),
            "avg_skills_per_job":  round(total_skills / total_jobs, 2) if total_jobs else 0,
            "avg_tools_per_job":   round(total_tools  / total_jobs, 2) if total_jobs else 0,
        },
    }


# ---------------------------------------------------------------------------
# Checkpoint helpers
# ---------------------------------------------------------------------------

def load_checkpoint() -> dict:
    """Return {job_id: result_dict} from checkpoint file, or {}."""
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH, encoding="utf-8") as f:
            data = json.load(f)
        print(f"Loaded checkpoint: {len(data)} jobs already processed")
        return {r["id"]: r for r in data}
    return {}


def save_checkpoint(results_by_id: dict) -> None:
    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
        json.dump(list(results_by_id.values()), f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Main extraction run
# ---------------------------------------------------------------------------

def main() -> None:
    """Run LangExtract on all jobs in JOBS_PATH."""
    print("=" * 60)
    print("LangExtract Inference — All Jobs")
    print("=" * 60)

    with open(JOBS_PATH, encoding="utf-8") as f:
        jobs = json.load(f)
    print(f"\nLoaded {len(jobs)} jobs from {JOBS_PATH}")

    results_by_id = load_checkpoint()
    already_done  = len(results_by_id)

    req_available = sum(1 for j in jobs if j.get("requirements_section"))
    print(f"With requirements section: {req_available} / {len(jobs)}")

    start_time = time.time()
    succeeded  = 0
    failed     = 0

    for job in tqdm(jobs, desc="Extracting entities"):
        job_id = job["id"]
        if job_id in results_by_id:
            continue

        requirements = job.get("requirements_section")
        used_req     = bool(requirements)
        text         = requirements if used_req else job.get("description_clean", "")

        if text:
            skills, tools = extract_entities(text)
        else:
            skills, tools = [], []

        results_by_id[job_id] = {
            "id":               job_id,
            "experience_level": job.get("experienceLevel", ""),
            "skills":           skills,
            "tools":            tools,
            "used_requirements_section": used_req,
        }

        if skills or tools:
            succeeded += 1
        else:
            failed += 1

        if len(results_by_id) % CHECKPOINT_INTERVAL == 0:
            save_checkpoint(results_by_id)
            print(f"\n  Checkpoint saved at {len(results_by_id)} jobs")

        time.sleep(SLEEP_BETWEEN_JOBS)

    elapsed       = time.time() - start_time
    total_processed = len(results_by_id) - already_done

    print(f"\n{'=' * 60}")
    print("Summary")
    print(f"{'=' * 60}")
    print(f"  Jobs processed this run:  {total_processed}")
    print(f"  With entities:            {succeeded}")
    print(f"  Empty (no text / failed): {failed}")
    print(f"  Elapsed:                  {elapsed:.1f}s")
    if total_processed:
        print(f"  Avg time/job:             {elapsed / total_processed:.1f}s")

    # Preserve original job order
    id_order = [job["id"] for job in jobs]
    ordered  = [results_by_id[jid] for jid in id_order if jid in results_by_id]

    INFERENCE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(INFERENCE_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(ordered, f, ensure_ascii=False, indent=2)
    print(f"\nSaved per-job results to {INFERENCE_OUTPUT}")

    stats = compute_aggregated_stats(ordered)
    ANALYZED_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(ANALYZED_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"Saved aggregated stats to {ANALYZED_OUTPUT}")

    if CHECKPOINT_PATH.exists():
        CHECKPOINT_PATH.unlink()
        print("Checkpoint file removed.")

    print(f"\n{'=' * 60}")
    s = stats["summary"]
    print(f"  Total unique skills: {s['total_unique_skills']}")
    print(f"  Total unique tools:  {s['total_unique_tools']}")
    print(f"  Avg skills/job:      {s['avg_skills_per_job']}")
    print(f"  Avg tools/job:       {s['avg_tools_per_job']}")
    print(f"\nTop 10 Skills:")
    for item in stats["top_skills"][:10]:
        print(f"  {item['count']:4d}  {item['name']}")
    print(f"\nTop 10 Tools:")
    for item in stats["top_tools"][:10]:
        print(f"  {item['count']:4d}  {item['name']}")
    print(f"{'=' * 60}")
    print("Done!")
    print(f"{'=' * 60}")


# ---------------------------------------------------------------------------
# Retry nulls
# ---------------------------------------------------------------------------

def retry_nulls() -> None:
    """Re-run extraction for jobs where both skills and tools are empty."""
    print("=" * 60)
    print("Retrying empty results")
    print("=" * 60)

    if not INFERENCE_OUTPUT.exists():
        print(f"ERROR: {INFERENCE_OUTPUT} not found. Run main extraction first.")
        return

    with open(INFERENCE_OUTPUT, encoding="utf-8") as f:
        results = json.load(f)

    empties = [r for r in results if not r["skills"] and not r["tools"]]
    print(f"\nFound {len(empties)} empty entries out of {len(results)} jobs")

    if not empties:
        print("Nothing to retry.")
        return

    # Build id → full job text lookup
    with open(JOBS_PATH, encoding="utf-8") as f:
        jobs = json.load(f)
    jobs_by_id = {j["id"]: j for j in jobs}

    recovered  = 0
    still_empty = 0
    start_time  = time.time()

    for r in tqdm(empties, desc="Retrying empties"):
        job = jobs_by_id.get(r["id"])
        if not job:
            still_empty += 1
            continue

        requirements = job.get("requirements_section")
        used_req     = bool(requirements)
        text         = requirements if used_req else job.get("description_clean", "")

        if text:
            skills, tools = extract_entities(text)
            r["skills"] = skills
            r["tools"]  = tools
            r["used_requirements_section"] = used_req
            if skills or tools:
                recovered += 1
            else:
                still_empty += 1
        else:
            still_empty += 1

        time.sleep(SLEEP_BETWEEN_JOBS)

    with open(INFERENCE_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    stats = compute_aggregated_stats(results)
    with open(ANALYZED_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - start_time
    print(f"\n{'=' * 60}")
    print("Retry Summary")
    print(f"{'=' * 60}")
    print(f"  Retried:     {len(empties)}")
    print(f"  Recovered:   {recovered}")
    print(f"  Still empty: {still_empty}")
    print(f"  Elapsed:     {elapsed:.1f}s")
    print(f"\nUpdated {INFERENCE_OUTPUT}")
    print(f"Updated {ANALYZED_OUTPUT}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    load_dotenv(REPO_ROOT / ".env")
    api_key = os.getenv("LANGEXTRACT_API_KEY")
    if not api_key:
        raise EnvironmentError("LANGEXTRACT_API_KEY not set in .env")
    os.environ["GOOGLE_API_KEY"] = api_key

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--retry-nulls",
        action="store_true",
        help="Re-run extraction for jobs that returned no entities",
    )
    args = parser.parse_args()

    if args.retry_nulls:
        retry_nulls()
    else:
        main()

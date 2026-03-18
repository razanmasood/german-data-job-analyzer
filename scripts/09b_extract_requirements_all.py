"""
Extract requirements sections from all 1,240 job postings using the Gemini API.

Pipeline position: runs after 09_prepare_ner_dataset.py, before 10_run_inference.py.

For each job in jobs_combined_clean.json, this script calls Gemini to extract
only the requirements/qualifications section from the full job description.
The extracted section is stored in a new requirements_section field. Jobs where
extraction fails or no requirements section is found receive requirements_section=None.

The output file jobs_with_requirements.json is a copy of the source data enriched
with this field — the source file is never modified.

Usage:
    python 09b_extract_requirements_all.py               # full extraction run
    python 09b_extract_requirements_all.py --retry-nulls # re-run only on None entries

Input:  data/processed/jobs_combined_clean.json
        prompts/section_extraction.txt
Output: data/processed/jobs_with_requirements.json
"""

import argparse
import json
import os
import time
from pathlib import Path

from google import genai
from tqdm import tqdm

# --- Constants / configuration ---

JOBS_PATH = Path("data/processed/jobs_combined_clean.json")
SECTION_PROMPT_PATH = Path("prompts/section_extraction.txt")
OUTPUT_PATH = Path("data/processed/jobs_with_requirements.json")
CHECKPOINT_PATH = Path("data/processed/jobs_with_requirements_checkpoint.json")

GEMINI_MODEL = "models/gemini-2.5-flash-lite"
CHECKPOINT_INTERVAL = 100  # save progress every N jobs

# --- Gemini extraction ---

def extract_requirements_section(description, prompt_template, client):
    """Extract the requirements/qualifications section from a job description.

    Fills the prompt template with the description, calls Gemini, and returns
    the extracted section as a string. Returns None if the model signals that
    no requirements section exists (NO_REQUIREMENTS_SECTION_FOUND) or if all
    retry attempts fail.

    Retries up to 3 times on 503 errors (service overload) with a 10-second
    delay between attempts. Any other exception fails immediately.

    Args:
        description: Full job description text (description_clean field).
        prompt_template: Contents of section_extraction.txt with {description} placeholder.
        client: Authenticated google.genai.Client instance.

    Returns:
        Extracted requirements section as a string, or None.
    """
    filled_prompt = prompt_template.replace("{description}", description)

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=filled_prompt,
            )
            extracted = response.text.strip()

            if "NO_REQUIREMENTS_SECTION_FOUND" in extracted:
                return None

            return extracted

        except Exception as e:
            if "503" in str(e) and attempt < 2:
                print(f"  503 error, retrying in 10s (attempt {attempt + 1}/3)...")
                time.sleep(10)
            else:
                print(f"  Extraction failed: {e}")
                return None

# --- Checkpoint and I/O helpers ---

def load_checkpoint():
    """Load a previously saved checkpoint if one exists.

    Returns:
        Dict mapping job id → enriched job dict for all already-processed jobs,
        or an empty dict if no checkpoint file is found.
    """
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Loaded checkpoint: {len(data)} jobs already processed")
        return {job["id"]: job for job in data}
    return {}


def save_checkpoint(results_by_id):
    """Write current results to the checkpoint file.

    Args:
        results_by_id: Dict mapping job id → enriched job dict.
    """
    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
        json.dump(list(results_by_id.values()), f, ensure_ascii=False, indent=2)

# --- Core extraction logic ---

def main(client, prompt_template):
    """Run requirements extraction on all jobs in JOBS_PATH.

    Skips jobs already present in the checkpoint. Saves a checkpoint every
    CHECKPOINT_INTERVAL jobs. On completion, writes the full enriched dataset
    to OUTPUT_PATH in the original job order and removes the checkpoint file.

    In test mode (test_mode=True), processes only the first test_limit jobs,
    prints a preview of extracted sections, and exits without saving output.

    Args:
        client: Authenticated google.genai.Client instance.
        prompt_template: Contents of section_extraction.txt.
    """
    print("=" * 60)
    print("Requirements Section Extraction — All Jobs")
    print("=" * 60)

    test_mode = True
    test_limit = 3

    with open(JOBS_PATH, "r", encoding="utf-8") as f:
        jobs = json.load(f)
    print(f"\nLoaded {len(jobs)} jobs from {JOBS_PATH}")

    results_by_id = load_checkpoint()
    already_done = len(results_by_id)

    jobs_to_process = jobs[:test_limit] if test_mode else jobs
    if test_mode:
        print(f"\n[TEST MODE] Processing first {test_limit} jobs only.")
        print("Set test_mode = False to run on all jobs.\n")

    start_time = time.time()
    succeeded = 0
    failed = 0

    for job in tqdm(jobs_to_process, desc="Extracting requirements"):
        job_id = job["id"]

        if job_id in results_by_id:
            continue

        desc = job.get("description_clean", "")
        requirements = extract_requirements_section(desc, prompt_template, client) if desc else None

        enriched = dict(job)
        enriched["requirements_section"] = requirements
        results_by_id[job_id] = enriched

        if requirements is not None:
            succeeded += 1
        else:
            failed += 1

        if not test_mode and len(results_by_id) % CHECKPOINT_INTERVAL == 0:
            save_checkpoint(results_by_id)
            print(f"\n  Checkpoint saved at {len(results_by_id)} jobs")

    elapsed = time.time() - start_time
    total_processed = len(results_by_id) - already_done

    print(f"\n{'=' * 60}")
    print("Summary")
    print(f"{'=' * 60}")
    print(f"  Jobs processed this run: {total_processed}")
    print(f"  Requirements found:      {succeeded}")
    print(f"  Fell back to None:       {failed}")
    print(f"  Elapsed:                 {elapsed:.1f}s")
    if total_processed:
        print(f"  Avg time/job:            {elapsed / total_processed:.1f}s")

    if test_mode:
        print("\n[TEST MODE] Sample results:")
        for job in list(results_by_id.values())[:test_limit]:
            section = job.get("requirements_section")
            preview = section[:120].replace("\n", " ") if section else "None"
            print(f"  id={job['id']}  extracted={'yes' if section else 'NO'}")
            print(f"    {preview}")
        print("\nInspect above. Set test_mode = False to run on all 1,240 jobs.")
        return

    # Preserve original job order when writing output
    id_order = [job["id"] for job in jobs]
    ordered_results = [results_by_id[jid] for jid in id_order if jid in results_by_id]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(ordered_results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(ordered_results)} enriched jobs to {OUTPUT_PATH}")

    if CHECKPOINT_PATH.exists():
        CHECKPOINT_PATH.unlink()
        print("Checkpoint file removed.")

    print(f"{'=' * 60}")
    print("Done!")
    print(f"{'=' * 60}")


def retry_nulls(client, prompt_template):
    """Re-run extraction for jobs where requirements_section is None.

    Reads OUTPUT_PATH, identifies jobs with a null requirements_section,
    and attempts extraction again. Updates the jobs in place and saves
    the file back to OUTPUT_PATH.

    Useful after a run with transient API errors produced more nulls than expected.
    Does not use checkpointing — intended for small retry batches.

    Args:
        client: Authenticated google.genai.Client instance.
        prompt_template: Contents of section_extraction.txt.
    """
    print("=" * 60)
    print("Retrying null requirements sections")
    print("=" * 60)

    if not OUTPUT_PATH.exists():
        print(f"ERROR: {OUTPUT_PATH} not found. Run main extraction first.")
        return

    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    nulls = [j for j in jobs if j.get("requirements_section") is None]
    print(f"\nFound {len(nulls)} null entries out of {len(jobs)} jobs")

    if not nulls:
        print("Nothing to retry.")
        return

    recovered = 0
    still_none = 0
    start_time = time.time()

    for job in tqdm(nulls, desc="Retrying nulls"):
        desc = job.get("description_clean", "")
        requirements = extract_requirements_section(desc, prompt_template, client) if desc else None
        job["requirements_section"] = requirements
        if requirements is not None:
            recovered += 1
        else:
            still_none += 1

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - start_time
    print(f"\n{'=' * 60}")
    print("Retry Summary")
    print(f"{'=' * 60}")
    print(f"  Retried:    {len(nulls)}")
    print(f"  Recovered:  {recovered}")
    print(f"  Still None: {still_none}")
    print(f"  Elapsed:    {elapsed:.1f}s")
    print(f"\nUpdated {OUTPUT_PATH}")

# --- Main pipeline ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--retry-nulls", action="store_true",
                        help="Re-run extraction only for jobs where requirements_section is None")
    args = parser.parse_args()

    api_key = os.getenv("LANGEXTRACT_API_KEY")
    if not api_key:
        raise EnvironmentError("LANGEXTRACT_API_KEY environment variable not set.")
    client = genai.Client(api_key=api_key)

    with open(SECTION_PROMPT_PATH, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    if args.retry_nulls:
        retry_nulls(client, prompt_template)
    else:
        main(client, prompt_template)

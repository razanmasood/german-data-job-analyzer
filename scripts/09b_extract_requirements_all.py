"""
Extract requirements sections from all job postings using Ollama.

TWO-STEP PREPROCESSING:
1. Load all 1,240 jobs from jobs_combined_clean.json
2. For each job, call Ollama to extract the requirements/qualifications section

Adds a requirements_section field to each job (None if extraction failed).
Saves output to jobs_with_requirements.json — does NOT overwrite the source file.
Includes checkpointing every 100 jobs for safe resumption.

Input:  data/processed/jobs_combined_clean.json
        prompts/section_extraction.txt
Output: data/processed/jobs_with_requirements.json
"""

import json
import os
import time
from pathlib import Path

import requests
from tqdm import tqdm

JOBS_PATH = Path("data/processed/jobs_combined_clean.json")
SECTION_PROMPT_PATH = Path("prompts/section_extraction.txt")
OUTPUT_PATH = Path("data/processed/jobs_with_requirements.json")
CHECKPOINT_PATH = Path("data/processed/jobs_with_requirements_checkpoint.json")


def call_ollama(prompt_text, model="llama3.1:8b", retries=1, expect_json=True):
    """Send prompt to Ollama and return parsed result. Retries once on failure."""
    ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    url = f"{ollama_host}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt_text,
        "stream": False,
        "temperature": 0.0,
        "num_predict": 2048,
        "num_ctx": 8192,
        "top_p": 0.9,
    }

    if expect_json:
        payload["format"] = "json"

    for attempt in range(1 + retries):
        try:
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.HTTPError) as e:
            if attempt < retries:
                print(f"  Attempt {attempt + 1} failed: {e}. Retrying in 5s...")
                time.sleep(5)
            else:
                raise


def extract_requirements_section(description, section_prompt_template):
    """Extract only the requirements/qualifications section from full job posting.

    Returns extracted requirements section text, or None if not found.
    """
    filled_prompt = section_prompt_template.replace('{description}', description)

    try:
        ollama_result = call_ollama(filled_prompt, expect_json=False)
        extracted_section = ollama_result.get('response', '').strip()

        if "NO_REQUIREMENTS_SECTION_FOUND" in extracted_section:
            return None

        return extracted_section

    except Exception as e:
        print(f"  Section extraction failed: {e}")
        return None


def load_checkpoint():
    """Load existing checkpoint if available. Returns dict keyed by job id."""
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Loaded checkpoint: {len(data)} jobs already processed")
        return {job["id"]: job for job in data}
    return {}


def save_checkpoint(results_by_id):
    """Save current results as a checkpoint."""
    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
        json.dump(list(results_by_id.values()), f, ensure_ascii=False, indent=2)


def main():
    """Extract requirements sections for all jobs and save enriched dataset."""
    print("=" * 60)
    print("Requirements Section Extraction — All Jobs")
    print("=" * 60)

    # Test mode: process only N jobs first
    test_mode = False
    test_limit = 5

    with open(JOBS_PATH, "r", encoding="utf-8") as f:
        jobs = json.load(f)
    print(f"\nLoaded {len(jobs)} jobs from {JOBS_PATH}")

    with open(SECTION_PROMPT_PATH, "r", encoding="utf-8") as f:
        section_prompt_template = f.read()
    print(f"Loaded section extraction prompt from {SECTION_PROMPT_PATH}")

    # Load checkpoint
    results_by_id = load_checkpoint()
    already_done = len(results_by_id)

    jobs_to_process = jobs[:test_limit] if test_mode else jobs
    if test_mode:
        print(f"\n[TEST MODE] Processing first {test_limit} jobs only.")
        print("Set test_mode = False in main() to run on all jobs.\n")

    start_time = time.time()
    succeeded = 0
    failed = 0

    for job in tqdm(jobs_to_process, desc="Extracting requirements"):
        job_id = job["id"]

        if job_id in results_by_id:
            continue

        desc = job.get("description_clean", "")
        requirements = extract_requirements_section(desc, section_prompt_template) if desc else None

        enriched = dict(job)
        enriched["requirements_section"] = requirements

        results_by_id[job_id] = enriched

        if requirements is not None:
            succeeded += 1
        else:
            failed += 1

        # Checkpoint every 100 jobs (only in full mode)
        if not test_mode and len(results_by_id) % 100 == 0:
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

    # Save final output (preserve original job order)
    id_order = [job["id"] for job in jobs]
    ordered_results = [results_by_id[jid] for jid in id_order if jid in results_by_id]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(ordered_results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(ordered_results)} enriched jobs to {OUTPUT_PATH}")

    # Clean up checkpoint after successful full run
    if CHECKPOINT_PATH.exists():
        CHECKPOINT_PATH.unlink()
        print("Checkpoint file removed.")

    print(f"{'=' * 60}")
    print("Done!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

"""
Pre-annotate 150 sampled job postings using Ollama (llama3.1:8b).

For each job, sends the description to the LLM with the annotation prompt,
extracts SKILL and TOOL entities, and saves structured results.
Includes checkpointing every 50 jobs and retry logic for failed requests.

Input:  data/annotation/sample_150.json
        prompts/annotation.txt
Output: data/annotation/annotations_llm_150.json
"""

import json
import os
import re
import time

import requests
from tqdm import tqdm


def classify_language(text):
    """Classify text as German, English, or Mixed using word heuristics."""
    if not text or not isinstance(text, str):
        return "unknown"

    text_lower = text.lower()

    german_words = ['der', 'die', 'das', 'und', 'mit', 'für', 'wir', 'haben', 'sind', 'eine']
    english_words = ['the', 'and', 'with', 'you', 'we', 'are', 'have', 'will', 'our', 'your']

    german_count = sum(len(re.findall(r'\b' + w + r'\b', text_lower)) for w in german_words)
    english_count = sum(len(re.findall(r'\b' + w + r'\b', text_lower)) for w in english_words)

    total = german_count + english_count
    if total == 0:
        return "unknown"

    german_ratio = german_count / total
    if german_ratio > 0.6:
        return "de"
    elif german_ratio < 0.4:
        return "en"
    else:
        return "mixed"


def call_ollama(prompt_text, model="llama3.1:8b", retries=1):
    """Send prompt to Ollama and return parsed result. Retries once on failure."""
    ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    url = f"{ollama_host}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt_text,
        "stream": False,
        "format": "json",
        "temperature": 0.0,
        "num_predict": 512,
    }

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


def load_checkpoint(checkpoint_path):
    """Load existing checkpoint results if available."""
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
        print(f"Loaded checkpoint with {len(results)} completed jobs")
        return results
    return []


def save_checkpoint(results, checkpoint_path):
    """Save current results as a checkpoint."""
    with open(checkpoint_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def main():
    sample_path = "data/annotation/sample_150.json"
    prompt_path = "prompts/annotation.txt"
    output_path = "data/annotation/annotations_llm_150.json"
    checkpoint_path = "data/annotation/annotations_llm_checkpoint.json"

    print("=" * 80)
    print("LLM Pre-Annotation: 150 Job Postings")
    print("=" * 80)

    # Load prompt template
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    print(f"\nLoaded prompt template from: {prompt_path}")

    # Load sample data
    with open(sample_path, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    print(f"Loaded {len(jobs)} jobs from: {sample_path}")

    # Load checkpoint if exists
    results = load_checkpoint(checkpoint_path)
    completed_ids = {r['id'] for r in results}

    failed = []
    start_time = time.time()

    print(f"\nProcessing {len(jobs)} jobs ({len(completed_ids)} already completed)...\n")

    for i, job in enumerate(tqdm(jobs, desc="Annotating")):
        job_id = job.get('id')  # Use original LinkedIn job ID

        # Skip already processed jobs
        if job_id in completed_ids:
            continue

        title = job.get('title', 'N/A')
        desc = job.get('description', '')
        language = classify_language(desc)

        # Fill prompt template
        filled_prompt = prompt_template.replace('{description}', desc)

        # Call Ollama
        try:
            ollama_result = call_ollama(filled_prompt)
            response_text = ollama_result.get('response', '{}')
        except Exception as e:
            print(f"\n  FAILED job {job_id} ({title}): {e}")
            failed.append({"id": job_id, "title": title, "error": str(e)})
            continue

        # Parse JSON response
        try:
            extracted = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"\n  JSON parse error for {job_id}: {e}")
            print(f"  Raw response: {response_text[:200]}")
            extracted = {"skills": [], "tools": []}

        skills = extracted.get('skills', [])
        tools = extracted.get('tools', [])

        results.append({
            "id": job_id,
            "jobTitle": title,
            "description": desc,
            "language": language,
            "entities": {
                "skills": skills,
                "tools": tools,
            }
        })

        # Checkpoint every 50 jobs
        if len(results) % 50 == 0:
            save_checkpoint(results, checkpoint_path)
            print(f"\n  Checkpoint saved at {len(results)} jobs")

    # Save final output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Clean up checkpoint after successful completion
    if os.path.exists(checkpoint_path) and not failed:
        os.remove(checkpoint_path)

    elapsed = time.time() - start_time

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total_skills = sum(len(r['entities']['skills']) for r in results)
    total_tools = sum(len(r['entities']['tools']) for r in results)
    print(f"  Total processed: {len(results)}")
    print(f"  Failed:          {len(failed)}")
    if results:
        print(f"  Avg skills/job:  {total_skills / len(results):.1f}")
        print(f"  Avg tools/job:   {total_tools / len(results):.1f}")
    print(f"  Total time:      {elapsed:.1f}s")
    if results:
        print(f"  Avg time/job:    {elapsed / len(results):.1f}s")
    print(f"\nResults saved to: {output_path}")

    if failed:
        print(f"\nFailed jobs ({len(failed)}):")
        for f_job in failed:
            print(f"  - {f_job['id']}: {f_job['title']} ({f_job['error'][:80]})")

    print("=" * 80)


if __name__ == "__main__":
    main()

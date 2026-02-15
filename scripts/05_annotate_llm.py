"""
Pre-annotate 150 sampled job postings using Ollama (llama3.1:8b).

TWO-STEP PROCESS:
1. Extract requirements section from full job posting
2. Extract SKILL and TOOL entities from requirements section only

For each job, sends the description to the LLM with the section extraction prompt,
then sends the extracted requirements to the entity extraction prompt.
Includes checkpointing every 50 jobs and retry logic for failed requests.

Input:  data/annotation/sample_150.json
        prompts/section_extraction.txt (NEW)
        prompts/annotation.txt
Output: data/annotation/annotations_llm_150.json
"""

import json
import os
import re
import time

import requests
from tqdm import tqdm


def preprocess_description(text):
    """
    Remove parentheses and brackets but keep their content.
    Helps LLM extract terms often hidden in parenthetical examples.

    Examples:
    - "languages (e.g. Python, Java)" -> "languages , e.g. Python, Java"
    - "platforms (AWS, Azure)" -> "platforms , AWS, Azure"
    """
    # Replace (content) with , content
    text = re.sub(r'\(([^)]+)\)', r', \1', text)
    text = re.sub(r'\[([^\]]+)\]', r', \1', text)

    # Clean up multiple commas/spaces
    text = re.sub(r',\s*,', ',', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


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


def call_ollama(prompt_text, model="llama3.1:8b", retries=1, expect_json=True):
    """Send prompt to Ollama and return parsed result. Retries once on failure."""
    ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    url = f"{ollama_host}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt_text,
        "stream": False,
        "temperature": 0.0,      # Deterministic for consistent extraction
        "num_predict": 2048,     # Allow up to 2048 tokens for output
        "num_ctx": 8192,         # Context window - handle long job descriptions
        "top_p": 0.9,            # Slight randomness for better extraction
    }
    
    # Only add format constraint for entity extraction, not section extraction
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


# NEW FUNCTION
def extract_requirements_section(description, section_prompt_template):
    """
    Extract only the requirements/qualifications section from full job posting.
    
    Args:
        description: Full job posting text
        section_prompt_template: Prompt template for section extraction
        
    Returns:
        Extracted requirements section text, or None if not found
    """
    filled_prompt = section_prompt_template.replace('{description}', description)
    
    try:
        ollama_result = call_ollama(filled_prompt, expect_json=False)
        extracted_section = ollama_result.get('response', '').strip()
        
        # Check if section was found
        if "NO_REQUIREMENTS_SECTION_FOUND" in extracted_section:
            return None
            
        return extracted_section
        
    except Exception as e:
        print(f"  Section extraction failed: {e}")
        return None


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
    section_prompt_path = "prompts/section_extraction.txt"  # NEW
    entity_prompt_path = "prompts/annotation.txt"
    output_path = "data/annotation/annotations_llm_150.json"
    checkpoint_path = "data/annotation/annotations_llm_checkpoint.json"

    print("=" * 80)
    print("LLM Pre-Annotation: 150 Job Postings (2-Step Process)")
    print("=" * 80)

    # Load prompts
    with open(section_prompt_path, 'r', encoding='utf-8') as f:
        section_prompt_template = f.read()
    print(f"\nLoaded section extraction prompt from: {section_prompt_path}")
    
    with open(entity_prompt_path, 'r', encoding='utf-8') as f:
        entity_prompt_template = f.read()
    print(f"Loaded entity extraction prompt from: {entity_prompt_path}")

    # Load sample data
    with open(sample_path, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    print(f"Loaded {len(jobs)} jobs from: {sample_path}")

    # Load checkpoint if exists
    results = load_checkpoint(checkpoint_path)
    completed_ids = {r['id'] for r in results}

    failed = []
    no_requirements_section = []  # Track jobs with no detectable requirements
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

        # STEP 1: Extract requirements section
        requirements_section = extract_requirements_section(desc, section_prompt_template)
        
        if not requirements_section:
            print(f"\n  WARNING: No requirements section found for job {job_id} ({title})")
            no_requirements_section.append({"id": job_id, "title": title})
            # Store with empty entities but keep full description
            results.append({
                "id": job_id,
                "jobTitle": title,
                "description": desc,  # Keep full description
                "requirements_section": None,
                "language": language,
                "entities": {
                    "skills": [],
                    "tools": [],
                },
                "warning": "NO_REQUIREMENTS_SECTION_FOUND"
            })
            continue

        # STEP 2: Preprocess requirements section and extract entities
        processed_requirements = preprocess_description(requirements_section)
        filled_prompt = entity_prompt_template.replace('{description}', processed_requirements)

        # Call Ollama for entity extraction
        try:
            ollama_result = call_ollama(filled_prompt, expect_json=True)
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
            "description": desc,  # Keep full original description
            "requirements_section": requirements_section,  # Store extracted section
            "processed_requirements": processed_requirements,  # Store preprocessed version
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
    print(f"  Total processed:      {len(results)}")
    print(f"  Failed:               {len(failed)}")
    print(f"  No requirements sect: {len(no_requirements_section)}")
    if results:
        print(f"  Avg skills/job:       {total_skills / len(results):.1f}")
        print(f"  Avg tools/job:        {total_tools / len(results):.1f}")
    print(f"  Total time:           {elapsed:.1f}s")
    if results:
        print(f"  Avg time/job:         {elapsed / len(results):.1f}s")
    print(f"\nResults saved to: {output_path}")

    if no_requirements_section:
        print(f"\nJobs with no requirements section ({len(no_requirements_section)}):")
        for job in no_requirements_section[:5]:  # Show first 5
            print(f"  - {job['id']}: {job['title']}")
        if len(no_requirements_section) > 5:
            print(f"  ... and {len(no_requirements_section) - 5} more")

    if failed:
        print(f"\nFailed jobs ({len(failed)}):")
        for f_job in failed:
            print(f"  - {f_job['id']}: {f_job['title']} ({f_job['error'][:80]})")

    print("=" * 80)


if __name__ == "__main__":
    main()
"""
Test the annotation prompt on 5 diverse job postings using Ollama (llama3.1:8b).

Picks 2 German, 2 English, and 1 mixed-language description across
different experience levels. Sends each to Ollama, parses results,
and saves output for review.

Input:  data/annotation/sample_150.json
        prompts/annotation.txt
Output: data/annotation/test_prompt_results.json
"""

import json
import os
import re
import requests


def classify_language(text):
    """Classify text as German, English, or Mixed using word heuristics."""
    if not text or not isinstance(text, str):
        return 'Unknown'

    text_lower = text.lower()

    german_words = ['der', 'die', 'das', 'und', 'mit', 'für', 'wir', 'haben', 'sind', 'eine']
    english_words = ['the', 'and', 'with', 'you', 'we', 'are', 'have', 'will', 'our', 'your']

    german_count = sum(len(re.findall(r'\b' + w + r'\b', text_lower)) for w in german_words)
    english_count = sum(len(re.findall(r'\b' + w + r'\b', text_lower)) for w in english_words)

    total = german_count + english_count
    if total == 0:
        return 'Unknown'

    german_ratio = german_count / total
    if german_ratio > 0.6:
        return 'German'
    elif german_ratio < 0.4:
        return 'English'
    else:
        return 'Mixed'


def select_diverse_jobs(jobs):
    """Select 5 diverse jobs: 2 German, 2 English, 1 Mixed."""
    for job in jobs:
        job['_language'] = classify_language(job.get('description', ''))

    german = [j for j in jobs if j['_language'] == 'German']
    english = [j for j in jobs if j['_language'] == 'English']
    mixed = [j for j in jobs if j['_language'] == 'Mixed']

    print(f"Language breakdown in sample: German={len(german)}, English={len(english)}, Mixed={len(mixed)}")

    selected = []

    # Pick 2 German with different experience levels
    exp_seen = set()
    for job in german:
        exp = job.get('experienceLevel', 'Unknown')
        if exp not in exp_seen:
            selected.append(job)
            exp_seen.add(exp)
            if len(selected) == 2:
                break
    if len(selected) < 2 and len(german) >= 2:
        selected = german[:2]

    # Pick 2 English with different experience levels
    exp_seen_en = set()
    for job in english:
        exp = job.get('experienceLevel', 'Unknown')
        if exp not in exp_seen_en and exp not in exp_seen:
            selected.append(job)
            exp_seen_en.add(exp)
            if len(selected) == 4:
                break
    # Fill remaining English slots if needed
    while len(selected) < 4 and english:
        for job in english:
            if job not in selected:
                selected.append(job)
                break
        else:
            break

    # Pick 1 Mixed
    if mixed:
        selected.append(mixed[0])
    elif english:
        # Fallback: pick another English job and label it
        for job in english:
            if job not in selected:
                selected.append(job)
                break

    return selected


def call_ollama(prompt_text, model="llama3.1:8b"):
    """Send prompt to Ollama and return parsed result."""
    ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    url = f"{ollama_host}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt_text,
        "stream": False,
        "format": "json",
        "temperature": 0.0,      # Deterministic for consistent extraction
        "num_predict": 2048,     # INCREASED: Allow up to 2048 tokens for output
        "num_ctx": 8192,         # ADDED: Context window - handle long job descriptions
        "top_p": 0.9,            # ADDED: Slight randomness for better extraction
    }
    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        result = response.json()
        return result
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to Ollama")
        print(f"Tried: {url}")
        print("Make sure Ollama is running and accessible.")
        print("Try: OLLAMA_HOST=http://host.docker.internal:11434 python scripts/04_test_prompt.py")
        raise


def main():
    sample_path = "data/annotation/sample_150.json"
    prompt_path = "prompts/annotation.txt"
    output_path = "data/annotation/test_prompt_results.json"

    print("=" * 80)
    print("Testing Annotation Prompt on 5 Diverse Jobs")
    print("=" * 80)

    # Load prompt template
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    print(f"\nLoaded prompt template from: {prompt_path}")

    # Load sample data
    with open(sample_path, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    print(f"Loaded {len(jobs)} jobs from: {sample_path}")

    # Select diverse jobs
    print("\nSelecting 5 diverse jobs...")
    selected = select_diverse_jobs(jobs)
    print(f"Selected {len(selected)} jobs\n")

    results = []

    for i, job in enumerate(selected, 1):
        lang = job.get('_language', 'Unknown')
        exp = job.get('experienceLevel', 'N/A')
        title = job.get('title', 'N/A')
        company = job.get('companyName', 'N/A')
        desc = job.get('description', '')

        print("=" * 80)
        print(f"JOB {i}/{len(selected)}")
        print(f"  Title:      {title}")
        print(f"  Company:    {company}")
        print(f"  Language:   {lang}")
        print(f"  Experience: {exp}")
        print(f"  Desc length: {len(desc)} chars")
        print("-" * 80)

        # Fill prompt template
        filled_prompt = prompt_template.replace('{description}', desc)

        # Call Ollama
        print("  Sending to Ollama...")
        ollama_result = call_ollama(filled_prompt)

        duration = ollama_result.get('total_duration', 0) / 1e9
        response_text = ollama_result.get('response', '{}')

        # Parse JSON response
        try:
            extracted = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"  ERROR parsing response: {e}")
            print(f"  Raw response: {response_text[:500]}")
            extracted = {"skills": [], "tools": [], "_parse_error": str(e)}

        skills = extracted.get('skills', [])
        tools = extracted.get('tools', [])

        print(f"  Time: {duration:.1f}s")
        print(f"\n  SKILLS ({len(skills)}):")
        for s in skills:
            print(f"    - {s}")
        print(f"\n  TOOLS ({len(tools)}):")
        for t in tools:
            print(f"    - {t}")
        print()

        # Store result
        results.append({
            "id": job.get('id'),
            "job_title": title,
            "company": company,
            "language": lang,
            "experienceLevel": exp,
            "description_length": len(desc),
            "description": desc,
            "extracted_skills": skills,
            "extracted_tools": tools,
            "generation_time_seconds": round(duration, 2)
        })

    # Save results
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total_skills = sum(len(r['extracted_skills']) for r in results)
    total_tools = sum(len(r['extracted_tools']) for r in results)
    total_time = sum(r['generation_time_seconds'] for r in results)
    print(f"  Jobs processed:  {len(results)}")
    print(f"  Total skills:    {total_skills}")
    print(f"  Total tools:     {total_tools}")
    print(f"  Avg skills/job:  {total_skills / len(results):.1f}")
    print(f"  Avg tools/job:   {total_tools / len(results):.1f}")
    print(f"  Total time:      {total_time:.1f}s")
    print(f"  Avg time/job:    {total_time / len(results):.1f}s")
    print(f"\nResults saved to: {output_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()

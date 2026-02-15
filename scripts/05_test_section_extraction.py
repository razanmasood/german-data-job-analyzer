"""
Test the 2-step annotation process on 5 diverse job postings using Ollama (llama3.1:8b).

STEP 1: Extract requirements section from full job posting
STEP 2: Extract SKILL and TOOL entities from requirements section only

Picks 2 German, 2 English, and 1 mixed-language description across
different experience levels. Shows both the extracted section and final entities.

Input:  data/annotation/sample_150.json
        prompts/section_extraction.txt
        prompts/annotation.txt
Output: data/annotation/test_section_extraction_results.json
"""

import json
import os
import re
import requests


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


def call_ollama(prompt_text, model="llama3.1:8b", expect_json=True):
    """Send prompt to Ollama and return parsed result."""
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

    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        result = response.json()
        return result
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to Ollama")
        print(f"Tried: {url}")
        print("Make sure Ollama is running and accessible.")
        print("Try: OLLAMA_HOST=http://host.docker.internal:11434 python scripts/05_test_section_extraction.py")
        raise


def extract_requirements_section(description, section_prompt_template):
    """
    Extract only the requirements/qualifications section from full job posting.
    
    Args:
        description: Full job posting text
        section_prompt_template: Prompt template for section extraction
        
    Returns:
        Tuple of (extracted_section_text, generation_time_seconds)
        Returns (None, time) if section not found
    """
    filled_prompt = section_prompt_template.replace('{description}', description)
    
    ollama_result = call_ollama(filled_prompt, expect_json=False)
    duration = ollama_result.get('total_duration', 0) / 1e9
    extracted_section = ollama_result.get('response', '').strip()
    
    # Check if section was found
    if "NO_REQUIREMENTS_SECTION_FOUND" in extracted_section:
        return None, duration
        
    return extracted_section, duration


def main():
    sample_path = "data/annotation/sample_150.json"
    section_prompt_path = "prompts/section_extraction.txt"
    entity_prompt_path = "prompts/annotation.txt"
    output_path = "data/annotation/test_section_extraction_results.json"

    print("=" * 80)
    print("Testing 2-Step Annotation Process on 5 Diverse Jobs")
    print("Step 1: Extract requirements section")
    print("Step 2: Extract entities from requirements only")
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

    # Select diverse jobs
    print("\nSelecting 5 diverse jobs...")
    selected = select_diverse_jobs(jobs)
    print(f"Selected {len(selected)} jobs\n")

    results = []
    no_section_found = []

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

        # STEP 1: Extract requirements section
        print("  STEP 1: Extracting requirements section...")
        requirements_section, section_time = extract_requirements_section(desc, section_prompt_template)
        
        if not requirements_section:
            print(f"  ⚠️  WARNING: No requirements section found!")
            no_section_found.append(title)
            results.append({
                "id": job.get('id'),
                "job_title": title,
                "company": company,
                "language": lang,
                "experienceLevel": exp,
                "description_length": len(desc),
                "description": desc,
                "requirements_section": None,
                "section_extraction_time": round(section_time, 2),
                "extracted_skills": [],
                "extracted_tools": [],
                "entity_extraction_time": 0,
                "warning": "NO_REQUIREMENTS_SECTION_FOUND"
            })
            print()
            continue

        print(f"  ✓ Requirements section: {len(requirements_section)} chars")
        print(f"  ✓ Section extraction time: {section_time:.1f}s")
        
        # Show first 200 chars of extracted section
        print(f"\n  Extracted section preview:")
        print(f"  '{requirements_section[:200]}...'")

        # STEP 2: Extract entities from requirements section
        print(f"\n  STEP 2: Extracting entities from requirements...")
        processed_requirements = preprocess_description(requirements_section)
        filled_prompt = entity_prompt_template.replace('{description}', processed_requirements)

        ollama_result = call_ollama(filled_prompt, expect_json=True)
        entity_time = ollama_result.get('total_duration', 0) / 1e9
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

        print(f"  ✓ Entity extraction time: {entity_time:.1f}s")
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
            "requirements_section": requirements_section,
            "requirements_section_length": len(requirements_section),
            "section_extraction_time": round(section_time, 2),
            "extracted_skills": skills,
            "extracted_tools": tools,
            "entity_extraction_time": round(entity_time, 2)
        })

    # Save results
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total_skills = sum(len(r['extracted_skills']) for r in results)
    total_tools = sum(len(r['extracted_tools']) for r in results)
    section_time_total = sum(r['section_extraction_time'] for r in results)
    entity_time_total = sum(r['entity_extraction_time'] for r in results)
    total_time = section_time_total + entity_time_total
    
    print(f"  Jobs processed:        {len(results)}")
    print(f"  No section found:      {len(no_section_found)}")
    if no_section_found:
        print(f"    Jobs: {', '.join(no_section_found)}")
    print(f"  Total skills:          {total_skills}")
    print(f"  Total tools:           {total_tools}")
    print(f"  Avg skills/job:        {total_skills / len(results):.1f}")
    print(f"  Avg tools/job:         {total_tools / len(results):.1f}")
    print(f"  Section extract time:  {section_time_total:.1f}s")
    print(f"  Entity extract time:   {entity_time_total:.1f}s")
    print(f"  Total time:            {total_time:.1f}s")
    print(f"  Avg time/job:          {total_time / len(results):.1f}s")
    print(f"\nResults saved to: {output_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
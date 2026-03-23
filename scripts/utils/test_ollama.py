#!/usr/bin/env python3
"""
Test script for Ollama API integration.
Loads a job posting and extracts skills and tools using llama3.1:8b model.

Requirements:
- Ollama must be running and accessible
- In devcontainer: port 11434 must be forwarded in devcontainer.json
- Can override Ollama host with OLLAMA_HOST environment variable
  Example: OLLAMA_HOST=http://host.docker.internal:11434 python scripts/test_ollama.py
"""

import json
import os
import requests


def load_sample_job(json_file_path: str) -> dict:
    """Load one job posting from the JSON file."""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        jobs = json.load(f)

    # Return the first job posting
    if jobs and len(jobs) > 0:
        return jobs[0]
    else:
        raise ValueError("No jobs found in the JSON file")


def extract_skills_with_ollama(job_description: str) -> dict:
    """
    Send job description to Ollama and extract SKILLS and TOOLS.

    Args:
        job_description: The job description text

    Returns:
        Dict containing the extracted skills and tools
    """
    # Get Ollama host from environment variable or use default
    ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    url = f"{ollama_host}/api/generate"

    prompt = f"""Analyze the following job description and extract all SKILLS and TOOLS mentioned.
Return the result as a JSON object with two arrays: "skills" and "tools".
Skills are general competencies (e.g., "machine learning", "data analysis", "communication").
Tools are specific technologies, frameworks, or software (e.g., "Python", "PyTorch", "Docker").

Job Description:
{job_description}

Return ONLY valid JSON in this format:
{{
  "skills": ["skill1", "skill2", ...],
  "tools": ["tool1", "tool2", ...]
}}
"""

    payload = {
        "model": "llama3.1:8b",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    print(f"Sending request to Ollama at {ollama_host}...")

    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        result = response.json()
        return result
    except requests.exceptions.ConnectionError as e:
        print("\n" + "=" * 80)
        print("ERROR: Cannot connect to Ollama")
        print("=" * 80)
        print(f"\nFailed to connect to: {url}")
        print("\nTroubleshooting steps:")
        print("1. Verify Ollama is running on your host machine:")
        print("   - Run: ollama list")
        print("   - Or check: curl http://localhost:11434/api/version")
        print("\n2. If running in a devcontainer:")
        print("   - Rebuild the container to apply port forwarding")
        print("   - Or try: OLLAMA_HOST=http://host.docker.internal:11434 python scripts/test_ollama.py")
        print("\n3. Ensure the llama3.1:8b model is installed:")
        print("   - Run: ollama pull llama3.1:8b")
        print("=" * 80)
        raise


def main():
    # Path to the jobs JSON file
    json_file = "data/raw/jobs_combined.json"

    print("=" * 80)
    print("Testing Ollama with Job Description")
    print("=" * 80)

    # Load a sample job
    print(f"\nLoading job from: {json_file}")
    job = load_sample_job(json_file)

    print(f"\nJob Title: {job['title']}")
    print(f"Company: {job['companyName']}")
    print(f"Location: {job['location']}")
    print(f"\nDescription length: {len(job['description'])} characters")

    # Extract skills and tools using Ollama
    print("\n" + "-" * 80)
    result = extract_skills_with_ollama(job['description'])

    print("\nOllama Response:")
    print("-" * 80)
    print(f"Model: {result.get('model', 'N/A')}")
    print(f"Generation time: {result.get('total_duration', 0) / 1e9:.2f} seconds")

    # Parse the response
    response_text = result.get('response', '{}')
    print(f"\nRaw response:\n{response_text}")

    try:
        extracted = json.loads(response_text)

        print("\n" + "=" * 80)
        print("EXTRACTED RESULTS")
        print("=" * 80)

        print(f"\nSKILLS ({len(extracted.get('skills', []))} found):")
        for skill in extracted.get('skills', []):
            print(f"  - {skill}")

        print(f"\nTOOLS ({len(extracted.get('tools', []))} found):")
        for tool in extracted.get('tools', []):
            print(f"  - {tool}")

    except json.JSONDecodeError as e:
        print(f"\nError parsing JSON response: {e}")
        print("Response was not valid JSON")


if __name__ == "__main__":
    main()

import json
import re

# Load the combined job data
with open('data/raw/jobs_combined.json', 'r', encoding='utf-8') as f:
    jobs = json.load(f)

def classify_language(text):
    """
    Simple heuristic to classify text as German or English.
    Returns 'German' if more German words than English words, else 'English'.
    """
    if not text or not isinstance(text, str):
        return 'Unknown'

    text_lower = text.lower()

    # Count German indicator words
    german_words = ['der', 'die', 'das', 'und', 'mit', 'für']
    german_count = sum(len(re.findall(r'\b' + word + r'\b', text_lower)) for word in german_words)

    # Count English indicator words
    english_words = ['the', 'a', 'an']
    english_count = sum(len(re.findall(r'\b' + word + r'\b', text_lower)) for word in english_words)

    return 'German' if german_count > english_count else 'English'

# Classify all jobs
for job in jobs:
    job['language'] = classify_language(job.get('description', ''))

# Count languages
german_count = sum(1 for job in jobs if job['language'] == 'German')
english_count = sum(1 for job in jobs if job['language'] == 'English')
unknown_count = sum(1 for job in jobs if job['language'] == 'Unknown')

# Display statistics
print("\n=== Language Distribution ===")
print(f"Total jobs: {len(jobs)}")
print(f"German descriptions: {german_count} ({german_count/len(jobs)*100:.1f}%)")
print(f"English descriptions: {english_count} ({english_count/len(jobs)*100:.1f}%)")
if unknown_count > 0:
    print(f"Unknown/Missing: {unknown_count} ({unknown_count/len(jobs)*100:.1f}%)")

# Get examples
german_jobs = [job for job in jobs if job['language'] == 'German']
english_jobs = [job for job in jobs if job['language'] == 'English']

# Show 5 English examples
print("\n" + "="*80)
print("=== 5 ENGLISH DESCRIPTION EXAMPLES ===")
print("="*80)
for idx, job in enumerate(english_jobs[:5], 1):
    print(f"\n--- English Example {idx} ---")
    print(f"Title: {job['title']}")
    print(f"Company: {job['companyName']}")
    print(f"Experience Level: {job.get('experienceLevel', 'N/A')}")
    print(f"\nDescription:")
    print(job['description'])
    print("\n" + "-"*80)

# Show 5 German examples
print("\n" + "="*80)
print("=== 5 GERMAN DESCRIPTION EXAMPLES ===")
print("="*80)
for idx, job in enumerate(german_jobs[:5], 1):
    print(f"\n--- German Example {idx} ---")
    print(f"Title: {job['title']}")
    print(f"Company: {job['companyName']}")
    print(f"Experience Level: {job.get('experienceLevel', 'N/A')}")
    print(f"\nDescription:")
    print(job['description'])
    print("\n" + "-"*80)
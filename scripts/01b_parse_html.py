"""
Parse HTML descriptions in jobs_combined.json to fix concatenated words.

Reads: data/raw/jobs_combined.json
Writes: data/processed/jobs_combined_clean.json

This script:
1. Uses descriptionHtml instead of description field
2. Properly parses HTML to preserve word boundaries
3. Creates a cleaned version of the full dataset
"""

import json
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))
from utils.html_parser import clean_html_description


def main():
    # Paths
    input_file = Path("data/raw/jobs_combined.json")
    output_file = Path("data/processed/jobs_combined_clean.json")
    
    print(f"Reading {len(str(input_file))} jobs from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    print(f"Loaded {len(jobs)} jobs")
    
    # Process each job
    print("Parsing HTML descriptions...")
    for i, job in enumerate(jobs, 1):
        if i % 100 == 0:
            print(f"  Processed {i}/{len(jobs)} jobs...")
        
        # Parse HTML description
        html_desc = job.get('descriptionHtml', '')
        clean_desc = clean_html_description(html_desc)
        
        # Store cleaned version
        job['description_clean'] = clean_desc
        
        # Keep original fields for reference
        # (don't delete description or descriptionHtml)
    
    # Save cleaned data
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(jobs, indent=2, ensure_ascii=False, fp=f)
    
    print(f"✓ Saved {len(jobs)} jobs with clean descriptions")
    
    # Show example
    print("\n" + "="*60)
    print("EXAMPLE: Before vs After")
    print("="*60)
    example = jobs[0]
    print(f"\nJob: {example['title']}")
    print(f"\nOriginal description (first 200 chars):")
    print(example['description'][:200] + "...")
    print(f"\nCleaned description (first 200 chars):")
    print(example['description_clean'][:200] + "...")
    print("\n✓ Check for concatenated words in original vs clean version")


if __name__ == "__main__":
    main()
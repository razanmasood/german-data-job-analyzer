"""
Sample 150 job postings from the combined dataset for annotation.

Input:  data/raw/jobs_combined.json (1,240 jobs)
Output: data/annotation/sample_150.json (150 randomly sampled jobs)
"""

import json
import os
import random
from collections import Counter


def main():
    input_path = "data/processed/jobs_combined_clean.json"
    output_dir = "data/annotation"
    output_path = os.path.join(output_dir, "sample_150.json")
    sample_size = 150

    print("=" * 80)
    print("Sampling Job Postings for Annotation")
    print("=" * 80)

    # Load combined dataset
    print(f"\nLoading jobs from: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    print(f"Total jobs loaded: {len(jobs)}")

    # Sample with fixed seed for reproducibility
    random.seed(42)
    sample = random.sample(jobs, sample_size)
    print(f"Sampled: {sample_size} jobs")

    # Summary stats
    print("\n" + "-" * 80)
    print("Sample Summary")
    print("-" * 80)

    # Experience level distribution
    exp_counts = Counter(job.get('experienceLevel', 'Unknown') for job in sample)
    print("\nExperience Level Distribution:")
    for level, count in exp_counts.most_common():
        pct = count / sample_size * 100
        print(f"  {level}: {count} ({pct:.1f}%)")

    # Search term distribution
    search_counts = Counter(job.get('Search_term', 'Unknown') for job in sample)
    print("\nSearch Term Distribution:")
    for term, count in search_counts.most_common():
        pct = count / sample_size * 100
        print(f"  {term}: {count} ({pct:.1f}%)")

    # Save sample
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 80}")
    print(f"Saved {sample_size} sampled jobs to: {output_path}")
    print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")
    print("=" * 80)


if __name__ == "__main__":
    main()

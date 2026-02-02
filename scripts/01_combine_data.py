import pandas as pd
import json

# Load both CSV files
ds_jobs = pd.read_csv('data/raw/ds_jobs.csv')
ml_jobs = pd.read_csv('data/raw/ml_jobs.csv')

# Combine into one dataframe
combined = pd.concat([ds_jobs, ml_jobs], ignore_index=True)

# Remove duplicates based on 'id' field
deduplicated = combined.drop_duplicates(subset='id', keep='first')

# Calculate statistics
total_jobs = len(deduplicated)
desc_filled = deduplicated['description'].notna().sum()
exp_filled = deduplicated['experienceLevel'].notna().sum()

# Display statistics
print(f"\n=== Data Combination Summary ===")
print(f"Total jobs after deduplication: {total_jobs}")
print(f"Jobs with 'description' filled: {desc_filled} ({desc_filled/total_jobs*100:.1f}%)")
print(f"Jobs with 'experienceLevel' filled: {exp_filled} ({exp_filled/total_jobs*100:.1f}%)")

# Sample 3 job descriptions
print(f"\n=== Sample Job Descriptions ===")
sample_jobs = deduplicated[deduplicated['description'].notna()].sample(n=3, random_state=42)
for idx, (_, row) in enumerate(sample_jobs.iterrows(), 1):
    print(f"\n--- Sample {idx} ---")
    print(f"Title: {row['title']}")
    print(f"Company: {row['companyName']}")
    print(f"Experience Level: {row['experienceLevel']}")
    print(f"\nDescription:")
    print(row['description'])

# Save to JSON
output_path = 'data/raw/jobs_combined.json'
deduplicated.to_json(output_path, orient='records', indent=2, force_ascii=False)
print(f"\n✓ Saved combined data to {output_path}")

import pandas as pd
import json
import os

# Load both CSV files
ds_jobs = pd.read_csv('data/raw/ds_jobs.csv')
ml_jobs = pd.read_csv('data/raw/ml_jobs.csv')
combined = pd.concat([ds_jobs, ml_jobs], ignore_index=True)

# --- Analysis ---
col = 'experienceLevel'
total = len(combined)
missing = combined[col].isna() | (combined[col].astype(str).str.strip().isin(['', 'nan']))
missing_count = missing.sum()
missing_pct = missing_count / total * 100
value_counts = combined[col].value_counts(dropna=False)

# --- Print results ---
print(f"\n{'='*60}")
print(f"  Experience Level Analysis")
print(f"{'='*60}")
print(f"Total rows:        {total:,}")
print(f"Missing/empty:     {missing_count:,}  ({missing_pct:.1f}%)")
print(f"Non-missing:       {total - missing_count:,}  ({100 - missing_pct:.1f}%)")
print(f"\nValue distribution:")

for val, count in value_counts.items():
    pct = count / total * 100
    label = repr(val) if pd.notna(val) else "<MISSING/NaN>"
    bar = '█' * max(1, int(pct / 2))
    print(f"  {label:35s} {count:6,}  ({pct:5.1f}%)  {bar}")

# --- Recommendation logic ---
if missing_pct > 50:
    recommendation = "BUILD A CLASSIFIER"
    reason = f"{missing_pct:.1f}% of values are missing — too many gaps to rely on existing data."
elif combined[col].nunique() > 20:
    recommendation = "BUILD A SIMPLE MAPPER"
    reason = f"{combined[col].nunique()} unique values detected — values are messy and need normalization."
elif missing_pct < 20:
    recommendation = "USE THE EXISTING DATA"
    reason = f"Only {missing_pct:.1f}% missing with {combined[col].nunique()} clean, consistent categories."
else:
    recommendation = "BUILD A SIMPLE MAPPER"
    reason = f"{missing_pct:.1f}% missing — moderate gaps that may need filling or remapping."

print(f"\n{'='*60}")
print(f"  RECOMMENDATION: {recommendation}")
print(f"{'='*60}")
print(f"  Reason: {reason}")

# --- Optional seniority grouping ---
seniority_map = {
    'Internship': 'Junior',
    'Entry level': 'Junior',
    'Associate': 'Mid',
    'Mid-Senior level': 'Senior',
    'Director': 'Senior',
    'Executive': 'Senior',
    'Not Applicable': 'Unknown',
}

print(f"\n  Optional 3-tier seniority mapping:")
for original, grouped in seniority_map.items():
    print(f"    {original:25s} -> {grouped}")

# --- Save results ---
os.makedirs('data/processed', exist_ok=True)

results = {
    'total_rows': total,
    'missing_count': int(missing_count),
    'missing_pct': round(missing_pct, 2),
    'recommendation': recommendation,
    'reason': reason,
    'value_distribution': {
        str(k): {'count': int(v), 'pct': round(v / total * 100, 2)}
        for k, v in value_counts.items()
    },
    'seniority_map': seniority_map,
}

output_path = 'data/processed/experience_level_analysis.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n  Results saved to: {output_path}")

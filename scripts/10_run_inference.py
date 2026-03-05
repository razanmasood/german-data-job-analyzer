"""
Run NER inference on all job postings to extract SKILL and TOOL entities.

Loads the fine-tuned xlm-roberta-large model and processes each job's
description_clean text, extracting entities via offset mapping to avoid
subword artifacts. Saves per-job results and aggregated statistics.
"""

import json
from collections import Counter
from itertools import combinations
from pathlib import Path

import torch
from tqdm import tqdm
from transformers import AutoModelForTokenClassification, AutoTokenizer

MODEL_PATH = Path("models/ner/best")
LABEL_MAP_PATH = Path("data/processed/ner_dataset/label_map.json")
JOBS_PATH = Path("data/processed/jobs_combined_clean.json")
INFERENCE_OUTPUT = Path("data/processed/inference_results.json")
ANALYZED_OUTPUT = Path("data/analyzed/results.json")


def load_resources():
    """Load model, tokenizer, label map, and job data."""
    with open(LABEL_MAP_PATH, "r", encoding="utf-8") as f:
        label_map = json.load(f)
    label_list = label_map["label_list"]

    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH))
    model = AutoModelForTokenClassification.from_pretrained(str(MODEL_PATH))
    model.eval()

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model.to(device)

    with open(JOBS_PATH, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    return model, tokenizer, label_list, jobs, device


def extract_entities(text, model, tokenizer, label_list, device):
    """Run inference on a single text and extract entity spans."""
    encoding = tokenizer(
        text,
        return_offsets_mapping=True,
        truncation=True,
        max_length=512,
        return_tensors="pt",
    )

    offset_mapping = encoding.pop("offset_mapping")[0].tolist()
    input_ids = encoding["input_ids"].to(device)
    attention_mask = encoding["attention_mask"].to(device)

    with torch.no_grad():
        logits = model(input_ids=input_ids, attention_mask=attention_mask).logits

    pred_ids = torch.argmax(logits, dim=-1)[0].tolist()

    # Walk predictions and offset mapping to extract entity text
    entities = []
    current_entity = None

    for idx, (pred_id, (start, end)) in enumerate(zip(pred_ids, offset_mapping)):
        # Skip special tokens
        if start == 0 and end == 0:
            continue

        tag = label_list[pred_id]

        if tag.startswith("B-"):
            # Save previous entity if any
            if current_entity is not None:
                entities.append(current_entity)
            entity_type = tag[2:]  # SKILL or TOOL
            current_entity = {
                "type": entity_type,
                "char_start": start,
                "char_end": end,
            }
        elif tag.startswith("I-") and current_entity is not None:
            expected_type = tag[2:]
            if expected_type == current_entity["type"]:
                current_entity["char_end"] = end
            else:
                # Type mismatch — close current, skip this token
                entities.append(current_entity)
                current_entity = None
        else:
            # O tag — close current entity
            if current_entity is not None:
                entities.append(current_entity)
                current_entity = None

    # Don't forget the last entity
    if current_entity is not None:
        entities.append(current_entity)

    # Slice entity text from original string and deduplicate
    seen_skills = set()
    seen_tools = set()
    skills = []
    tools = []

    for ent in entities:
        entity_text = text[ent["char_start"]:ent["char_end"]].strip()
        if not entity_text:
            continue
        key = entity_text.lower()
        if ent["type"] == "SKILL":
            if key not in seen_skills:
                seen_skills.add(key)
                skills.append(entity_text)
        else:
            if key not in seen_tools:
                seen_tools.add(key)
                tools.append(entity_text)

    return sorted(skills, key=str.lower), sorted(tools, key=str.lower)


def compute_aggregated_stats(results):
    """Compute aggregated statistics from per-job results."""
    skill_counter = Counter()
    tool_counter = Counter()
    skills_by_level = {}
    tools_by_level = {}
    skill_cooccurrence = Counter()

    for job in results:
        level = job["experience_level"]
        skills_lower = [s.lower() for s in job["skills"]]
        tools_lower = [t.lower() for t in job["tools"]]

        for s in skills_lower:
            skill_counter[s] += 1
        for t in tools_lower:
            tool_counter[t] += 1

        # Per experience level
        if level not in skills_by_level:
            skills_by_level[level] = Counter()
            tools_by_level[level] = Counter()
        for s in skills_lower:
            skills_by_level[level][s] += 1
        for t in tools_lower:
            tools_by_level[level][t] += 1

        # Skill co-occurrence (pairs within same job)
        for a, b in combinations(sorted(set(skills_lower)), 2):
            skill_cooccurrence[(a, b)] += 1

    total_jobs = len(results)
    total_skills = sum(len(j["skills"]) for j in results)
    total_tools = sum(len(j["tools"]) for j in results)

    def counter_to_list(counter):
        return [{"name": name, "count": count}
                for name, count in counter.most_common()]

    stats = {
        "top_skills": counter_to_list(skill_counter),
        "top_tools": counter_to_list(tool_counter),
        "skills_by_experience_level": {
            level: counter_to_list(c) for level, c in skills_by_level.items()
        },
        "tools_by_experience_level": {
            level: counter_to_list(c) for level, c in tools_by_level.items()
        },
        "skill_cooccurrence": [
            {"pair": list(pair), "count": count}
            for pair, count in skill_cooccurrence.most_common(50)
        ],
        "summary": {
            "total_jobs": total_jobs,
            "total_unique_skills": len(skill_counter),
            "total_unique_tools": len(tool_counter),
            "avg_skills_per_job": round(total_skills / total_jobs, 2) if total_jobs else 0,
            "avg_tools_per_job": round(total_tools / total_jobs, 2) if total_jobs else 0,
        },
    }
    return stats


def main():
    """Run NER inference on all job postings using the fine-tuned model.

    Loads xlm-roberta from models/ner/best/, processes each job's
    description_clean field, and saves per-job entity results and
    aggregated statistics (top skills/tools, co-occurrence, by experience level).
    """
    print("=" * 60)
    print("NER Inference on Full Dataset")
    print("=" * 60)

    # Load everything
    print("\nLoading model, tokenizer, and data...")
    model, tokenizer, label_list, jobs, device = load_resources()
    print(f"  Model loaded on: {device}")
    print(f"  Jobs to process: {len(jobs)}")

    # Run inference
    results = []
    for job in tqdm(jobs, desc="Running inference"):
        try:
            text = job.get("description_clean", "")
            if not text:
                skills, tools = [], []
            else:
                skills, tools = extract_entities(text, model, tokenizer, label_list, device)

            results.append({
                "id": job["id"],
                "experience_level": job.get("experienceLevel", ""),
                "skills": skills,
                "tools": tools,
            })
        except Exception as e:
            print(f"\n  ERROR on job {job.get('id', '?')} — {e} (skipping)")

    # Save per-job results
    INFERENCE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(INFERENCE_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved per-job results to {INFERENCE_OUTPUT}")

    # Compute and save aggregated stats
    stats = compute_aggregated_stats(results)
    ANALYZED_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(ANALYZED_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"Saved aggregated stats to {ANALYZED_OUTPUT}")

    # Print summary
    s = stats["summary"]
    print(f"\n{'=' * 60}")
    print(f"Summary")
    print(f"{'=' * 60}")
    print(f"  Total jobs processed:  {s['total_jobs']}")
    print(f"  Total unique skills:   {s['total_unique_skills']}")
    print(f"  Total unique tools:    {s['total_unique_tools']}")
    print(f"  Avg skills per job:    {s['avg_skills_per_job']}")
    print(f"  Avg tools per job:     {s['avg_tools_per_job']}")

    print(f"\nTop 10 Skills:")
    for item in stats["top_skills"][:10]:
        print(f"  {item['count']:4d}  {item['name']}")

    print(f"\nTop 10 Tools:")
    for item in stats["top_tools"][:10]:
        print(f"  {item['count']:4d}  {item['name']}")

    print(f"\n{'=' * 60}")
    print("Done!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

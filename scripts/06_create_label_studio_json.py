# File: 03_create_label_studio_json.py
# Purpose: Convert LLM entity extractions to Label Studio format with character positions

import json
from pathlib import Path
from typing import List, Dict, Tuple

def find_entity_positions(text: str, entity: str) -> List[Tuple[int, int]]:
    """
    Find all occurrences of an entity in text and return (start, end) positions.
    
    Args:
        text: The job description text
        entity: The entity string to find
        
    Returns:
        List of (start, end) tuples for all occurrences
    """
    positions = []
    start = 0
    while True:
        pos = text.find(entity, start)
        if pos == -1:
            break
        positions.append((pos, pos + len(entity)))
        start = pos + 1  # Continue searching after this match
    
    return positions

def create_label_studio_task(job_data: Dict) -> Dict:
    """
    Convert a job posting with LLM extractions to Label Studio format.
    
    Args:
        job_data: Job dict with entities.skills, entities.tools, requirements_sectionß
    
    Returns:
        Label Studio task dict with data and predictions
    """
    # Use requirements_section if available, otherwise fall back to full description
    req = job_data.get("requirements_section")
    text = req if req else job_data.get("description", "")

    task = {
        "data": {
            "text": text,
            "meta": {
                "id": job_data["id"],
                "title": job_data["jobTitle"],
                "language": job_data["language"]
            }
        },
        "predictions": [
            {
                "result": []
            }
        ]
    }
    result = task["predictions"][0]["result"]
    
    # Track which positions we've already annotated to avoid duplicates
    annotated_positions = set()
    
    # Get entities from nested structure
    entities = job_data.get("entities", {})
    
    # Process skills
    for skill in entities.get("skills", []):
        positions = find_entity_positions(text, skill)
        for start, end in positions:
            # Only add if this exact position hasn't been annotated
            if (start, end) not in annotated_positions:
                result.append({
                    "value": {
                        "start": start,
                        "end": end,
                        "text": skill,
                        "labels": ["SKILL"]
                    },
                    "from_name": "label",
                    "to_name": "text",
                    "type": "labels"
                })
                annotated_positions.add((start, end))
    
    # Process tools
    for tool in entities.get("tools", []):
        positions = find_entity_positions(text, tool)
        for start, end in positions:
            if (start, end) not in annotated_positions:
                result.append({
                    "value": {
                        "start": start,
                        "end": end,
                        "text": tool,
                        "labels": ["TOOL"]
                    },
                    "from_name": "label",
                    "to_name": "text",
                    "type": "labels"
                })
                annotated_positions.add((start, end))
    
    return task

def main():
    # Paths
    data_dir = Path("data")
    annotation_dir = data_dir / "annotation"
    input_path = annotation_dir / "annotations_llm_150.json"
    output_path = annotation_dir / "label_studio_tasks_with_predictions.json"
    
    # Load LLM annotations
    print(f"Loading {input_path}...")
    with open(input_path, encoding='utf-8') as f:
        job_data = json.load(f)
    
    print(f"Processing {len(job_data)} job postings...")
    
    # Convert to Label Studio format
    label_studio_tasks = []
    skipped = 0
    not_found = 0
    
    for job in job_data:
        # Create task (includes all 150 jobs)
        task = create_label_studio_task(job)

        # Check if any entities were actually found in text
        entities = job.get("entities", {})
        skills = entities.get("skills", [])
        tools = entities.get("tools", [])

        if not skills and not tools:
            skipped += 1
        elif not task["predictions"][0]["result"]:
            not_found += 1
            print(f"Warning: No entities found in text for job {job['id']}")

        label_studio_tasks.append(task)
    
    # Save
    print(f"Saving {len(label_studio_tasks)} tasks to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(label_studio_tasks, f, ensure_ascii=False, indent=2)
    
    print(f"\nDone!")
    print(f"   Total tasks:           {len(label_studio_tasks)}")
    print(f"   With pre-annotations:  {len(label_studio_tasks) - skipped}")
    print(f"   No entities (fallback): {skipped}")
    if not_found > 0:
        print(f"   Warning: {not_found} jobs where entities weren't found in text")

if __name__ == "__main__":
    main()
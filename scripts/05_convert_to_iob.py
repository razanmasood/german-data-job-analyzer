"""
Convert Label Studio JSON export to IOB-tagged HuggingFace Dataset.

Reads character-level entity annotations, aligns them to xlm-roberta-large
subword tokens using offset mapping, and saves train/val/test splits.
"""

import json
from pathlib import Path

from datasets import Dataset, DatasetDict, ClassLabel, Sequence, Value, Features
from sklearn.model_selection import train_test_split
from tqdm import tqdm
from transformers import AutoTokenizer


# Label mapping
LABEL_LIST = ["O", "B-SKILL", "I-SKILL", "B-TOOL", "I-TOOL"]
LABEL2ID = {label: i for i, label in enumerate(LABEL_LIST)}

INPUT_PATH = Path("data/annotation/label_studio_export.json")
OUTPUT_PATH = Path("data/processed/ner_dataset")
MODEL_NAME = "xlm-roberta-large"
SEED = 42


def extract_entities(annotation_result):
    """Extract sorted entity spans from a Label Studio annotation result."""
    entities = []
    for item in annotation_result:
        if item.get("from_name") != "label":
            continue
        value = item["value"]
        entities.append({
            "start": value["start"],
            "end": value["end"],
            "label": value["labels"][0],
        })
    entities.sort(key=lambda e: e["start"])
    return entities


def assign_iob_tags(offset_mapping, entities):
    """Assign IOB tags to tokens based on character offset alignment.

    For each token, checks if its character span falls within an entity span.
    The first token overlapping an entity gets B-, subsequent tokens get I-.
    Special tokens (offset 0,0) get -100.
    """
    tags = []
    entity_idx = 0
    n_entities = len(entities)

    for token_start, token_end in offset_mapping:
        # Special tokens (<s>, </s>, <pad>)
        if token_start == 0 and token_end == 0:
            tags.append(-100)
            continue

        tag = LABEL2ID["O"]

        # Advance entity pointer past tokens we've passed
        while entity_idx < n_entities and entities[entity_idx]["end"] <= token_start:
            entity_idx += 1

        if entity_idx < n_entities:
            ent = entities[entity_idx]
            # Check if token overlaps with current entity
            if token_start >= ent["start"] and token_start < ent["end"]:
                label = ent["label"]
                # B- if this is the first token of the entity
                if token_start <= ent["start"]:
                    tag = LABEL2ID[f"B-{label}"]
                else:
                    tag = LABEL2ID[f"I-{label}"]

        # Also check previous entity (token might still be inside it)
        if tag == LABEL2ID["O"] and entity_idx > 0:
            prev_ent = entities[entity_idx - 1]
            if token_start >= prev_ent["start"] and token_start < prev_ent["end"]:
                tag = LABEL2ID[f"I-{prev_ent['label']}"]

        tags.append(tag)

    return tags


def convert_entry(entry, tokenizer):
    """Convert a single Label Studio entry to tokenized IOB format."""
    text = entry["data"]["text"]
    annotation = entry["annotations"][0]
    entities = extract_entities(annotation["result"])

    encoding = tokenizer(
        text,
        return_offsets_mapping=True,
        truncation=True,
        max_length=512,
    )

    offset_mapping = encoding["offset_mapping"]
    tags = assign_iob_tags(offset_mapping, entities)

    tokens = tokenizer.convert_ids_to_tokens(encoding["input_ids"])

    return {
        "id": entry["id"],
        "tokens": tokens,
        "ner_tags": tags,
        "input_ids": encoding["input_ids"],
        "attention_mask": encoding["attention_mask"],
    }


def print_alignment_sample(example, n=3):
    """Print a few entity examples to verify token-label alignment."""
    tokens = example["tokens"]
    tags = example["ner_tags"]
    print(f"\n  Sample entities (id={example['id']}):")
    count = 0
    i = 0
    while i < len(tags) and count < n:
        if tags[i] > 0:  # B- or I- tag
            entity_tokens = [tokens[i]]
            entity_tag = LABEL_LIST[tags[i]]
            j = i + 1
            while j < len(tags) and tags[j] in (LABEL2ID["I-SKILL"], LABEL2ID["I-TOOL"]):
                entity_tokens.append(tokens[j])
                j += 1
            text = "".join(t.replace("▁", " ") for t in entity_tokens).strip()
            print(f"    {entity_tag}: \"{text}\" (tokens {i}-{j-1})")
            count += 1
            i = j
        else:
            i += 1


def main():
    """Convert Label Studio annotations to an IOB-tagged HuggingFace DatasetDict.

    Reads human-corrected annotations from Label Studio export, tokenizes with
    xlm-roberta-large, aligns entity spans to token offsets, and saves
    train/val/test splits to data/processed/ner_dataset/.
    """
    print("=" * 60)
    print("Label Studio → IOB Conversion")
    print("=" * 60)

    # Load data
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"\n✓ Loaded {len(data)} entries from {INPUT_PATH}")

    # Load tokenizer
    print(f"  Loading tokenizer: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # Convert all entries
    print(f"\n  Converting to IOB format...")
    examples = []
    total_entities = {"SKILL": 0, "TOOL": 0}
    for entry in tqdm(data, desc="  Processing"):
        example = convert_entry(entry, tokenizer)
        examples.append(example)
        for tag_id in example["ner_tags"]:
            if tag_id == LABEL2ID["B-SKILL"]:
                total_entities["SKILL"] += 1
            elif tag_id == LABEL2ID["B-TOOL"]:
                total_entities["TOOL"] += 1

    print(f"\n✓ Converted {len(examples)} entries")
    print(f"  Total entities: {total_entities['SKILL']} SKILL, {total_entities['TOOL']} TOOL")

    # Show alignment samples
    print("\n  Alignment verification:")
    for ex in examples[:2]:
        print_alignment_sample(ex)

    # Train/val/test split (70/15/15)
    train_data, temp_data = train_test_split(
        examples, test_size=0.30, random_state=SEED
    )
    val_data, test_data = train_test_split(
        temp_data, test_size=0.50, random_state=SEED
    )

    print(f"\n  Split sizes:")
    print(f"    Train: {len(train_data)}")
    print(f"    Val:   {len(val_data)}")
    print(f"    Test:  {len(test_data)}")

    # Build HuggingFace DatasetDict
    features = Features({
        "id": Value("int32"),
        "tokens": Sequence(Value("string")),
        "ner_tags": Sequence(Value("int32")),
        "input_ids": Sequence(Value("int32")),
        "attention_mask": Sequence(Value("int32")),
    })

    def list_of_dicts_to_dict_of_lists(records):
        return {key: [r[key] for r in records] for key in records[0]}

    dataset_dict = DatasetDict({
        "train": Dataset.from_dict(list_of_dicts_to_dict_of_lists(train_data), features=features),
        "validation": Dataset.from_dict(list_of_dicts_to_dict_of_lists(val_data), features=features),
        "test": Dataset.from_dict(list_of_dicts_to_dict_of_lists(test_data), features=features),
    })

    # Save
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    dataset_dict.save_to_disk(str(OUTPUT_PATH))
    print(f"\n✓ Saved dataset to {OUTPUT_PATH}/")

    # Save label mapping for reference
    label_map_path = OUTPUT_PATH / "label_map.json"
    with open(label_map_path, "w", encoding="utf-8") as f:
        json.dump({"label_list": LABEL_LIST, "label2id": LABEL2ID}, f, indent=2)
    print(f"✓ Saved label mapping to {label_map_path}")

    print(f"\n{'=' * 60}")
    print("Done!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

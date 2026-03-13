"""
03_compare_results.py
---------------------
Load result files from the NER comparison experiments and produce a formatted
comparison table plus a summary JSON file.

Models compared
---------------
1. Baseline          -- xlm-roberta-large fine-tuned with HuggingFace Trainer
                        (src/training/train_ner.py, 10 epochs, Apple M4 MPS).
                        Test metrics from README: P=0.644, R=0.690, F1=0.666.
                        Per-entity breakdown not recorded.
2. GLiNER zero-shot  -- urchade/gliner_multi-v2.1 at default threshold (0.5).
                        Results from experiments/ner_comparison/results/gliner_results.json.
3. SpanMarker fine-  -- xlm-roberta backbone fine-tuned with SpanMarker.
   tuned               Results from experiments/ner_comparison/results/spanmarker_results.json.
                        Skipped gracefully if the file does not yet exist.

Output
------
  - Formatted comparison table printed to stdout.
  - experiments/ner_comparison/results/comparison_summary.json

Usage
-----
    python experiments/ner_comparison/03_compare_results.py
"""

import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
RESULTS_DIR      = Path(__file__).resolve().parent / "results"
GLINER_FILE      = RESULTS_DIR / "gliner_results.json"
SPANMARKER_FILE  = RESULTS_DIR / "spanmarker_results.json"
SUMMARY_FILE     = RESULTS_DIR / "comparison_summary.json"

# ---------------------------------------------------------------------------
# Baseline -- xlm-roberta-large fine-tuned via HuggingFace Trainer
# (src/training/train_ner.py, 10 epochs on Apple M4 MPS).
# Metrics sourced from README.md; per-entity breakdown not recorded.
# ---------------------------------------------------------------------------
BASELINE = {
    "precision": 0.644,
    "recall":    0.690,
    "f1":        0.666,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_entity_metrics(report: str, entity: str) -> dict | None:
    """Extract precision, recall, and F1 for *entity* from a seqeval
    classification_report string.

    seqeval formats each entity row as (whitespace-flexible):
        ENTITY   <precision>   <recall>   <f1-score>   <support>

    Returns None if the entity is not found in the report.
    """
    pattern = rf"^\s*{re.escape(entity)}\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+\d+"
    match = re.search(pattern, report, re.MULTILINE)
    if not match:
        return None
    return {
        "precision": float(match.group(1)),
        "recall":    float(match.group(2)),
        "f1":        float(match.group(3)),
    }


def load_gliner(path: Path) -> dict:
    """Load GLiNER results and return a normalised model-entry dict."""
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)

    # Use the default-threshold section (0.5)
    section = raw["default_threshold"]
    report  = section["classification_report"]

    return {
        "model":             raw["model"],
        "approach":          "zero-shot",
        "num_test_examples": raw["num_test_examples"],
        "overall":           section["overall"],
        "per_entity": {
            entity: parse_entity_metrics(report, entity)
            for entity in raw.get("entity_labels", ["SKILL", "TOOL"])
        },
        "inference_time_seconds": section.get("inference_time_seconds"),
        "notes": f"threshold={section['threshold']}",
    }


def load_spanmarker(path: Path) -> dict:
    """Load SpanMarker results and return a normalised model-entry dict."""
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)

    results = raw["test_results"]
    report  = results["classification_report"]

    return {
        "model":             raw["model"],
        "approach":          "fine-tuned",
        "num_test_examples": raw["num_test_examples"],
        "overall":           results["overall"],
        "per_entity": {
            entity: parse_entity_metrics(report, entity)
            for entity in raw.get("entity_labels", ["SKILL", "TOOL"])
        },
        "inference_time_seconds": results.get("inference_time_seconds"),
        "notes": (
            f"epochs={raw['training']['max_epochs']}, lr={raw['training']['learning_rate']}"
            if "training" in raw
            else "training metadata unavailable"
        ),
    }


def baseline_entry() -> dict:
    """Construct a normalised entry for the xlm-roberta-large baseline."""
    return {
        "model":             "xlm-roberta-large (HuggingFace Trainer, baseline)",
        "approach":          "fine-tuned",
        "num_test_examples": 23,
        "overall":           BASELINE,
        "per_entity": {
            "SKILL": None,
            "TOOL":  None,
        },
        "inference_time_seconds": None,
        "notes": (
            "10 epochs, batch 2 + grad-accum 4, lr 2e-5, Apple M4 MPS; "
            "per-entity breakdown not recorded"
        ),
    }


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt(value) -> str:
    """Format a number as 4 decimal places, or return 'N/A' for None."""
    if value is None:
        return "N/A"
    return f"{value:.4f}"


def print_table(models: list[dict]) -> None:
    """Print a comparison table to stdout."""
    col_w  = 36   # model-name column width
    num_w  = 9    # numeric column width
    metric_keys = ["precision", "recall", "f1"]
    sections = [
        ("Overall", "overall"),
        ("SKILL",   "per_entity.SKILL"),
        ("TOOL",    "per_entity.TOOL"),
    ]

    # Total width
    total_w = col_w + len(sections) * 3 * (num_w + 2)

    # Section header (centred over each group of 3 columns)
    group_w = 3 * (num_w + 2)
    print()
    print(f"{'Model':<{col_w}}", end="")
    for label, _ in sections:
        print(f"  {label:^{group_w - 2}}", end="")
    print()

    # Metric sub-header
    print(f"{'':{ col_w}}", end="")
    for _ in sections:
        for m in ["Precision", "Recall", "F1"]:
            print(f"  {m:>{num_w}}", end="")
    print()

    print("-" * total_w)

    # Data rows
    for entry in models:
        print(f"{entry['model']:<{col_w}}", end="")
        for _, key_path in sections:
            # Traverse dotted path, e.g. "per_entity.SKILL"
            node: dict | None = entry
            for part in key_path.split("."):
                node = node.get(part) if isinstance(node, dict) else None
                if node is None:
                    break
            for metric in metric_keys:
                val = node.get(metric) if isinstance(node, dict) else None
                print(f"  {fmt(val):>{num_w}}", end="")
        print()

    print("-" * total_w)
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    models: list[dict] = []

    # 1. Baseline
    models.append(baseline_entry())

    # 2. GLiNER
    if GLINER_FILE.exists():
        models.append(load_gliner(GLINER_FILE))
        print(f"Loaded GLiNER results      : {GLINER_FILE.name}")
    else:
        print(f"WARNING: {GLINER_FILE} not found — skipping GLiNER.")

    # 3. SpanMarker
    if SPANMARKER_FILE.exists():
        models.append(load_spanmarker(SPANMARKER_FILE))
        print(f"Loaded SpanMarker results  : {SPANMARKER_FILE.name}")
    else:
        print(f"NOTE: {SPANMARKER_FILE} not found — SpanMarker row omitted.")

    print_table(models)

    # Save JSON summary
    summary = {
        "description": (
            "NER model comparison: xlm-roberta-large baseline (HuggingFace Trainer) "
            "vs GLiNER zero-shot vs xlm-roberta-large fine-tuned with SpanMarker. "
            "Metrics evaluated on the held-out test split (23 sentences) of the "
            "annotated skill/tool dataset."
        ),
        "entity_labels": ["SKILL", "TOOL"],
        "models": models,
    }

    with open(SUMMARY_FILE, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)

    print(f"Comparison summary saved to {SUMMARY_FILE}")


if __name__ == "__main__":
    main()

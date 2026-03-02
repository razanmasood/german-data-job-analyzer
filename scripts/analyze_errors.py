"""
NER error analysis script.

Runs inference on the test set, compares predicted spans against gold spans,
categorizes every error, and writes a human-readable report to docs/error_analysis.md.
"""

import json
from pathlib import Path

import numpy as np
import torch
from datasets import DatasetDict
from transformers import AutoModelForTokenClassification, AutoTokenizer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "ner_dataset"
MODEL_PATH = PROJECT_ROOT / "models" / "ner" / "best"
REPORT_PATH = PROJECT_ROOT / "docs" / "error_analysis.md"


def load_label_map():
    """Load label list and ID mappings from the NER dataset label_map.json."""
    with open(DATASET_PATH / "label_map.json") as f:
        return json.load(f)


def extract_spans(tag_ids, label_list):
    """Walk IOB tag IDs and return a list of (start, end, entity_type) spans.

    start and end are token indices (inclusive start, exclusive end).
    entity_type is 'SKILL' or 'TOOL'.
    """
    spans = []
    current_start = None
    current_type = None

    for i, tid in enumerate(tag_ids):
        label = label_list[tid]
        if label.startswith("B-"):
            # Close previous span if open
            if current_start is not None:
                spans.append((current_start, i, current_type))
            current_type = label[2:]  # SKILL or TOOL
            current_start = i
        elif label.startswith("I-"):
            etype = label[2:]
            if current_start is not None and etype == current_type:
                # Continue current span
                pass
            else:
                # I- without matching B- — treat as new span start
                if current_start is not None:
                    spans.append((current_start, i, current_type))
                current_type = etype
                current_start = i
        else:
            # O tag — close any open span
            if current_start is not None:
                spans.append((current_start, i, current_type))
                current_start = None
                current_type = None

    # Close final span if still open
    if current_start is not None:
        spans.append((current_start, len(tag_ids), current_type))

    return spans


def spans_overlap(s1, s2):
    """Check if two (start, end, type) spans overlap."""
    return s1[0] < s2[1] and s2[0] < s1[1]


def categorize_errors(gold_spans, pred_spans):
    """Compare gold vs predicted spans and categorize errors.

    Returns dict with keys: missed, false_alarm, label_confusion, boundary_error, correct.
    Each value is a list of dicts with error details.
    """
    errors = {
        "missed": [],
        "false_alarm": [],
        "label_confusion": [],
        "boundary_error": [],
        "correct": [],
    }

    gold_matched = set()
    pred_matched = set()

    # For each gold span, find overlapping predictions
    for gi, gs in enumerate(gold_spans):
        overlapping = []
        for pi, ps in enumerate(pred_spans):
            if spans_overlap(gs, ps):
                overlapping.append((pi, ps))

        if not overlapping:
            errors["missed"].append({"gold": gs})
            continue

        # Pick best overlapping prediction (exact match first, then same type, then any)
        best_pi, best_ps = None, None
        for pi, ps in overlapping:
            if ps == gs:
                best_pi, best_ps = pi, ps
                break
        if best_ps is None:
            for pi, ps in overlapping:
                if ps[2] == gs[2]:
                    best_pi, best_ps = pi, ps
                    break
        if best_ps is None:
            best_pi, best_ps = overlapping[0]

        gold_matched.add(gi)
        pred_matched.add(best_pi)

        if best_ps == gs:
            errors["correct"].append({"gold": gs, "pred": best_ps})
        elif best_ps[2] != gs[2]:
            errors["label_confusion"].append({"gold": gs, "pred": best_ps})
        else:
            # Same type, different boundaries
            errors["boundary_error"].append({"gold": gs, "pred": best_ps})

    # Predicted spans with no overlapping gold span
    for pi, ps in enumerate(pred_spans):
        if pi not in pred_matched:
            errors["false_alarm"].append({"pred": ps})

    return errors


def span_to_text(tokens, span):
    """Convert a (start, end, type) span to its token text."""
    return " ".join(tokens[span[0]:span[1]])


def run_inference(dataset_test, model, tokenizer, label_list, device):
    """Run inference on each test sample and return predictions."""
    model.eval()
    results = []

    for idx in range(len(dataset_test)):
        sample = dataset_test[idx]
        input_ids = torch.tensor([sample["input_ids"]], device=device)
        attention_mask = torch.tensor([sample["attention_mask"]], device=device)
        gold_tags = np.array(sample["ner_tags"])
        tokens = sample["tokens"]

        with torch.no_grad():
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits[0].cpu().numpy()
        pred_tag_ids = np.argmax(logits, axis=-1)

        # Build valid mask: positions where gold != -100
        valid_mask = gold_tags != -100
        gold_valid = gold_tags[valid_mask]
        pred_valid = pred_tag_ids[valid_mask]

        # Extract spans
        gold_spans = extract_spans(gold_valid.tolist(), label_list)
        pred_spans = extract_spans(pred_valid.tolist(), label_list)

        # Categorize
        errors = categorize_errors(gold_spans, pred_spans)

        results.append({
            "sample_id": sample["id"],
            "tokens": tokens,
            "gold_spans": gold_spans,
            "pred_spans": pred_spans,
            "errors": errors,
        })

    return results


def generate_report(results, label_list):
    """Generate a markdown error analysis report."""
    # Aggregate counts
    counts = {"missed": 0, "false_alarm": 0, "label_confusion": 0, "boundary_error": 0, "correct": 0}
    all_errors = {"missed": [], "false_alarm": [], "label_confusion": [], "boundary_error": []}

    for r in results:
        for cat in counts:
            counts[cat] += len(r["errors"][cat])
        for cat in all_errors:
            for err in r["errors"][cat]:
                all_errors[cat].append({**err, "sample_id": r["sample_id"], "tokens": r["tokens"]})

    total_gold = sum(len(r["gold_spans"]) for r in results)
    total_pred = sum(len(r["pred_spans"]) for r in results)
    total_errors = counts["missed"] + counts["false_alarm"] + counts["label_confusion"] + counts["boundary_error"]

    lines = []
    lines.append("# NER Error Analysis Report\n")
    lines.append("## Summary\n")
    lines.append(f"- **Test samples**: {len(results)}")
    lines.append(f"- **Gold entities**: {total_gold}")
    lines.append(f"- **Predicted entities**: {total_pred}")
    lines.append(f"- **Correct**: {counts['correct']}")
    lines.append(f"- **Total errors**: {total_errors}")
    lines.append("")

    lines.append("### Error Breakdown\n")
    lines.append("| Category | Count | % of Errors |")
    lines.append("|----------|------:|------------:|")
    for cat, label in [
        ("missed", "Missed entity (FN)"),
        ("false_alarm", "False alarm (FP)"),
        ("label_confusion", "Label confusion"),
        ("boundary_error", "Boundary error"),
    ]:
        pct = (counts[cat] / total_errors * 100) if total_errors > 0 else 0
        lines.append(f"| {label} | {counts[cat]} | {pct:.1f}% |")
    lines.append("")

    # Per-category detail sections
    category_info = [
        ("missed", "Missed Entities (False Negatives)",
         "Gold entities that the model failed to predict at all."),
        ("false_alarm", "False Alarms (False Positives)",
         "Predicted entities that do not overlap with any gold entity."),
        ("label_confusion", "Label Confusions",
         "Predicted entities that overlap a gold entity but have the wrong type (SKILL vs TOOL)."),
        ("boundary_error", "Boundary Errors",
         "Predicted entities that overlap a gold entity with the correct type but wrong boundaries."),
    ]

    for cat, title, description in category_info:
        lines.append(f"## {title}\n")
        lines.append(f"{description}\n")

        if not all_errors[cat]:
            lines.append("_No errors in this category._\n")
            continue

        for i, err in enumerate(all_errors[cat], 1):
            tokens = err["tokens"]
            lines.append(f"### {i}. Sample {err['sample_id']}\n")

            if "gold" in err:
                gs = err["gold"]
                gold_text = span_to_text(tokens, gs)
                lines.append(f"- **Gold**: `{gold_text}` ({gs[2]}) [tokens {gs[0]}:{gs[1]}]")

            if "pred" in err:
                ps = err["pred"]
                pred_text = span_to_text(tokens, ps)
                lines.append(f"- **Pred**: `{pred_text}` ({ps[2]}) [tokens {ps[0]}:{ps[1]}]")

            # Show context: a window around the span
            if "gold" in err:
                s, e = err["gold"][0], err["gold"][1]
            else:
                s, e = err["pred"][0], err["pred"][1]
            ctx_start = max(0, s - 3)
            ctx_end = min(len(tokens), e + 3)
            context = " ".join(tokens[ctx_start:ctx_end])
            lines.append(f"- **Context**: ...{context}...")
            lines.append("")

    return "\n".join(lines)


def main():
    """Run NER inference on the test set and write a detailed error analysis report.

    Loads the fine-tuned model, runs predictions on the held-out test split,
    categorizes span-level errors (missed, wrong type, boundary), and saves
    a full report to data/analyzed/ner_error_report.txt.
    """
    print("NER Error Analysis")
    print("=" * 50)

    # Device
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    print(f"Device: {device}")

    # Load label map
    label_map = load_label_map()
    label_list = label_map["label_list"]
    print(f"Labels: {label_list}")

    # Load dataset
    print(f"Loading dataset from {DATASET_PATH}")
    dataset = DatasetDict.load_from_disk(str(DATASET_PATH))
    test_data = dataset["test"]
    print(f"Test samples: {len(test_data)}")

    # Load model and tokenizer
    print(f"Loading model from {MODEL_PATH}")
    model = AutoModelForTokenClassification.from_pretrained(str(MODEL_PATH))
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH))
    model.to(device)
    print(f"Model loaded ({model.num_parameters():,} params)")

    # Run inference
    print("Running inference on test set...")
    results = run_inference(test_data, model, tokenizer, label_list, device)

    # Generate report
    print("Generating report...")
    report = generate_report(results, label_list)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        f.write(report)
    print(f"Report written to {REPORT_PATH}")

    # Print quick summary
    total_errors = sum(
        len(r["errors"][cat])
        for r in results
        for cat in ["missed", "false_alarm", "label_confusion", "boundary_error"]
    )
    total_correct = sum(len(r["errors"]["correct"]) for r in results)
    print(f"\nCorrect: {total_correct}, Errors: {total_errors}")


if __name__ == "__main__":
    main()

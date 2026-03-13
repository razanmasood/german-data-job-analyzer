"""
02b_spanmarker_eval.py
----------------------
Evaluate the already-trained SpanMarker model on the held-out test split.
Loads the saved model from experiments/ner_comparison/models/spanmarker/ and
produces the same spanmarker_results.json as 02_spanmarker_train.py would.

Usage
-----
    python experiments/ner_comparison/02b_spanmarker_eval.py
"""

import json
import os
import time
from pathlib import Path

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

from datasets import load_from_disk
from span_marker.tokenizer import SpanMarkerTokenizer
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score
from seqeval.scheme import IOB2
from span_marker import SpanMarkerModel, Trainer
from transformers import TrainingArguments

# ---------------------------------------------------------------------------
# Paths (mirrors 02_spanmarker_train.py)
# ---------------------------------------------------------------------------
REPO_ROOT    = Path(__file__).resolve().parents[2]
DATASET_DIR  = REPO_ROOT / "data" / "processed" / "ner_dataset"
RESULTS_DIR  = Path(__file__).resolve().parent / "results"
RESULTS_FILE = RESULTS_DIR / "spanmarker_results.json"
MODEL_DIR    = Path(__file__).resolve().parent / "models" / "spanmarker"
CKPT_DIR     = Path(__file__).resolve().parent / "models" / "spanmarker_checkpoints"

BACKBONE       = "xlm-roberta-large"
ENTITY_LABELS  = ["SKILL", "TOOL"]
BATCH_SIZE     = 4

ID2IOB = {
    -100: None,
    0:    "O",
    1:    "B-SKILL",
    2:    "I-SKILL",
    3:    "B-TOOL",
    4:    "I-TOOL",
}

# ---------------------------------------------------------------------------
# Patch: datasets 4.5.0 returns Column objects instead of plain lists.
# The HF tokenizer's isinstance check fails on Column, so convert first.
# ---------------------------------------------------------------------------
_orig_tokenizer_call = SpanMarkerTokenizer.__call__

def _patched_tokenizer_call(self, batch, **kwargs):
    if "tokens" in batch and not isinstance(batch["tokens"], (list, tuple, str)):
        batch = dict(batch)
        batch["tokens"] = list(batch["tokens"])
    return _orig_tokenizer_call(self, batch, **kwargs)

SpanMarkerTokenizer.__call__ = _patched_tokenizer_call

# ---------------------------------------------------------------------------
# Helpers (copied from 02_spanmarker_train.py)
# ---------------------------------------------------------------------------

def subtokens_to_words_int(tokens, ner_tags):
    words, word_tags = [], []
    current_pieces, current_tag = [], None
    for token, tag in zip(tokens, ner_tags):
        if tag == -100:
            continue
        surface = token.lstrip("\u2581")
        if token.startswith("\u2581") or not current_pieces:
            if current_pieces:
                words.append("".join(current_pieces))
                word_tags.append(current_tag)
            current_pieces = [surface]
            current_tag = tag
        else:
            current_pieces.append(surface)
    if current_pieces:
        words.append("".join(current_pieces))
        word_tags.append(current_tag)
    return words, word_tags


def prepare_spanmarker_split(hf_split):
    from datasets import Dataset
    all_tokens, all_tags = [], []
    for example in hf_split:
        words, word_tags = subtokens_to_words_int(example["tokens"], example["ner_tags"])
        all_tokens.append(words)
        all_tags.append(word_tags)
    return Dataset.from_dict({"tokens": all_tokens, "ner_tags": all_tags})


def char_to_word_map(words):
    """Map each character position in ' '.join(words) to its word index."""
    mapping = {}
    pos = 0
    for word_idx, word in enumerate(words):
        for c in range(len(word)):
            mapping[pos + c] = word_idx
        pos += len(word) + 1  # +1 for the space
    return mapping


def add_word_indices(spans, words):
    """Convert char_start/end_index to word_start/end_index in-place."""
    mapping = char_to_word_map(words)
    for span in spans:
        start = mapping.get(span["char_start_index"], 0)
        end   = mapping.get(span["char_end_index"] - 1, len(words) - 1) + 1
        span["word_start_index"] = start
        span["word_end_index"]   = end
    return spans


def word_spans_to_iob(num_words, spans):
    iob_tags = ["O"] * num_words
    for span in sorted(spans, key=lambda s: s["score"], reverse=True):
        start, end, label = span["word_start_index"], span["word_end_index"], span["label"].upper()
        if all(iob_tags[i] == "O" for i in range(start, end)):
            iob_tags[start] = f"B-{label}"
            for i in range(start + 1, end):
                iob_tags[i] = f"I-{label}"
    return iob_tags


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def evaluate():
    assert MODEL_DIR.exists(), f"No saved model found at {MODEL_DIR}. Run 02_spanmarker_train.py first."
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load dataset
    print(f"Loading dataset from {DATASET_DIR} ...")
    raw_ds = load_from_disk(str(DATASET_DIR))
    test_ds = prepare_spanmarker_split(raw_ds["test"])
    val_ds  = prepare_spanmarker_split(raw_ds["validation"])
    print(f"  val={len(val_ds)}  test={len(test_ds)} sentences")

    # 2. Load saved model
    print(f"\nLoading model from {MODEL_DIR} ...")
    model = SpanMarkerModel.from_pretrained(str(MODEL_DIR))
    print("  Done.")

    # 3. Official evaluation via SpanMarker's Trainer
    training_args = TrainingArguments(
        output_dir=str(CKPT_DIR),
        per_device_eval_batch_size=BATCH_SIZE,
        report_to="none",
    )
    trainer = Trainer(model=model, args=training_args)

    print("\nRunning official evaluation on test split ...")
    t_eval = time.time()
    eval_metrics = trainer.evaluate(test_ds)
    eval_elapsed = time.time() - t_eval
    print(f"  Done in {eval_elapsed:.1f}s")

    # 4. Per-example predictions
    print("\nGenerating per-example predictions ...")
    t_inf = time.time()
    all_gold, all_pred, per_example_records = [], [], []

    for example, raw_example in zip(test_ds, raw_ds["test"]):
        words    = list(example["tokens"])
        gold_iob = [ID2IOB[t] for t in example["ner_tags"]]
        spans    = model.predict(words, show_progress_bar=False)
        pred_iob = word_spans_to_iob(len(words), spans)

        all_gold.append(gold_iob)
        all_pred.append(pred_iob)
        per_example_records.append({
            "id":       int(raw_example["id"]),
            "text":     " ".join(words),
            "gold_iob": gold_iob,
            "pred_iob": pred_iob,
            "pred_spans": [
                {
                    "text":             s["span"] if isinstance(s["span"], str) else " ".join(s["span"]),
                    "label":            s["label"],
                    "score":            round(float(s["score"]), 4),
                    "word_start_index": s["word_start_index"],
                    "word_end_index":   s["word_end_index"],
                }
                for s in spans
            ],
        })

    inf_elapsed = time.time() - t_inf

    # 5. Seqeval metrics
    precision  = precision_score(all_gold, all_pred, scheme=IOB2, zero_division=0)
    recall     = recall_score(   all_gold, all_pred, scheme=IOB2, zero_division=0)
    f1         = f1_score(       all_gold, all_pred, scheme=IOB2, zero_division=0)
    report_str = classification_report(all_gold, all_pred, scheme=IOB2, zero_division=0)

    # 6. Save results
    results = {
        "model":             f"{BACKBONE} (SpanMarker fine-tuned)",
        "entity_labels":     ENTITY_LABELS,
        "num_test_examples": len(test_ds),
        "test_results": {
            "inference_time_seconds": round(inf_elapsed, 2),
            "overall": {
                "precision": round(precision, 4),
                "recall":    round(recall, 4),
                "f1":        round(f1, 4),
            },
            "per_entity_trainer": {
                "SKILL": eval_metrics.get("eval_SKILL", {}),
                "TOOL":  eval_metrics.get("eval_TOOL",  {}),
            },
            "classification_report": report_str,
            "per_example":           per_example_records,
        },
    }
    with open(RESULTS_FILE, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print(f"\nResults saved to {RESULTS_FILE}")

    # 7. Print summary
    print("\n" + "=" * 60)
    print("SpanMarker fine-tuned evaluation -- test split summary")
    print("=" * 60)
    print(f"  Model     : {BACKBONE} (SpanMarker)")
    print(f"  Test size : {len(test_ds)} sentences")
    print()
    print(f"  {'Metric':<12}  {'Value':>8}")
    print(f"  {'-'*12}  {'-'*8}")
    print(f"  {'Precision':<12}  {precision:>8.4f}")
    print(f"  {'Recall':<12}  {recall:>8.4f}")
    print(f"  {'F1':<12}  {f1:>8.4f}")
    print()
    print("Per-class breakdown:")
    print(report_str)


if __name__ == "__main__":
    evaluate()

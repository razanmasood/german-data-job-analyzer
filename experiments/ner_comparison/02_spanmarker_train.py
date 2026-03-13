"""
02_spanmarker_train.py
----------------------
Fine-tune a SpanMarker model on the annotated skill/tool NER dataset and
evaluate it on the held-out test split.

Pipeline
--------
1. Load the HuggingFace DatasetDict from data/processed/ner_dataset/.
2. Reconstruct word-level tokens and integer IOB tags from the stored
   SentencePiece sub-word tokens (same logic as 01_gliner_eval.py).
3. Build SpanMarker-compatible Dataset objects with 'tokens' and 'ner_tags'
   columns.
4. Fine-tune SpanMarkerModel (xlm-roberta-large backbone) for up to 5 epochs
   with early stopping on validation overall_f1 (patience=2).
5. Save the best checkpoint to experiments/ner_comparison/models/spanmarker/.
6. Evaluate on the test split; save results to
   experiments/ner_comparison/results/spanmarker_results.json in the same
   structure as gliner_results.json.
7. Print overall precision, recall, F1 and per-entity breakdown to the
   terminal.

SpanMarker dataset contract
---------------------------
The SpanMarker Trainer requires each split to have exactly two columns:
  - 'tokens'   : List[str]  -- word-level surface tokens (not sub-word).
  - 'ner_tags' : List[int]  -- integer IOB tags aligned to each word.

The label list passed to from_pretrained must follow the IOB/IOB2 scheme so
that SpanMarker's LabelNormalizerIOB can convert them to span tuples
internally:
    ['O', 'B-SKILL', 'I-SKILL', 'B-TOOL', 'I-TOOL']

Usage
-----
    python experiments/ner_comparison/02_spanmarker_train.py
"""

import json
import os
import time
from pathlib import Path

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

from datasets import Dataset, load_from_disk
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score
from seqeval.scheme import IOB2
from span_marker import SpanMarkerModel, Trainer
from transformers import EarlyStoppingCallback, TrainingArguments

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT    = Path(__file__).resolve().parents[2]
DATASET_DIR  = REPO_ROOT / "data" / "processed" / "ner_dataset"
RESULTS_DIR  = Path(__file__).resolve().parent / "results"
RESULTS_FILE = RESULTS_DIR / "spanmarker_results.json"
MODEL_DIR    = Path(__file__).resolve().parent / "models" / "spanmarker"
CKPT_DIR     = Path(__file__).resolve().parent / "models" / "spanmarker_checkpoints"

# ---------------------------------------------------------------------------
# Model and label configuration
# ---------------------------------------------------------------------------
BACKBONE = "xlm-roberta-large"

# Full IOB label list -- SpanMarker auto-detects the IOB scheme and collapses
# B-X / I-X pairs to entity type X internally.
IOB_LABELS = ["O", "B-SKILL", "I-SKILL", "B-TOOL", "I-TOOL"]

ENTITY_LABELS = ["SKILL", "TOOL"]

# Integer tag -> string IOB (matches the stored dataset's label_map.json)
ID2IOB = {
    -100: None,    # special / padding tokens -- skipped during reconstruction
    0:    "O",
    1:    "B-SKILL",
    2:    "I-SKILL",
    3:    "B-TOOL",
    4:    "I-TOOL",
}

# Training hyper-parameters
MAX_EPOCHS               = 5
EARLY_STOPPING_PATIENCE  = 2
LEARNING_RATE            = 2e-5
BATCH_SIZE               = 4   # conservative: xlm-roberta-large is memory-heavy on CPU


# ---------------------------------------------------------------------------
# Data reconstruction helpers
# ---------------------------------------------------------------------------

def subtokens_to_words_int(
    tokens: list[str], ner_tags: list[int]
) -> tuple[list[str], list[int]]:
    """Reconstruct word-level surface tokens and integer IOB tags from stored
    SentencePiece sub-word tokens.

    XLM-RoBERTa tokenizes with SentencePiece: a leading U+2581 ('▁') marks
    the start of a new surface word; tokens without it are continuations.
    Special tokens (tag == -100) are skipped entirely.

    The first sub-token of each word determines the word's IOB tag, consistent
    with how the dataset was originally annotated at word boundaries.

    Parameters
    ----------
    tokens:
        Raw sub-word token strings (including '<s>', '</s>' specials).
    ner_tags:
        Integer NER tag per sub-word (-100 for special/padding tokens).

    Returns
    -------
    words:
        Reconstructed surface word strings.
    word_tags:
        Integer IOB tag for each word (values 0-4, matching the label map).
    """
    words:     list[str] = []
    word_tags: list[int] = []

    current_pieces: list[str] = []
    current_tag: int | None = None

    for token, tag in zip(tokens, ner_tags):
        if tag == -100:
            continue

        surface = token.lstrip("\u2581")  # strip the word-boundary marker

        if token.startswith("\u2581") or not current_pieces:
            # Flush the previous word before starting a new one
            if current_pieces:
                words.append("".join(current_pieces))
                word_tags.append(current_tag)
            current_pieces = [surface]
            current_tag = tag      # first sub-token owns the tag
        else:
            # Continuation sub-token -- extend the current word, tag unchanged
            current_pieces.append(surface)

    # Flush the final word
    if current_pieces:
        words.append("".join(current_pieces))
        word_tags.append(current_tag)

    return words, word_tags


def prepare_spanmarker_split(hf_split) -> Dataset:
    """Convert a stored sub-word DatasetDict split to a word-level Dataset
    ready for SpanMarker's Trainer.

    SpanMarker's Trainer.preprocess_dataset() requires exactly the columns
    'tokens' and 'ner_tags'; all others are dropped internally.

    Parameters
    ----------
    hf_split:
        One split of the HuggingFace DatasetDict
        (e.g. ``raw_ds['train']``).

    Returns
    -------
    Dataset with columns 'tokens' (List[str]) and 'ner_tags' (List[int]).
    """
    all_tokens: list[list[str]] = []
    all_tags:   list[list[int]] = []

    for example in hf_split:
        words, word_tags = subtokens_to_words_int(
            example["tokens"], example["ner_tags"]
        )
        all_tokens.append(words)
        all_tags.append(word_tags)

    return Dataset.from_dict({"tokens": all_tokens, "ner_tags": all_tags})


# ---------------------------------------------------------------------------
# Post-training per-example evaluation helpers
# ---------------------------------------------------------------------------

def word_spans_to_iob(num_words: int, spans: list[dict]) -> list[str]:
    """Convert SpanMarker word-index span predictions to word-level IOB2 tags.

    SpanMarker's ``model.predict(word_list)`` returns dicts with keys
    'word_start_index', 'word_end_index' (exclusive), 'label', and 'score'.
    Overlapping spans are resolved by giving precedence to the highest-scoring
    span, matching SpanMarker's own evaluation logic.

    Parameters
    ----------
    num_words:
        Number of words in the sentence.
    spans:
        List of span dicts from ``model.predict(word_list)``.

    Returns
    -------
    List of IOB2 tag strings, one per word.
    """
    iob_tags = ["O"] * num_words

    # Highest-score spans are assigned first; lower-score spans are skipped if
    # they overlap with an already-tagged region.
    for span in sorted(spans, key=lambda s: s["score"], reverse=True):
        start = span["word_start_index"]
        end   = span["word_end_index"]   # exclusive
        label = span["label"].upper()

        if all(iob_tags[i] == "O" for i in range(start, end)):
            iob_tags[start] = f"B-{label}"
            for i in range(start + 1, end):
                iob_tags[i] = f"I-{label}"

    return iob_tags


# ---------------------------------------------------------------------------
# Main training and evaluation function
# ---------------------------------------------------------------------------

def train_and_evaluate() -> None:
    """Fine-tune SpanMarker and evaluate it on the test split."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    CKPT_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Load and reconstruct dataset splits
    # ------------------------------------------------------------------
    print(f"Loading dataset from {DATASET_DIR} ...")
    raw_ds = load_from_disk(str(DATASET_DIR))

    print("  Reconstructing word-level tokens from sub-word tokens ...")
    train_ds = prepare_spanmarker_split(raw_ds["train"])
    val_ds   = prepare_spanmarker_split(raw_ds["validation"])
    test_ds  = prepare_spanmarker_split(raw_ds["test"])

    print(
        f"  train={len(train_ds)}  val={len(val_ds)}  test={len(test_ds)} sentences"
    )

    # ------------------------------------------------------------------
    # 2. Initialise SpanMarker model from the xlm-roberta-large backbone
    # ------------------------------------------------------------------
    print(f"\nInitialising SpanMarker with backbone '{BACKBONE}' ...")
    model = SpanMarkerModel.from_pretrained(BACKBONE, labels=IOB_LABELS)
    print("  Model initialised.")

    # ------------------------------------------------------------------
    # 3. Training arguments
    # ------------------------------------------------------------------
    training_args = TrainingArguments(
        output_dir=str(CKPT_DIR),
        num_train_epochs=MAX_EPOCHS,
        learning_rate=LEARNING_RATE,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        # Evaluate and checkpoint at the end of every epoch so that
        # EarlyStoppingCallback can compare consecutive validation F1 scores.
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,         # keep only the two most recent checkpoints
        # Reload the best checkpoint (highest eval_overall_f1) after training.
        load_best_model_at_end=True,
        metric_for_best_model="eval_overall_f1",
        greater_is_better=True,
        logging_strategy="epoch",   # one log line per epoch, not per step
        report_to="none",
    )

    # ------------------------------------------------------------------
    # 4. Train with early stopping on validation overall_f1
    # ------------------------------------------------------------------
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        callbacks=[
            EarlyStoppingCallback(
                early_stopping_patience=EARLY_STOPPING_PATIENCE
            )
        ],
    )

    print(
        f"\nTraining for up to {MAX_EPOCHS} epochs "
        f"(early stopping patience={EARLY_STOPPING_PATIENCE}) ..."
    )
    t_train = time.time()
    trainer.train()
    train_elapsed = time.time() - t_train
    print(f"  Training complete in {train_elapsed:.1f}s")

    # ------------------------------------------------------------------
    # 5. Save the best model to the designated output directory
    # ------------------------------------------------------------------
    model.save_pretrained(str(MODEL_DIR))
    print(f"\nBest model saved to {MODEL_DIR}")

    # ------------------------------------------------------------------
    # 6. Official test-set evaluation via SpanMarker's internal pipeline
    #    Returns overall_f1, per-entity F1s etc. (prefixed with 'eval_').
    # ------------------------------------------------------------------
    print("\nRunning official evaluation on test split ...")
    t_eval = time.time()
    eval_metrics = trainer.evaluate(test_ds)
    eval_elapsed = time.time() - t_eval
    print(f"  Done in {eval_elapsed:.1f}s")

    # ------------------------------------------------------------------
    # 7. Per-example predictions for the JSON report
    #    model.predict() runs on one word list at a time and returns span
    #    dicts with word_start_index, word_end_index, label, and score.
    # ------------------------------------------------------------------
    print("\nGenerating per-example predictions for results file ...")
    t_inf = time.time()

    all_gold: list[list[str]] = []
    all_pred: list[list[str]] = []
    per_example_records: list[dict] = []

    for example, raw_example in zip(test_ds, raw_ds["test"]):
        words    = example["tokens"]
        gold_iob = [ID2IOB[t] for t in example["ner_tags"]]

        # predict() accepts a batch of pretokenized sentences (List[List[str]])
        spans    = model.predict([words], show_progress_bar=False)[0]
        pred_iob = word_spans_to_iob(len(words), spans)

        all_gold.append(gold_iob)
        all_pred.append(pred_iob)

        # Normalise span text: predict() returns a list of word strings when
        # given a word-list input; join them for the JSON record.
        per_example_records.append(
            {
                "id":       int(raw_example["id"]),
                "text":     " ".join(words),
                "gold_iob": gold_iob,
                "pred_iob": pred_iob,
                "pred_spans": [
                    {
                        "text":             (
                            " ".join(s["span"])
                            if isinstance(s["span"], list)
                            else s["span"]
                        ),
                        "label":            s["label"],
                        "score":            round(float(s["score"]), 4),
                        "word_start_index": s["word_start_index"],
                        "word_end_index":   s["word_end_index"],
                    }
                    for s in spans
                ],
            }
        )

    inf_elapsed = time.time() - t_inf

    # ------------------------------------------------------------------
    # 8. Compute seqeval metrics from the per-example IOB sequences.
    #    This mirrors the GLiNER evaluation approach for a fair comparison.
    # ------------------------------------------------------------------
    precision  = precision_score(all_gold, all_pred, scheme=IOB2, zero_division=0)
    recall     = recall_score(   all_gold, all_pred, scheme=IOB2, zero_division=0)
    f1         = f1_score(       all_gold, all_pred, scheme=IOB2, zero_division=0)
    report_str = classification_report(all_gold, all_pred, scheme=IOB2, zero_division=0)

    # ------------------------------------------------------------------
    # 9. Assemble and save JSON results
    # ------------------------------------------------------------------
    # Pull per-entity metrics from the SpanMarker trainer's eval output.
    skill_metrics = eval_metrics.get("eval_SKILL", {})
    tool_metrics  = eval_metrics.get("eval_TOOL",  {})

    results = {
        "model":             f"{BACKBONE} (SpanMarker fine-tuned)",
        "entity_labels":     ENTITY_LABELS,
        "num_test_examples": len(test_ds),
        "training": {
            "backbone":                BACKBONE,
            "train_sentences":         len(train_ds),
            "val_sentences":           len(val_ds),
            "max_epochs":              MAX_EPOCHS,
            "early_stopping_patience": EARLY_STOPPING_PATIENCE,
            "learning_rate":           LEARNING_RATE,
            "train_time_seconds":      round(train_elapsed, 2),
        },
        "test_results": {
            "inference_time_seconds": round(inf_elapsed, 2),
            "overall": {
                "precision": round(precision, 4),
                "recall":    round(recall, 4),
                "f1":        round(f1, 4),
            },
            # Per-entity metrics as reported by SpanMarker's internal evaluator
            # (these may differ slightly from seqeval above due to span
            # reconstruction differences; both are included for transparency).
            "per_entity_trainer": {
                "SKILL": skill_metrics,
                "TOOL":  tool_metrics,
            },
            "classification_report": report_str,
            "per_example":           per_example_records,
        },
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)

    print(f"\nResults saved to {RESULTS_FILE}")

    # ------------------------------------------------------------------
    # 10. Print terminal summary
    # ------------------------------------------------------------------
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
    train_and_evaluate()

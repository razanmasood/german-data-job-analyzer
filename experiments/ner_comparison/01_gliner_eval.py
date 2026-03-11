"""
01_gliner_eval.py
-----------------
Zero-shot evaluation of GLiNER (urchade/gliner_multi-v2.1) on the NER test split
that was used for xlm-roberta fine-tuning.

The model is run twice on the same test set — once with GLiNER's default
confidence threshold and once with threshold=0.3 — so that the effect of
lowering the acceptance threshold (higher recall at the cost of precision)
can be measured directly.

Pipeline
--------
1. Load the HuggingFace DatasetDict from data/processed/ner_dataset/
2. For every test sentence, reconstruct word-level tokens and gold IOB tags
   from the stored SentencePiece sub-word tokens.
3. Run GLiNER inference twice per sentence:
      a. default threshold (GLiNER default: 0.5)
      b. threshold=0.3
4. Convert GLiNER's character-span output back to word-level IOB tags so that
   predictions and gold labels share the same representation.
5. Compute precision, recall and F1 with seqeval for each threshold.
6. Save a detailed JSON report to experiments/ner_comparison/results/gliner_results.json
   under two top-level keys ("default_threshold" and "threshold_0.3") and
   print a side-by-side summary.

Usage
-----
    python experiments/ner_comparison/01_gliner_eval.py
"""

import io
import json
import time
from pathlib import Path

from datasets import load_from_disk
from gliner import GLiNER
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score
from seqeval.scheme import IOB2

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = REPO_ROOT / "data" / "processed" / "ner_dataset"
RESULTS_DIR      = Path(__file__).resolve().parent / "results"
RESULTS_FILE     = RESULTS_DIR / "gliner_results.json"
DIAGNOSTIC_FILE  = RESULTS_DIR / "gliner_diagnostic.txt"

# GLiNER model hub identifier
MODEL_NAME = "urchade/gliner_multi-v2.1"

# Entity labels to pass to GLiNER – must match the classes in the gold dataset
ENTITY_LABELS = ["SKILL", "TOOL"]

# Integer tag → IOB string (from label_map.json)
ID2LABEL = {
    -100: None,       # special/padding tokens – ignored
    0: "O",
    1: "B-SKILL",
    2: "I-SKILL",
    3: "B-TOOL",
    4: "I-TOOL",
}


# ---------------------------------------------------------------------------
# Token reconstruction helpers
# ---------------------------------------------------------------------------

def subtokens_to_words(tokens: list[str], ner_tags: list[int]) -> tuple[list[str], list[str]]:
    """Reconstruct word-level tokens and IOB labels from SentencePiece sub-words.

    XLM-RoBERTa encodes text with SentencePiece. A leading '▁' (U+2581)
    marks the start of a new surface word; tokens without '▁' are
    continuations of the preceding word. Special tokens (ner_tags == -100)
    are skipped.

    Parameters
    ----------
    tokens:
        Raw sub-word token strings from the dataset (including special tokens
        such as '<s>' and '</s>').
    ner_tags:
        Integer NER tag for each sub-word (-100 for special/padding tokens).

    Returns
    -------
    words:
        Reconstructed surface words (one entry per word boundary).
    word_labels:
        IOB label string for each word.  The label is taken from the *first*
        sub-token of each word, which always carries the B-/I-/O tag.
    """
    words: list[str] = []
    word_labels: list[str] = []

    current_word_pieces: list[str] = []
    current_label: str | None = None

    for token, tag in zip(tokens, ner_tags):
        # Skip special tokens (CLS, SEP, padding)
        if tag == -100:
            continue

        # Strip the leading space marker to get the surface form
        surface = token.lstrip("\u2581")

        if token.startswith("\u2581") or not current_word_pieces:
            # Flush previous word if one exists
            if current_word_pieces:
                words.append("".join(current_word_pieces))
                word_labels.append(current_label)

            # Start a new word
            current_word_pieces = [surface]
            current_label = ID2LABEL[tag]
        else:
            # Continuation sub-token – append to the current word
            current_word_pieces.append(surface)
            # Do NOT update current_label: the first sub-token owns the tag

    # Flush the last word
    if current_word_pieces:
        words.append("".join(current_word_pieces))
        word_labels.append(current_label)

    return words, word_labels


def words_to_char_offsets(words: list[str]) -> list[tuple[int, int]]:
    """Build character-level [start, end) offsets for each word in the
    space-joined text that will be passed to GLiNER.

    Parameters
    ----------
    words:
        List of surface words.

    Returns
    -------
    offsets:
        List of (start, end) character index pairs.  ``end`` is exclusive.
    """
    offsets: list[tuple[int, int]] = []
    pos = 0
    for word in words:
        start = pos
        end = pos + len(word)
        offsets.append((start, end))
        pos = end + 1  # +1 for the space separator
    return offsets


# ---------------------------------------------------------------------------
# Span → IOB conversion
# ---------------------------------------------------------------------------

def spans_to_iob(
    word_offsets: list[tuple[int, int]],
    gliner_spans: list[dict],
) -> list[str]:
    """Convert GLiNER character-level spans to word-level IOB2 tags.

    GLiNER returns a list of dicts with keys 'start', 'end', and 'label'.
    This function maps each predicted span back to the words it covers and
    assigns B-/I- prefixed IOB tags.  Words not covered by any span receive
    'O'.

    Overlapping spans are resolved by giving precedence to the *first* span
    that covers a given word (i.e., the one with the lower start offset).

    Parameters
    ----------
    word_offsets:
        Character [start, end) offsets for every word (from
        ``words_to_char_offsets``).
    gliner_spans:
        Predicted entity spans from GLiNER, each a dict with at least
        'start' (int), 'end' (int), and 'label' (str).

    Returns
    -------
    iob_tags:
        One IOB2 tag string per word.
    """
    # Initialise all words as outside any entity
    iob_tags = ["O"] * len(word_offsets)

    # Sort spans by start position so earlier spans win on overlap
    sorted_spans = sorted(gliner_spans, key=lambda s: s["start"])

    for span in sorted_spans:
        span_start = span["start"]
        span_end = span["end"]
        label = span["label"].upper()

        first_in_span = True
        for idx, (w_start, w_end) in enumerate(word_offsets):
            # Check whether the word and span overlap
            if w_start < span_end and w_end > span_start:
                # Only tag the word if it has not already been claimed
                if iob_tags[idx] == "O":
                    iob_tags[idx] = f"B-{label}" if first_in_span else f"I-{label}"
                    first_in_span = False

    return iob_tags


# ---------------------------------------------------------------------------
# Inference helper
# ---------------------------------------------------------------------------

def _run_inference(
    model: GLiNER,
    test_ds,
    threshold: float | None = None,
) -> tuple[list[list[str]], list[list[str]], list[dict], float]:
    """Run GLiNER inference over every example in *test_ds*.

    Parameters
    ----------
    model:
        A loaded GLiNER model instance.
    test_ds:
        HuggingFace Dataset split with 'tokens', 'ner_tags', and 'id' columns.
    threshold:
        Confidence threshold forwarded to ``model.predict_entities``.  Pass
        ``None`` to use GLiNER's built-in default (0.5).

    Returns
    -------
    all_gold:
        Gold IOB tag sequences, one list per example.
    all_pred:
        Predicted IOB tag sequences, one list per example.
    per_example_records:
        List of dicts containing text, gold/pred IOB tags, and raw GLiNER spans
        (for inclusion in the JSON report).
    elapsed:
        Wall-clock seconds taken for the inference loop.
    """
    all_gold: list[list[str]] = []
    all_pred: list[list[str]] = []
    per_example_records: list[dict] = []

    t_inf = time.time()

    for example in test_ds:
        # Reconstruct word-level tokens and gold labels from sub-word tokens
        words, gold_iob = subtokens_to_words(example["tokens"], example["ner_tags"])

        # Build the plain-text sentence GLiNER will see
        text = " ".join(words)

        # Character offsets for each word so we can convert spans -> IOB later
        word_offsets = words_to_char_offsets(words)

        # Run GLiNER zero-shot inference; pass threshold only when specified
        kwargs = {} if threshold is None else {"threshold": threshold}
        spans = model.predict_entities(text, ENTITY_LABELS, **kwargs)

        # Convert character spans -> word-level IOB tags
        pred_iob = spans_to_iob(word_offsets, spans)

        all_gold.append(gold_iob)
        all_pred.append(pred_iob)

        per_example_records.append(
            {
                "id": int(example["id"]),
                "text": text,
                "gold_iob": gold_iob,
                "pred_iob": pred_iob,
                "gliner_spans": [
                    {
                        "text": s["text"],
                        "label": s["label"],
                        "score": round(float(s["score"]), 4),
                        "start": s["start"],
                        "end": s["end"],
                    }
                    for s in spans
                ],
            }
        )

    elapsed = time.time() - t_inf
    return all_gold, all_pred, per_example_records, elapsed


def _compute_metrics(all_gold: list[list[str]], all_pred: list[list[str]]) -> dict:
    """Compute seqeval precision, recall, F1, and classification report.

    Parameters
    ----------
    all_gold:
        Gold IOB tag sequences.
    all_pred:
        Predicted IOB tag sequences.

    Returns
    -------
    dict with keys 'precision', 'recall', 'f1', and 'classification_report'.
    """
    return {
        "precision":             round(precision_score(all_gold, all_pred, scheme=IOB2, zero_division=0), 4),
        "recall":                round(recall_score(   all_gold, all_pred, scheme=IOB2, zero_division=0), 4),
        "f1":                    round(f1_score(       all_gold, all_pred, scheme=IOB2, zero_division=0), 4),
        "classification_report": classification_report(all_gold, all_pred, scheme=IOB2, zero_division=0),
    }


# ---------------------------------------------------------------------------
# Diagnostic helper
# ---------------------------------------------------------------------------

def _run_diagnostic(model: GLiNER, test_ds, n: int = 3) -> None:
    """Inspect the first *n* test examples and write a human-readable report.

    For each example the report shows three sections:

    1. **Plain text** — the space-joined word string that is passed to GLiNER.
    2. **Token / gold-tag table** — every reconstructed word aligned with its
       gold IOB label, making it easy to spot annotation boundaries.
    3. **GLiNER predicted spans** — each span returned by the model at the
       default threshold, with its confidence score.

    The report is printed to the terminal and also saved to
    ``DIAGNOSTIC_FILE`` so it can be reviewed offline.

    Parameters
    ----------
    model:
        A loaded GLiNER model instance (default threshold used for spans).
    test_ds:
        HuggingFace Dataset split to sample from.
    n:
        Number of examples to include (default: 3).
    """
    buf = io.StringIO()

    def emit(line: str = "") -> None:
        """Write *line* to both stdout and the string buffer."""
        print(line)
        buf.write(line + "\n")

    header = f"GLiNER diagnostic — first {n} test examples (default threshold)"
    emit("=" * len(header))
    emit(header)
    emit("=" * len(header))

    for i, example in enumerate(test_ds):
        if i >= n:
            break

        # Reconstruct words and gold labels from SentencePiece sub-tokens
        words, gold_iob = subtokens_to_words(example["tokens"], example["ner_tags"])
        text = " ".join(words)
        word_offsets = words_to_char_offsets(words)

        # Run GLiNER with default threshold to get predicted spans
        spans = model.predict_entities(text, ENTITY_LABELS)

        emit(f"\n{'─' * 60}")
        emit(f"Example {i + 1}  (dataset id={example['id']})")
        emit(f"{'─' * 60}")

        # ------------------------------------------------------------------
        # Section 1: plain text
        # ------------------------------------------------------------------
        emit("\n[1] Plain text passed to GLiNER:")
        # Wrap long lines at ~80 chars on word boundaries for readability
        words_wrapped, line_buf, line_len = [], [], 0
        for word in text.split():
            if line_len + len(word) + 1 > 80 and line_buf:
                words_wrapped.append(" ".join(line_buf))
                line_buf, line_len = [], 0
            line_buf.append(word)
            line_len += len(word) + 1
        if line_buf:
            words_wrapped.append(" ".join(line_buf))
        for wrapped_line in words_wrapped:
            emit(f"    {wrapped_line}")

        # ------------------------------------------------------------------
        # Section 2: word / gold-tag alignment table
        # ------------------------------------------------------------------
        emit("\n[2] Reconstructed words with gold IOB tags:")
        col_w = max(len(w) for w in words) + 2  # column width for word column
        emit(f"    {'WORD':<{col_w}}  GOLD TAG")
        emit(f"    {'-' * col_w}  --------")
        for word, tag in zip(words, gold_iob):
            # Highlight non-O tags with a marker so they stand out
            marker = "  <--" if tag != "O" else ""
            emit(f"    {word:<{col_w}}  {tag}{marker}")

        # ------------------------------------------------------------------
        # Section 3: GLiNER predicted spans
        # ------------------------------------------------------------------
        emit("\n[3] GLiNER predicted spans (default threshold):")
        if spans:
            emit(f"    {'SPAN TEXT':<35}  {'LABEL':<8}  SCORE")
            emit(f"    {'-' * 35}  {'-' * 8}  -----")
            for span in spans:
                emit(
                    f"    {span['text']:<35}  {span['label']:<8}  {span['score']:.4f}"
                )
        else:
            emit("    (no spans predicted)")

    emit(f"\n{'=' * len(header)}")
    emit(f"End of diagnostic  ({n} examples shown)")
    emit("=" * len(header))

    # Save to file
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    DIAGNOSTIC_FILE.write_text(buf.getvalue(), encoding="utf-8")
    print(f"\nDiagnostic saved to {DIAGNOSTIC_FILE}")


# ---------------------------------------------------------------------------
# Main evaluation loop
# ---------------------------------------------------------------------------

def evaluate() -> None:
    """Run GLiNER zero-shot evaluation on the test split at two thresholds.

    Inference is performed twice — once with GLiNER's default confidence
    threshold (0.5) and once with threshold=0.3.  Metrics and per-example
    predictions for both runs are saved to a single JSON file under the keys
    "default_threshold" and "threshold_0.3".
    """

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Load dataset
    # ------------------------------------------------------------------
    print(f"Loading dataset from {DATASET_DIR} ...")
    dataset = load_from_disk(str(DATASET_DIR))
    test_ds = dataset["test"]
    print(f"  Test examples: {len(test_ds)}")

    # ------------------------------------------------------------------
    # 2. Load GLiNER model (once; reused for both threshold runs)
    # ------------------------------------------------------------------
    print(f"\nLoading GLiNER model '{MODEL_NAME}' ...")
    t0 = time.time()
    model = GLiNER.from_pretrained(MODEL_NAME)
    print(f"  Model loaded in {time.time() - t0:.1f}s")

    # ------------------------------------------------------------------
    # 2b. Diagnostic — inspect first 3 examples before full evaluation
    # ------------------------------------------------------------------
    print("\n--- Diagnostic (first 3 examples) ---")
    _run_diagnostic(model, test_ds, n=3)
    print("--- End diagnostic ---")

    # ------------------------------------------------------------------
    # 3a. Inference — default threshold
    # ------------------------------------------------------------------
    print(f"\n[1/2] Running inference with default threshold ...")
    gold_def, pred_def, records_def, elapsed_def = _run_inference(model, test_ds, threshold=None)
    print(f"  Done in {elapsed_def:.1f}s ({elapsed_def / len(test_ds):.2f}s per example)")

    # ------------------------------------------------------------------
    # 3b. Inference — threshold=0.3
    # ------------------------------------------------------------------
    print(f"\n[2/2] Running inference with threshold=0.3 ...")
    gold_03, pred_03, records_03, elapsed_03 = _run_inference(model, test_ds, threshold=0.3)
    print(f"  Done in {elapsed_03:.1f}s ({elapsed_03 / len(test_ds):.2f}s per example)")

    # ------------------------------------------------------------------
    # 4. Compute metrics with seqeval (strict IOB2) for each run
    # ------------------------------------------------------------------
    metrics_def = _compute_metrics(gold_def, pred_def)
    metrics_03  = _compute_metrics(gold_03,  pred_03)

    # ------------------------------------------------------------------
    # 5. Assemble and save JSON results
    # ------------------------------------------------------------------
    results = {
        "model":             MODEL_NAME,
        "entity_labels":     ENTITY_LABELS,
        "num_test_examples": len(test_ds),
        "default_threshold": {
            "threshold":              "default (0.5)",
            "inference_time_seconds": round(elapsed_def, 2),
            "overall":                {k: v for k, v in metrics_def.items() if k != "classification_report"},
            "classification_report":  metrics_def["classification_report"],
            "per_example":            records_def,
        },
        "threshold_0.3": {
            "threshold":              0.3,
            "inference_time_seconds": round(elapsed_03, 2),
            "overall":                {k: v for k, v in metrics_03.items() if k != "classification_report"},
            "classification_report":  metrics_03["classification_report"],
            "per_example":            records_03,
        },
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)

    print(f"\nResults saved to {RESULTS_FILE}")

    # ------------------------------------------------------------------
    # 6. Print terminal summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("GLiNER zero-shot evaluation -- test split summary")
    print("=" * 60)
    print(f"  Model     : {MODEL_NAME}")
    print(f"  Test size : {len(test_ds)} sentences")
    print()
    print(f"  {'Threshold':<22}  {'Precision':>9}  {'Recall':>9}  {'F1':>9}")
    print(f"  {'-'*22}  {'-'*9}  {'-'*9}  {'-'*9}")
    print(f"  {'default (0.5)':<22}  {metrics_def['precision']:>9.4f}  {metrics_def['recall']:>9.4f}  {metrics_def['f1']:>9.4f}")
    print(f"  {'0.3':<22}  {metrics_03['precision']:>9.4f}  {metrics_03['recall']:>9.4f}  {metrics_03['f1']:>9.4f}")
    print()
    print("-- default threshold -- per-class breakdown:")
    print(metrics_def["classification_report"])
    print("-- threshold=0.3 -- per-class breakdown:")
    print(metrics_03["classification_report"])


if __name__ == "__main__":
    evaluate()

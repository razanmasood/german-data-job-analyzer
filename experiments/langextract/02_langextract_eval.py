"""
02_langextract_eval.py
----------------------
Evaluation of LangExtract (gemini-2.5-flash-lite) on the NER test split
that was used for xlm-roberta fine-tuning.

Pipeline
--------
1. Load the HuggingFace DatasetDict from data/processed/ner_dataset/
2. For every test sentence, reconstruct word-level tokens and gold IOB tags
   from the stored SentencePiece sub-word tokens.
3. Build the space-joined text string and run LangExtract inference.
4. Convert LangExtract's character-grounded extractions back to word-level IOB
   tags so predictions and gold labels share the same representation.
   Falls back to fuzzy text search when source grounding is unavailable.
5. Compute precision, recall, and F1 with seqeval for SKILL, TOOL, and overall.
6. Save a detailed JSON report to experiments/langextract/results/langextract_eval_results.json
   and print a results table.

Usage
-----
    python experiments/langextract/02_langextract_eval.py

Requires LANGEXTRACT_API_KEY in .env at the repository root.
"""

import json
import os
import textwrap
import time
from pathlib import Path

import langextract as lx
from datasets import load_from_disk
from dotenv import load_dotenv
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score
from seqeval.scheme import IOB2

# ---------------------------------------------------------------------------
# Paths and configuration
# ---------------------------------------------------------------------------

REPO_ROOT    = Path(__file__).resolve().parents[2]
DATASET_DIR  = REPO_ROOT / "data" / "processed" / "ner_dataset"
RESULTS_DIR  = Path(__file__).resolve().parent / "results"
RESULTS_FILE = RESULTS_DIR / "langextract_eval_results.json"

LANGEXTRACT_MODEL  = "gemini-2.5-flash-lite"
ENTITY_LABELS      = ["SKILL", "TOOL"]
SLEEP_BETWEEN_JOBS = 2  # seconds — avoids hitting Gemini rate limits

# Integer tag → IOB string  (matches label_map.json produced by 09_convert_to_iob.py)
ID2LABEL = {
    -100: None,   # special / padding tokens — ignored
    0:    "O",
    1:    "B-SKILL",
    2:    "I-SKILL",
    3:    "B-TOOL",
    4:    "I-TOOL",
}

# ---------------------------------------------------------------------------
# Prompt and few-shot examples  (same as langextract_explore.ipynb)
# ---------------------------------------------------------------------------

PROMPT = textwrap.dedent("""
    Extract SKILL and TOOL entities from job posting requirements sections.

    SKILL: A technical competency, methodology, or domain knowledge.
    Examples: machine learning, NLP, deep learning, statistical modeling, MLOps, data engineering, CI/CD

    TOOL: A specific technology, programming language, framework, platform, or library.
    Examples: Python, PyTorch, TensorFlow, Docker, AWS, SQL, Kubernetes, scikit-learn

    Rules:
    - Use EXACT text from the source. Do not translate or paraphrase.
    - Do not extract soft skills (teamwork, communication).
    - Do not extract job titles or degree names.
    - Works in both German and English.
""")

EXAMPLES = [
    lx.data.ExampleData(
        text="Experience with Python and machine learning. Familiarity with Docker and AWS.",
        extractions=[
            lx.data.Extraction(extraction_class="TOOL",  extraction_text="Python"),
            lx.data.Extraction(extraction_class="SKILL", extraction_text="machine learning"),
            lx.data.Extraction(extraction_class="TOOL",  extraction_text="Docker"),
            lx.data.Extraction(extraction_class="TOOL",  extraction_text="AWS"),
        ],
    ),
    lx.data.ExampleData(
        text="Kenntnisse in Deep Learning und Datenanalyse. Erfahrung mit PyTorch und Kubernetes.",
        extractions=[
            lx.data.Extraction(extraction_class="SKILL", extraction_text="Deep Learning"),
            lx.data.Extraction(extraction_class="SKILL", extraction_text="Datenanalyse"),
            lx.data.Extraction(extraction_class="TOOL",  extraction_text="PyTorch"),
            lx.data.Extraction(extraction_class="TOOL",  extraction_text="Kubernetes"),
        ],
    ),
]

# ---------------------------------------------------------------------------
# Token reconstruction helpers
# (same logic as experiments/ner_comparison/01_gliner_eval.py)
# ---------------------------------------------------------------------------

def subtokens_to_words(tokens: list[str], ner_tags: list[int]) -> tuple[list[str], list[str]]:
    """Reconstruct word-level tokens and IOB labels from SentencePiece sub-words.

    XLM-RoBERTa uses SentencePiece. A leading '▁' (U+2581) marks the start of
    a new surface word; tokens without '▁' are continuations. Special tokens
    (ner_tags == -100) are skipped. The label of the first sub-token of each
    word is used as the word-level label.
    """
    words: list[str] = []
    word_labels: list[str] = []

    current_pieces: list[str] = []
    current_label: str | None = None

    for token, tag in zip(tokens, ner_tags):
        if tag == -100:
            continue

        surface = token.lstrip("\u2581")

        if token.startswith("\u2581") or not current_pieces:
            if current_pieces:
                words.append("".join(current_pieces))
                word_labels.append(current_label)
            current_pieces = [surface]
            current_label = ID2LABEL[tag]
        else:
            current_pieces.append(surface)

    if current_pieces:
        words.append("".join(current_pieces))
        word_labels.append(current_label)

    return words, word_labels


def words_to_char_offsets(words: list[str]) -> list[tuple[int, int]]:
    """Build character-level [start, end) offsets for each word in the
    space-joined text that will be passed to LangExtract.
    """
    offsets: list[tuple[int, int]] = []
    pos = 0
    for word in words:
        offsets.append((pos, pos + len(word)))
        pos += len(word) + 1  # +1 for the space separator
    return offsets


# ---------------------------------------------------------------------------
# Extraction → IOB conversion
# ---------------------------------------------------------------------------

def langextract_to_iob(
    word_offsets: list[tuple[int, int]],
    extractions: list,
    text: str,
) -> list[str]:
    """Convert LangExtract extractions to word-level IOB2 tags.

    Uses character offsets from LangExtract's source grounding when available.
    Falls back to case-insensitive substring search when grounding is absent.

    Overlapping extractions: the first extraction (by char_start) that covers
    a word wins.
    """
    iob_tags = ["O"] * len(word_offsets)

    # Sort by start position so earlier spans win on overlap
    def sort_key(e):
        start = getattr(e, "char_start", None)
        return start if start is not None else len(text)

    for e in sorted(extractions, key=sort_key):
        label = e.extraction_class.upper()
        if label not in ("SKILL", "TOOL"):
            continue

        char_start = getattr(e, "char_start", None)
        char_end   = getattr(e, "char_end",   None)

        if char_start is None:
            # Fallback: find the extraction text in the space-joined string
            needle = e.extraction_text.lower()
            pos = text.lower().find(needle)
            if pos == -1:
                continue
            char_start = pos
            char_end   = pos + len(e.extraction_text)

        first_in_span = True
        for i, (w_start, w_end) in enumerate(word_offsets):
            if w_start < char_end and w_end > char_start:
                if iob_tags[i] == "O":
                    iob_tags[i] = f"B-{label}" if first_in_span else f"I-{label}"
                    first_in_span = False

    return iob_tags


# ---------------------------------------------------------------------------
# Inference loop
# ---------------------------------------------------------------------------

def run_inference(
    test_ds,
) -> tuple[list[list[str]], list[list[str]], list[dict], float]:
    """Run LangExtract on every example in *test_ds*.

    Returns
    -------
    all_gold:
        Gold IOB tag sequences, one list per example.
    all_pred:
        Predicted IOB tag sequences, one list per example.
    per_example_records:
        List of dicts for inclusion in the JSON report.
    elapsed:
        Wall-clock seconds for the inference loop.
    """
    all_gold: list[list[str]] = []
    all_pred: list[list[str]] = []
    per_example_records: list[dict] = []

    n = len(test_ds)
    t_start = time.time()

    for i, example in enumerate(test_ds):
        print(f"  [{i + 1}/{n}] id={example['id']}", end=" ", flush=True)

        words, gold_iob = subtokens_to_words(example["tokens"], example["ner_tags"])
        text = " ".join(words)
        word_offsets = words_to_char_offsets(words)

        extractions = []
        for attempt in range(3):
            try:
                result = lx.extract(
                    text_or_documents=text,
                    prompt_description=PROMPT,
                    examples=EXAMPLES,
                    model_id=LANGEXTRACT_MODEL,
                    fence_output=True,
                    use_schema_constraints=True,
                )
                extractions = result.extractions
                print(f"→ {len(extractions)} entities")
                break
            except Exception as exc:
                if "503" in str(exc) and attempt < 2:
                    print(f"→ 503, retrying in 10s (attempt {attempt + 1}/3)...", end=" ", flush=True)
                    time.sleep(10)
                else:
                    print(f"→ ERROR: {exc}")
                    break

        pred_iob = langextract_to_iob(word_offsets, extractions, text)

        all_gold.append(gold_iob)
        all_pred.append(pred_iob)

        per_example_records.append(
            {
                "id": int(example["id"]),
                "text": text,
                "gold_iob": gold_iob,
                "pred_iob": pred_iob,
                "langextract_extractions": [
                    {
                        "text":       e.extraction_text,
                        "label":      e.extraction_class,
                        "char_start": getattr(e, "char_start", None),
                        "char_end":   getattr(e, "char_end",   None),
                    }
                    for e in extractions
                ],
            }
        )

        # Rate-limit: sleep between all jobs except the last
        if i < n - 1:
            time.sleep(SLEEP_BETWEEN_JOBS)

    elapsed = time.time() - t_start
    return all_gold, all_pred, per_example_records, elapsed


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def compute_metrics(
    all_gold: list[list[str]],
    all_pred: list[list[str]],
) -> dict:
    """Compute seqeval precision, recall, F1, and per-class breakdown."""
    return {
        "precision":             round(precision_score(all_gold, all_pred, scheme=IOB2, zero_division=0), 4),
        "recall":                round(recall_score(   all_gold, all_pred, scheme=IOB2, zero_division=0), 4),
        "f1":                    round(f1_score(       all_gold, all_pred, scheme=IOB2, zero_division=0), 4),
        "classification_report": classification_report(all_gold, all_pred, scheme=IOB2, zero_division=0),
        "classification_report_dict": classification_report(
            all_gold, all_pred, scheme=IOB2, zero_division=0, output_dict=True
        ),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def evaluate() -> None:
    """Run LangExtract evaluation on the NER test split."""

    # ------------------------------------------------------------------
    # 0. Load API key from .env
    # ------------------------------------------------------------------
    load_dotenv(REPO_ROOT / ".env")
    api_key = os.environ.get("LANGEXTRACT_API_KEY")
    if not api_key:
        raise EnvironmentError("LANGEXTRACT_API_KEY not found in .env")
    # LangExtract's Gemini provider reads GOOGLE_API_KEY
    os.environ["GOOGLE_API_KEY"] = api_key

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Load dataset
    # ------------------------------------------------------------------
    print(f"Loading dataset from {DATASET_DIR} ...")
    dataset = load_from_disk(str(DATASET_DIR))
    test_ds = dataset["test"]
    print(f"  Test examples: {len(test_ds)}")
    print(f"  Model:         {LANGEXTRACT_MODEL}")
    print(f"  Sleep between jobs: {SLEEP_BETWEEN_JOBS}s")
    print()

    # ------------------------------------------------------------------
    # 2. Run inference
    # ------------------------------------------------------------------
    print("Running inference...")
    all_gold, all_pred, records, elapsed = run_inference(test_ds)
    print(f"\nDone in {elapsed:.1f}s ({elapsed / len(test_ds):.1f}s per example)")

    # ------------------------------------------------------------------
    # 3. Compute metrics
    # ------------------------------------------------------------------
    metrics = compute_metrics(all_gold, all_pred)
    report_dict = metrics.pop("classification_report_dict")

    # ------------------------------------------------------------------
    # 4. Save JSON results
    # ------------------------------------------------------------------
    results = {
        "model":                  LANGEXTRACT_MODEL,
        "entity_labels":          ENTITY_LABELS,
        "num_test_examples":      len(test_ds),
        "inference_time_seconds": round(elapsed, 2),
        "overall":                {k: v for k, v in metrics.items() if k != "classification_report"},
        "classification_report":  metrics["classification_report"],
        "per_example":            records,
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print(f"\nResults saved to {RESULTS_FILE}")

    # ------------------------------------------------------------------
    # 5. Print results table
    # ------------------------------------------------------------------
    print()
    print("=" * 60)
    print("LangExtract evaluation — test split summary")
    print("=" * 60)
    print(f"  Model     : {LANGEXTRACT_MODEL}")
    print(f"  Test size : {len(test_ds)} sentences")
    print(f"  Elapsed   : {elapsed:.1f}s  ({elapsed / len(test_ds):.1f}s/example)")
    print()
    print(f"  {'Entity type':<14}  {'Precision':>9}  {'Recall':>9}  {'F1':>9}  {'Support':>8}")
    print(f"  {'-'*14}  {'-'*9}  {'-'*9}  {'-'*9}  {'-'*8}")

    for label in ENTITY_LABELS:
        row = report_dict.get(label, {})
        print(
            f"  {label:<14}  "
            f"{row.get('precision', 0.0):>9.4f}  "
            f"{row.get('recall', 0.0):>9.4f}  "
            f"{row.get('f1-score', 0.0):>9.4f}  "
            f"{int(row.get('support', 0)):>8}"
        )

    print(f"  {'-'*14}  {'-'*9}  {'-'*9}  {'-'*9}  {'-'*8}")
    overall = report_dict.get("micro avg", report_dict.get("weighted avg", {}))
    total_support = sum(int(report_dict.get(l, {}).get("support", 0)) for l in ENTITY_LABELS)
    print(
        f"  {'overall':<14}  "
        f"{metrics['precision']:>9.4f}  "
        f"{metrics['recall']:>9.4f}  "
        f"{metrics['f1']:>9.4f}  "
        f"{total_support:>8}"
    )
    print()
    print("Per-class detail:")
    print(metrics["classification_report"])


if __name__ == "__main__":
    evaluate()

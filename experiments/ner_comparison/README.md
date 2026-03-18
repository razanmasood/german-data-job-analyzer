# NER Model Comparison

Comparing four approaches to skill/tool extraction on the same annotated test set:
**GLiNER** (zero-shot), **SpanMarker** (fine-tuned), and **LangExtract** (LLM few-shot, evaluated in `experiments/langextract/02_langextract_eval.py`).
The XLM-RoBERTa HuggingFace Trainer baseline is also included for reference.

---

## Experiment Setup

| Item | Detail |
|---|---|
| Test set | 23 sentences, 325 gold entity spans (212 SKILL, 113 TOOL) |
| Source | `data/processed/ner_dataset/test/` — same split used for XLM-RoBERTa fine-tuning |
| Gold schema | SKILL = technical domain knowledge; TOOL = specific named technology |
| Evaluation | seqeval strict IOB2 (full span must match exactly: text + label + boundaries) |
| Scripts | `01_gliner_eval.py`, `02_spanmarker_train.py`, `03_compare_results.py`, `experiments/langextract/02_langextract_eval.py` |

Both models receive the same plain-text sentences reconstructed from the SentencePiece sub-word tokens stored in the dataset.

---

## Results

### Model Comparison

| Model | Type | Training samples | F1 overall | SKILL F1 | TOOL F1 |
|---|---|---|---|---|---|
| XLM-RoBERTa (HF Trainer) | fine-tuned | 105 | 0.666 | — | — |
| SpanMarker (xlm-roberta-large) | fine-tuned | 105 | **0.675** | 0.61 | **0.82** |
| LangExtract (gemini-2.5-flash-lite) | LLM few-shot | 0 (2 examples) | 0.593 | 0.50 | 0.75 |
| GLiNER (threshold=0.3) | zero-shot | 0 | 0.270 | 0.02 | 0.62 |

### GLiNER — `urchade/gliner_multi-v2.1` (zero-shot)

Evaluated at two confidence thresholds. Lowering the threshold raises recall at the cost of precision.

| Threshold | Entity | Precision | Recall | F1 |
|---|---|---|---|---|
| default (0.5) | SKILL | 0.03 | 0.01 | 0.01 |
| default (0.5) | TOOL | 0.73 | 0.42 | 0.54 |
| default (0.5) | **micro avg** | **0.38** | **0.15** | **0.22** |
| 0.3 | SKILL | 0.04 | 0.02 | 0.02 |
| 0.3 | TOOL | 0.63 | 0.61 | 0.62 |
| 0.3 | **micro avg** | **0.33** | **0.22** | **0.27** |

Full per-example predictions and raw span scores are in `results/gliner_results.json`.
Diagnostic output for the first 3 examples is in `results/gliner_diagnostic.txt`.

### SpanMarker — `xlm-roberta-large` (fine-tuned)

| Entity | Precision | Recall | F1 |
|---|---|---|---|
| SKILL | 0.53 | 0.71 | 0.61 |
| TOOL | 0.79 | 0.84 | 0.82 |
| **micro avg** | **0.611** | **0.754** | **0.675** |

### LangExtract — `gemini-2.5-flash-lite` (few-shot)

2 few-shot examples in prompt; no fine-tuning. Evaluated in `experiments/langextract/02_langextract_eval.py`.

| Entity | Precision | Recall | F1 |
|---|---|---|---|
| SKILL | 0.52 | 0.48 | 0.50 |
| TOOL | 0.69 | 0.81 | 0.75 |
| **micro avg** | **0.590** | **0.597** | **0.593** |

Note: LangExtract's source grounding (character-level span mapping) was unavailable with the Gemini provider — all entity-to-word alignment fell back to substring search. This introduces minor alignment noise but does not affect which entities are extracted.

Full per-example predictions are in `experiments/langextract/results/langextract_eval_results.json`.

---

## Findings

### 1. Fine-tuning still leads, but the gap is smaller than expected

SpanMarker (fine-tuned, 105 sentences) achieves F1=0.675 — the best overall result. However, LangExtract with just 2 few-shot examples reaches F1=0.593, only 0.082 F1 points behind. This gap reflects the value of domain-specific annotation even when using a powerful LLM: the fine-tuned model has seen the exact label schema, entity boundaries, and text style of this dataset; the LLM is inferring them from a 2-example prompt.

### 2. LangExtract outperforms GLiNER zero-shot by a large margin

LangExtract (F1=0.593) more than doubles GLiNER's best result (F1=0.270, threshold=0.3) despite both requiring no training data. The difference is prompt-based schema communication: LangExtract's natural-language prompt defines SKILL as "technical competency or domain knowledge" with examples, allowing the model to align with the annotation schema. GLiNER receives only a bare label string ("SKILL") and defaults to the general-corpus meaning (soft skills, competency phrases).

### 3. TOOL extraction generalises well across approaches; SKILL remains the hard problem

TOOL F1 ranges from 0.62 (GLiNER) to 0.82 (SpanMarker) across all models. Tool names are proper nouns with stable identity — `PyTorch`, `Kubernetes`, `Docker` — that any model recognises. SKILL is the harder entity: our schema uses it for technical domain labels (`machine learning`, `NLP`, `foundation models`), which overlap with common nouns and require schema understanding to annotate correctly. LangExtract's SKILL F1 (0.50) is substantially better than GLiNER (0.02) precisely because the prompt communicates the intended meaning; SpanMarker (0.61) is better still because it has seen labelled examples of the exact boundary convention.

### 4. LangExtract TOOL F1 (0.75) approaches but does not match SpanMarker (0.82)

The 0.07 TOOL F1 gap is likely explained by boundary precision: LangExtract extracts the entity text as a free string and the evaluation maps it back to word boundaries via substring search, which can misalign multi-word spans. SpanMarker predicts IOB tags at the token level and is trained on the exact span conventions in the gold data.

---

## Error Analysis — GLiNER SKILL Near-Zero Recall

SKILL F1 was effectively zero (0.01 at default threshold, 0.02 at 0.3) despite GLiNER returning confident SKILL predictions. This is a **schema disagreement**, not a detection failure.

**What GLiNER predicted as SKILL:**
> `Strong programming skills` (0.87), `Teamfähigkeit` (0.79),
> `Very good German and English skills` (0.71), `Deep expertise` (0.65)

**What the gold labels mark as SKILL:**
> `machine learning`, `NLP`, `computer science`, `foundation models`, `Generative AI`

GLiNER interprets "SKILL" as a soft-skill or competency phrase — the most common sense of the word in general NER corpora. Our annotation schema uses it for technical domain labels: the name of a field or methodology, not the sentence framing it. The model is working correctly; the label name means something different in this project.

TOOL recall was substantially higher (0.42 / 0.61) because tool names (`PyTorch`, `ROS 2`, `Isaac Sim`, `CUDA`) are proper nouns with stable, unambiguous identity across any training corpus — no schema agreement is needed to recognize them.

**Implication:** Zero-shot NER with a general label like "SKILL" will not work for this task without either (a) fine-tuning on domain examples or (b) descriptive entity definitions passed at inference time. LangExtract takes approach (b) and raises SKILL F1 from 0.02 to 0.50.

---

## File Map

```
experiments/ner_comparison/
├── README.md                   ← this file
├── 01_gliner_eval.py           ← GLiNER zero-shot evaluation
├── 02_spanmarker_train.py      ← SpanMarker fine-tuning + evaluation
├── 03_compare_results.py       ← side-by-side metric comparison
└── results/
    ├── gliner_results.json     ← GLiNER metrics + per-example predictions
    ├── gliner_diagnostic.txt   ← human-readable inspection of first 3 examples
    ├── spanmarker_results.json ← SpanMarker metrics + per-example predictions
    └── comparison_summary.json ← side-by-side comparison of all four models

experiments/langextract/
├── 02_langextract_eval.py      ← LangExtract few-shot evaluation
└── results/
    └── langextract_eval_results.json ← LangExtract metrics + per-example predictions
```

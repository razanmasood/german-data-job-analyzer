# NER Model Comparison

Comparing two approaches to skill/tool extraction on the same annotated test set:
**GLiNER** (zero-shot, evaluated here) and **SpanMarker** (fine-tuned, evaluated in `02_spanmarker_train.py`).

---

## Experiment Setup

| Item | Detail |
|---|---|
| Test set | 23 sentences, 325 gold entity spans (212 SKILL, 113 TOOL) |
| Source | `data/processed/ner_dataset/test/` — same split used for XLM-RoBERTa fine-tuning |
| Gold schema | SKILL = technical domain knowledge; TOOL = specific named technology |
| Evaluation | seqeval strict IOB2 (full span must match exactly: text + label + boundaries) |
| Scripts | `01_gliner_eval.py`, `02_spanmarker_train.py`, `03_compare_results.py` |

Both models receive the same plain-text sentences reconstructed from the SentencePiece sub-word tokens stored in the dataset.

---

## Results

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

### SpanMarker (TBD — see Day B)

| Threshold | Entity | Precision | Recall | F1 |
|---|---|---|---|---|
| — | SKILL | TBD | TBD | TBD |
| — | TOOL | TBD | TBD | TBD |
| — | **micro avg** | **TBD** | **TBD** | **TBD** |

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

**Implication:** Zero-shot NER with a general label like "SKILL" will not work for this task without either (a) fine-tuning on domain examples or (b) descriptive entity definitions passed at inference time. This motivates the SpanMarker fine-tuning experiment in `02_spanmarker_train.py`.

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
    ├── spanmarker_results.json ← (TBD)
    └── comparison.json         ← (TBD)
```

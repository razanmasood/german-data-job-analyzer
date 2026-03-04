# Day 8 Session Notes — NER Training Setup

**Date:** 2026-02-24 (Tuesday)

## What was done

### Created `src/ner/train.py`
- Loads pre-tokenized IOB dataset from `data/processed/ner_dataset/` (HuggingFace DatasetDict)
- Fine-tunes `xlm-roberta-large` (558M params) with `AutoModelForTokenClassification`
- 5-class token classification: O, B-SKILL, I-SKILL, B-TOOL, I-TOOL
- Dataset: 105 train / 22 validation / 23 test samples (150 annotated job postings)
- Token-level precision, recall, F1 metrics on entity tokens
- Saves best model by F1 to `models/ner/best/`
- Evaluates on test set after training
- MPS device auto-detection (for Apple Silicon)

### Verified
- xlm-roberta-base and xlm-roberta-large share the same tokenizer (vocab=250,002), so pre-tokenized `input_ids` from `05_convert_to_iob.py` are compatible with both
- Forward pass tested successfully: loss=1.96, logits shape [batch, seq_len, 5]
- Data collator correctly pads batches with label_pad_token_id=-100

### Installed dependencies
- `torch` (CPU-only wheel: `torch-2.10.0+cpu`)
- `accelerate>=1.1.0` (required by Trainer)

## OOM issue
- Both xlm-roberta-large (558M) and xlm-roberta-base (277M) were OOM-killed on the codespace with default memory
- Docker container needs 16GB+ memory allocation
- Training got killed during first batch on CPU

## Next steps (after Docker restart with 16GB)
1. Run `python src/ner/train.py` — configured for:
   - Model: `xlm-roberta-large`
   - Batch size: 8 (train), 16 (eval)
   - 10 epochs, lr=2e-5, warmup=13 steps
   - MPS device (Apple Silicon)
   - No gradient accumulation
2. Review training metrics and adjust hyperparameters if needed
3. Consider adding `seqeval` for proper span-level F1 (current metrics are token-level)

## Training config summary
| Parameter | Value |
|-----------|-------|
| Model | xlm-roberta-large |
| Parameters | 558,845,957 |
| Train batch size | 8 |
| Eval batch size | 16 |
| Epochs | 10 |
| Learning rate | 2e-5 |
| Warmup steps | 13 |
| Weight decay | 0.01 |
| Best model metric | F1 |
| Save total limit | 2 |
| Seed | 42 |

## After /compact
This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.

Analysis:
Let me chronologically analyze the conversation:

1. **Initial Request**: User asked to "Set up NER training for Day 8 — load IOB data and set up tokenization with xlm-roberta-large."

2. **Exploration Phase**: I used an Explore agent to understand the project structure, then read `05_convert_to_iob.py` to understand the data pipeline. Key findings:
   - Project is a German/English job posting NER system
   - 150 annotated job postings converted to IOB format
   - Pre-tokenized dataset in `data/processed/ner_dataset/` with train(105)/val(22)/test(23) splits
   - Labels: O, B-SKILL, I-SKILL, B-TOOL, I-TOOL (5 classes)
   - Dataset already contains `input_ids`, `attention_mask`, `ner_tags`, `tokens`, `id`
   - Tokenized with xlm-roberta-large tokenizer (SentencePiece, vocab=250,002)

3. **Created `src/ner/train.py`**: Full training script with data loading, model setup, metrics, training loop.

4. **Dry run verification**: Confirmed dataset loads, model initializes, forward pass works (loss=1.96, logits shape [2, 243, 5]).

5. **First error**: `ModuleNotFoundError: No module named 'torch'` - Fixed by installing PyTorch CPU wheel.

6. **Second error**: `ImportError: Using the Trainer with PyTorch requires accelerate>=1.1.0` - Fixed by installing accelerate.

7. **Deprecation warning**: `warmup_ratio is deprecated` - Fixed by switching to `warmup_steps=13`.

8. **OOM Kill**: xlm-roberta-large (558M params) got OOM-killed on CPU during training. Then xlm-roberta-base (277M) also got OOM-killed.

9. **User choice**: Asked user about model size. User said: "Switch to xlm-roberta-base and enable MPS device for Apple Silicon training."

10. **Switched to base**: Changed MODEL_NAME to xlm-roberta-base, added MPS device detection. Verified tokenizers are compatible (same vocab, same IDs).

11. **Still OOM**: xlm-roberta-base also killed. I tried to reduce batch size but user rejected the edit.

12. **User's file modification**: The system noted the user modified train.py - the file now shows xlm-roberta-base with batch_size=8.

13. **Final request**: User said: "Save current train.py state and write a summary to docs/session_notes.md. I need to restart the Docker container to increase memory to 16GB. When I'm back, the goal is to run training with xlm-roberta-large, batch_size=8, no gradient accumulation, on MPS device."

14. I switched train.py back to xlm-roberta-large (since that's the goal after restart) and created docs/session_notes.md.

15. **User feedback on session_notes.md**: User rejected first write because I forgot to add the date. I added "**Date:** 2026-02-24 (Monday)" and it was accepted.

Current state of train.py: xlm-roberta-large, batch_size=8, eval_batch=16, MPS support, no gradient accumulation.

Summary:
1. Primary Request and Intent:
   - **Initial request**: "Set up NER training for Day 8 — load IOB data and set up tokenization with xlm-roberta-large"
   - **Final request**: Save current `train.py` state and write a summary to `docs/session_notes.md`. User needs to restart Docker container to increase memory to 16GB. After restart, the goal is to run training with `xlm-roberta-large`, `batch_size=8`, no gradient accumulation, on MPS device (Apple Silicon).
   - The user is following a project schedule (`German_Data_Jobs_Schedule.md`) where Day 8 is about getting the NER training script ready and doing a first training run.

2. Key Technical Concepts:
   - **NER (Named Entity Recognition)** for extracting SKILL and TOOL entities from German/English job postings
   - **IOB tagging scheme**: O, B-SKILL, I-SKILL, B-TOOL, I-TOOL (5 labels, plus -100 for special tokens)
   - **xlm-roberta-large** (558M params) — multilingual transformer for token classification
   - **xlm-roberta-base** (277M params) — shares identical tokenizer/vocab (250,002 tokens) with large variant
   - **Pre-tokenized HuggingFace DatasetDict** with `input_ids`, `attention_mask`, `ner_tags`, `tokens`, `id` columns
   - **DataCollatorForTokenClassification** for dynamic batch padding with `label_pad_token_id=-100`
   - **MPS device support** for Apple Silicon GPU acceleration
   - **SentencePiece tokenizer** — both base and large share the same vocabulary and produce identical `input_ids`
   - Dataset: 105 train / 22 validation / 23 test samples from 150 annotated job postings (2,286 total entities)

3. Files and Code Sections:

   - **`src/ner/train.py`** (CREATED — main deliverable)
     - Full NER training script, currently configured for xlm-roberta-large
     - Key sections: `load_dataset()`, `compute_metrics()`, `main()` with Trainer setup
     - Final state of the file:
     ```python
     """
     NER training script for German/English job posting skill & tool extraction.
     
     Loads pre-tokenized IOB dataset and fine-tunes xlm-roberta-large
     for token classification (O, B-SKILL, I-SKILL, B-TOOL, I-TOOL).
     """
     
     import json
     from pathlib import Path
     
     import numpy as np
     import torch
     from datasets import DatasetDict
     from transformers import (
         AutoModelForTokenClassification,
         AutoTokenizer,
         DataCollatorForTokenClassification,
         Trainer,
         TrainingArguments,
     )
     
     PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
     DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "ner_dataset"
     OUTPUT_DIR = PROJECT_ROOT / "models" / "ner"
     MODEL_NAME = "xlm-roberta-large"
     
     LABEL_LIST = ["O", "B-SKILL", "I-SKILL", "B-TOOL", "I-TOOL"]
     LABEL2ID = {label: i for i, label in enumerate(LABEL_LIST)}
     ID2LABEL = {i: label for i, label in enumerate(LABEL_LIST)}
     NUM_LABELS = len(LABEL_LIST)
     ```
     - Device detection with MPS support:
     ```python
     if torch.cuda.is_available():
         device = "cuda"
     elif torch.backends.mps.is_available():
         device = "mps"
     else:
         device = "cpu"
     ```
     - TrainingArguments configured for: batch_size=8 train / 16 eval, 10 epochs, lr=2e-5, warmup_steps=13, weight_decay=0.01, save_total_limit=2, best model by F1
     - Dataset preparation: renames `ner_tags` → `labels`, removes `id` and `tokens` columns
     - Saves best model + tokenizer + label_map.json to `models/ner/best/`
     - Evaluates on test set after training

   - **`scripts/05_convert_to_iob.py`** (READ — reference for data pipeline)
     - Converts Label Studio JSON annotations to IOB-tagged HuggingFace Dataset
     - Uses xlm-roberta-large tokenizer with `return_offsets_mapping=True` for character-to-token alignment
     - Saves to `data/processed/ner_dataset/` as DatasetDict with train/val/test splits (70/15/15)
     - Important for understanding that the dataset is already pre-tokenized

   - **`data/processed/ner_dataset/`** (READ — training data)
     - Contains `dataset_dict.json`, `label_map.json`, `train/`, `validation/`, `test/` directories
     - `label_map.json`: `{"label_list": ["O", "B-SKILL", "I-SKILL", "B-TOOL", "I-TOOL"], "label2id": {...}}`
     - Columns: `id` (int32), `tokens` (Sequence[string]), `ner_tags` (Sequence[int32]), `input_ids` (Sequence[int32]), `attention_mask` (Sequence[int32])

   - **`docs/session_notes.md`** (CREATED — session summary)
     - Documents what was done, OOM issues, next steps, training config table
     - Dated 2026-02-24

   - **`requirements.txt`** (READ)
     - Contains: transformers, datasets, torch, streamlit, label-studio-sdk, pandas, scikit-learn, seaborn, requests, tqdm

4. Errors and fixes:
   - **`ModuleNotFoundError: No module named 'torch'`**: Fixed by `pip install torch --index-url https://download.pytorch.org/whl/cpu`
   - **`ImportError: Using the Trainer with PyTorch requires accelerate>=1.1.0`**: Fixed by `pip install 'accelerate>=1.1.0'` (version 1.12.0 installed)
   - **`warmup_ratio is deprecated and will be removed in v5.2`**: Fixed by replacing `warmup_ratio=0.1` with `warmup_steps=13`
   - **OOM Kill (exit code 137)**: xlm-roberta-large (558M params) killed during first training batch on CPU. xlm-roberta-base (277M) also killed. Root cause: insufficient Docker container memory. User decided to restart container with 16GB.
   - **User rejected batch size reduction edit**: I tried to change batch_size from 8→4 with gradient_accumulation_steps=2, but user rejected this. User's final intent is batch_size=8, no gradient accumulation, with more memory.
   - **User rejected first `session_notes.md`**: Missing the date of the session. Fixed by adding `**Date:** 2026-02-24 (Monday)` to the file.

5. Problem Solving:
   - Verified tokenizer compatibility between xlm-roberta-base and xlm-roberta-large — both produce identical `input_ids` (same SentencePiece vocab of 250,002 tokens), so pre-tokenized data works with either model
   - Successfully ran a dry-run: loaded dataset → loaded model → created batch with data collator → forward pass (loss=1.96, logits [2, 243, 5])
   - UNEXPECTED/MISSING keys in model load report are expected — loading a masked LM checkpoint for token classification drops the LM head and randomly initializes the classifier head
   - OOM issue remains unresolved — requires Docker restart with 16GB memory

6. All user messages:
   - "Set up NER training for Day 8 — load IOB data and set up tokenization with xlm-roberta-large."
   - User provided full training run output showing the OOM crash with xlm-roberta-base, asking about it (the output showed the ImportError for accelerate)
   - When asked about model size: "Switch to xlm-roberta-base and enable MPS device for Apple Silicon training."
   - User rejected the batch size reduction edit (no explicit message, just rejection)
   - "Save current train.py state and write a summary to docs/session_notes.md. I need to restart the Docker container to increase memory to 16GB. When I'm back, the goal is to run training with xlm-roberta-large, batch_size=8, no gradient accumulation, on MPS device."
   - User rejected first session_notes.md with feedback: "Add the date of the session as well"

7. Pending Tasks:
   - After Docker restart with 16GB memory: run `python src/ner/train.py` with xlm-roberta-large, batch_size=8, MPS device
   - Will need to reinstall `torch` (with MPS support, not CPU-only) and `accelerate` after container restart
   - Review training metrics and adjust hyperparameters if needed

8. Current Work:
   The final task was saving `train.py` in its xlm-roberta-large configuration and writing `docs/session_notes.md`. Both are complete. The script is ready to run after the Docker container restart with 16GB memory. Current `train.py` is configured for: `xlm-roberta-large`, `batch_size=8`, `eval_batch=16`, `10 epochs`, `lr=2e-5`, MPS device support, no gradient accumulation.

9. Optional Next Step:
   After the user returns from Docker restart with 16GB memory, the next step is:
   - Install `torch` with MPS support: `pip install torch accelerate`
   - Run training: `python src/ner/train.py`
   
   Per user's explicit statement: "When I'm back, the goal is to run training with xlm-roberta-large, batch_size=8, no gradient accumulation, on MPS device."

If you need specific details from before compaction (like exact code snippets, error messages, or content you generated), read the full transcript at: /root/.claude/projects/-workspaces-german-data-job-analyzer/6a76338f-d2b0-4ebe-b624-cb40581608d9.jsonl
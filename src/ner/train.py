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

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "ner_dataset"
OUTPUT_DIR = PROJECT_ROOT / "models" / "ner"
MODEL_NAME = "xlm-roberta-large"

# Labels
LABEL_LIST = ["O", "B-SKILL", "I-SKILL", "B-TOOL", "I-TOOL"]
LABEL2ID = {label: i for i, label in enumerate(LABEL_LIST)}
ID2LABEL = {i: label for i, label in enumerate(LABEL_LIST)}
NUM_LABELS = len(LABEL_LIST)


def load_dataset():
    """Load pre-tokenized IOB dataset from disk."""
    print(f"Loading dataset from {DATASET_PATH}")
    dataset = DatasetDict.load_from_disk(str(DATASET_PATH))
    print(f"  Train: {len(dataset['train'])} samples")
    print(f"  Val:   {len(dataset['validation'])} samples")
    print(f"  Test:  {len(dataset['test'])} samples")
    return dataset


def compute_metrics(eval_pred):
    """Compute precision, recall, F1 for entity tokens (ignoring O and -100)."""
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)

    # Flatten
    true_labels = []
    pred_labels = []
    for pred_seq, label_seq in zip(predictions, labels):
        for pred, label in zip(pred_seq, label_seq):
            if label == -100:
                continue
            true_labels.append(label)
            pred_labels.append(pred)

    true_labels = np.array(true_labels)
    pred_labels = np.array(pred_labels)

    # Entity-level metrics (non-O labels)
    entity_mask = true_labels != LABEL2ID["O"]
    pred_entity_mask = pred_labels != LABEL2ID["O"]

    # True positives: predicted entity label matches true entity label
    tp = np.sum((pred_labels == true_labels) & entity_mask)
    # False positives: predicted as entity but wrong
    fp = np.sum(pred_entity_mask & ~(pred_labels == true_labels))
    # False negatives: true entity but not predicted correctly
    fn = np.sum(entity_mask & ~(pred_labels == true_labels))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    # Overall accuracy (all tokens including O)
    accuracy = np.mean(pred_labels == true_labels)

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
    }


def main():
    print("=" * 60)
    print("NER Training — xlm-roberta-large")
    print("=" * 60)

    # Check device
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    print(f"\nDevice: {device}")

    # Load dataset
    dataset = load_dataset()

    # Load tokenizer (needed for data collator padding)
    print(f"\nLoading tokenizer: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # Load model
    print(f"Loading model: {MODEL_NAME}")
    model = AutoModelForTokenClassification.from_pretrained(
        MODEL_NAME,
        num_labels=NUM_LABELS,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )
    print(f"  Parameters: {model.num_parameters():,}")

    # Data collator — pads input_ids, attention_mask, and labels (ner_tags)
    # to the longest sequence in each batch
    data_collator = DataCollatorForTokenClassification(
        tokenizer=tokenizer,
        padding=True,
        label_pad_token_id=-100,
    )

    # Rename ner_tags → labels (expected by Trainer)
    dataset = dataset.rename_column("ner_tags", "labels")
    # Remove columns not needed by the model
    dataset = dataset.remove_columns(["id", "tokens"])

    # Training arguments
    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=16,
        num_train_epochs=10,
        weight_decay=0.01,
        warmup_steps=13,  # ~10% of 105 samples / batch 8 = 14 steps per epoch
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        save_total_limit=2,
        logging_steps=10,
        fp16=torch.cuda.is_available(),  # MPS doesn't support fp16 via Trainer
        report_to="none",
        seed=42,
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )

    # Train
    print(f"\nStarting training...")
    print(f"  Epochs: {training_args.num_train_epochs}")
    print(f"  Batch size: {training_args.per_device_train_batch_size}")
    print(f"  Learning rate: {training_args.learning_rate}")
    print(f"  Output: {OUTPUT_DIR}")
    print()

    train_result = trainer.train()

    # Save best model
    best_model_path = OUTPUT_DIR / "best"
    trainer.save_model(str(best_model_path))
    tokenizer.save_pretrained(str(best_model_path))
    print(f"\n✓ Best model saved to {best_model_path}")

    # Save label map alongside model
    label_map_path = best_model_path / "label_map.json"
    with open(label_map_path, "w") as f:
        json.dump({"label_list": LABEL_LIST, "label2id": LABEL2ID, "id2label": ID2LABEL}, f, indent=2)

    # Final evaluation on test set
    print("\nEvaluating on test set...")
    test_metrics = trainer.evaluate(dataset["test"], metric_key_prefix="test")
    print(f"\nTest Results:")
    for key, value in sorted(test_metrics.items()):
        if key.startswith("test_"):
            print(f"  {key}: {value:.4f}")

    # Training summary
    print(f"\nTraining Summary:")
    print(f"  Train loss: {train_result.metrics['train_loss']:.4f}")
    print(f"  Train samples: {train_result.metrics['train_samples_per_second']:.1f}/s")
    print(f"  Total steps: {train_result.global_step}")

    print(f"\n{'=' * 60}")
    print("Done!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

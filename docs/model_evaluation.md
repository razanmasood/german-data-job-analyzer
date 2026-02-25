# NER Model Evaluation

## Model

- **Base model:** xlm-roberta-large (559M parameters)
- **Task:** Token classification (IOB tagging) for SKILL and TOOL entity extraction from German/English job postings
- **Labels:** O, B-SKILL, I-SKILL, B-TOOL, I-TOOL

## Training Configuration

| Parameter                  | Value              |
|----------------------------|--------------------|
| Base model                 | xlm-roberta-large  |
| Per-device batch size      | 2                  |
| Gradient accumulation steps| 4                  |
| Effective batch size       | 8                  |
| Gradient checkpointing     | Enabled            |
| Epochs                     | 10                 |
| Learning rate              | 2e-5               |
| Weight decay               | 0.01               |
| Device                     | MPS (Apple M4)     |
| FP16                       | No (not supported on MPS) |
| Best model selection       | Highest val F1     |

## Dataset

| Split      | Samples |
|------------|---------|
| Train      | 105     |
| Validation | 22      |
| Test       | 23      |

## Test Set Results

| Metric    | Score  |
|-----------|--------|
| F1        | 0.6660 |
| Precision | 0.6435 |
| Recall    | 0.6902 |
| Accuracy  | 0.8799 |
| Loss      | 0.3297 |

## Notes

- The first training attempt with batch size 8 ran out of MPS memory. Reducing to batch size 2 with gradient accumulation 4 and enabling gradient checkpointing resolved the issue while maintaining the same effective batch size.
- Performance is expected to improve significantly with more labeled training data. The current dataset of 105 training samples is small for a model of this size.

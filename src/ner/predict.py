"""
Inference helper for the fine-tuned NER model.

Returns deduplicated lists of extracted SKILL and TOOL entities
from a raw text string.
"""

from pathlib import Path
from transformers import pipeline

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "ner" / "best"


def load_pipeline():
    """Load the token-classification pipeline from the local model directory."""
    return pipeline(
        "ner",
        model=str(MODEL_PATH),
        tokenizer=str(MODEL_PATH),
        aggregation_strategy="simple",
        device=-1,  # CPU
    )


def extract_entities(text: str, ner_pipeline) -> tuple[list[str], list[str]]:
    """
    Run NER on *text* and return (skills, tools) as deduplicated lowercase lists.
    """
    if not text.strip():
        return [], []

    results = ner_pipeline(text)

    skills, tools = [], []
    seen = set()
    for entity in results:
        group = entity.get("entity_group", "")
        word = entity.get("word", "").strip().lower()
        if not word or word in seen:
            continue
        seen.add(word)
        if group == "SKILL":
            skills.append(word)
        elif group == "TOOL":
            tools.append(word)

    return skills, tools

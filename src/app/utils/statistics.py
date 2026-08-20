from pydoc import Doc
import re
from dataclasses import asdict, dataclass

@dataclass(frozen=True)
class DocumentStats:
    character_count: int
    word_count: int
    line_count: int
    paragraph_count: int
    unique_word_count: int
    average_word_length: float

def compute_statistics(text: str) -> DocumentStats:
    characters = len(text)
    words = re.findall(r"[a-z0-9]+", text.lower())
    lines = text.split("\n") if text else []
    paragraphs = [p for p in text.split("\n") if p.strip()] if text else []

    word_count = len(words)
    unique_word_count = len(set(words))
    average_word_length = round(
        sum(len(word) for word in words) / word_count, 1
    ) if word_count else 0.0

    return DocumentStats(
        character_count=characters,
        word_count=word_count,
        line_count=len(lines),
        paragraph_count=len(paragraphs),
        unique_word_count=unique_word_count,
        average_word_length=average_word_length
    )

def stats_to_dict(stats: DocumentStats) -> dict:
    return asdict(stats)
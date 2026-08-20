"""
Text utilities for the project.

This module contains functions to clean and extract keywords from text.

Functions:
- clean_text: Clean the text by removing special characters and normalizing the text.
- extract_keywords: Extract keywords from the text by finding the most common words.
"""

import re
import unicodedata
from collections import Counter

def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\n", " ")
    text = re.sub(r"[\t]+", " ", text)
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    return "\n".join(lines)

def extract_keywords(text: str, *, top_n: int = 20) -> list[dict]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    tokens = [token for token in tokens if len(token) > 1]
    counts = Counter(tokens)
    return [
        {"word": word, "count": count}
        for word, count in counts.most_common(top_n)
    ]
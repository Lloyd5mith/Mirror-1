# tokenizer.py
import re
from typing import List

META_PREFIX = "__meta__"


def tokenize(text: str) -> List[str]:
    """
    Tokenize input text into lowercase word tokens.

    HARD RULE:
    - Meta tokens (starting with "__meta__") never reach the system as learnable symbols.
    """
    tokens = re.findall(r"\b\w+\b", (text or "").lower())
    return [t for t in tokens if t and not t.startswith(META_PREFIX)]


def norm(text: str, max_len: int) -> str:
    return (text or "").strip().lower()[:max_len]


def bracket(text: str) -> str:
    return f"[{text}]"

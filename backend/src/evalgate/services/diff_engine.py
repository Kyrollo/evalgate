from __future__ import annotations

import difflib
import re
from src.evalgate.domain.entities import DiffToken


def tokenize_words(text: str) -> list[str]:
    """Tokenize string into words and whitespace/punctuation preserving tokens."""
    return re.findall(r"\w+|\s+|[^\w\s]", text)


def compute_word_diff(baseline_text: str, candidate_text: str) -> list[DiffToken]:
    """Compute word-level diff between baseline output and candidate output."""
    if baseline_text == candidate_text:
        return [DiffToken(type="unchanged", text=candidate_text)]

    b_tokens = tokenize_words(baseline_text)
    c_tokens = tokenize_words(candidate_text)

    matcher = difflib.SequenceMatcher(None, b_tokens, c_tokens)
    diff_tokens: list[DiffToken] = []

    for tag, b_start, b_end, c_start, c_end in matcher.get_opcodes():
        if tag == "equal":
            diff_tokens.append(DiffToken(type="unchanged", text="".join(c_tokens[c_start:c_end])))
        elif tag == "delete":
            diff_tokens.append(DiffToken(type="removed", text="".join(b_tokens[b_start:b_end])))
        elif tag == "insert":
            diff_tokens.append(DiffToken(type="added", text="".join(c_tokens[c_start:c_end])))
        elif tag == "replace":
            diff_tokens.append(DiffToken(type="removed", text="".join(b_tokens[b_start:b_end])))
            diff_tokens.append(DiffToken(type="added", text="".join(c_tokens[c_start:c_end])))

    return diff_tokens

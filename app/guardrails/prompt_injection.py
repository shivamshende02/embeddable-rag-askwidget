import re

INJECTION_PATTERNS = [
    re.compile(r"ignore (all )?(previous|prior|above) instructions", re.IGNORECASE),
    re.compile(r"you are now (a|an) ", re.IGNORECASE),
    re.compile(r"reveal (your |the )?system prompt", re.IGNORECASE),
    re.compile(r"disregard.*instructions", re.IGNORECASE),
]

def contains_injection_attempt(text: str) -> bool:
    return any(pattern.search(text) for pattern in INJECTION_PATTERNS)
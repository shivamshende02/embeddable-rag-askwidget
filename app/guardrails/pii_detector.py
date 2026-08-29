import re

PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(r"\b\d{10}\b|\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b"),
    "credit_card": re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
}

def detect_pii(text: str) -> dict[str, list[str]]:
    findings = {}
    for label, pattern in PII_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            findings[label] = matches
    return findings

def redact_pii(text: str) -> str:
    """Optional helper to replace detected PII with [REDACTED]."""
    redacted_text = text
    for pattern in PII_PATTERNS.values():
        redacted_text = pattern.sub("[REDACTED]", redacted_text)
    return redacted_text
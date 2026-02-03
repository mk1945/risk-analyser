from __future__ import annotations

import re
from typing import Any


def redact_text(text: str, entities: dict[str, Any]) -> str:
    """Best-effort local redaction to reduce sensitive leakage.

    Redacts detected parties/dates/amounts and common ID patterns.
    """
    out = text

    for p in entities.get("parties", [])[:20]:
        out = re.sub(re.escape(p), "[PARTY]", out, flags=re.IGNORECASE)

    for a in entities.get("amounts", [])[:20]:
        out = re.sub(re.escape(a), "[AMOUNT]", out, flags=re.IGNORECASE)

    for d in entities.get("dates", [])[:20]:
        out = re.sub(re.escape(d), "[DATE]", out, flags=re.IGNORECASE)

    # emails, phone numbers
    out = re.sub(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", "[EMAIL]", out, flags=re.IGNORECASE)
    out = re.sub(r"\b\+?\d[\d\s\-]{8,}\d\b", "[PHONE]", out)

    return out

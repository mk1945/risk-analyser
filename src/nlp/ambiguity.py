from __future__ import annotations

import re
from typing import Any


_AMBIGUOUS_TERMS_EN = [
    ("reasonable", r"\breasonable\b"),
    ("best efforts", r"\bbest efforts\b"),
    ("commercially reasonable", r"\bcommercially reasonable\b"),
    ("as soon as possible", r"\bas soon as possible\b|\basap\b"),
    ("material", r"\bmaterial\b"),
    ("from time to time", r"\bfrom time to time\b"),
    ("including but not limited", r"including\s+but\s+not\s+limited\s+to"),
    ("sole discretion", r"\bsole discretion\b"),
    ("as applicable", r"\bas applicable\b"),
    ("etc.", r"\betc\.?\b"),
]

_AMBIGUOUS_TERMS_HI = [
    ("उचित/उचितता (reasonable)", r"उचित"),
    ("यथाशीघ्र (ASAP)", r"यथाशीघ्र|शीघ्र"),
    ("समय-समय पर (from time to time)", r"समय\s*-?\s*समय\s*पर"),
    ("प्रासंगिक/लागू होने पर (as applicable)", r"लागू\s*होने\s*पर|प्रासंगिक"),
    ("आदि (etc.)", r"आदि"),
    ("पूर्ण विवेकाधिकार (sole discretion)", r"विवेकाधिकार|पूर्ण\s*विवेक"),
]


def detect_ambiguities(*, clauses: list[dict[str, Any]], lang: str) -> dict[str, list[dict[str, Any]]]:
    """Detect ambiguity signals per clause.

    Returns: clause_id -> [{term, evidence}]
    """

    out: dict[str, list[dict[str, Any]]] = {}

    patterns = _AMBIGUOUS_TERMS_HI if lang == "hi" else _AMBIGUOUS_TERMS_EN

    for c in clauses:
        cid = str(c.get("id"))
        text = str(c.get("text", ""))
        t = text if lang == "hi" else text.lower()

        hits: list[dict[str, Any]] = []
        for label, pat in patterns:
            m = re.search(pat, t, flags=re.IGNORECASE if lang != "hi" else 0)
            if not m:
                continue
            start = max(0, m.start() - 60)
            end = min(len(text), m.end() + 60)
            evidence = " ".join(text[start:end].split())
            hits.append({"term": label, "evidence": evidence})

        out[cid] = hits

    return out

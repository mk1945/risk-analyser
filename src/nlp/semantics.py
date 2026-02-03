from __future__ import annotations

import re
from typing import Any


_OBLIGATION_PATTERNS = [
    r"\bshall\b",
    r"\bmust\b",
    r"\bis required to\b",
    r"\bagrees to\b",
    r"\bwill\b",
]

_RIGHT_PATTERNS = [
    r"\bmay\b",
    r"\bis entitled to\b",
    r"\bhas the right to\b",
    r"\bcan\b",
]

_PROHIBITION_PATTERNS = [
    r"\bshall not\b",
    r"\bmust not\b",
    r"\bis prohibited\b",
    r"\bmay not\b",
]

# Very lightweight Hindi signals (best-effort; not a full Hindi NLP model)
_HI_OBLIGATION = [r"अनिवार्य", r"करना होगा", r"करेगा", r"करेगी", r"पालन करेगा"]
_HI_RIGHT = [r"अधिकार", r"हक", r"कर सकता", r"कर सकती", r"प्राप्त होगा"]
_HI_PROHIBITION = [r"नहीं करेगा", r"नहीं करेगी", r"प्रतिबंधित", r"वर्जित"]


def extract_obligation_right_prohibition(*, clauses: list[dict[str, Any]], lang: str) -> dict[str, dict[str, Any]]:
    """Extract obligation/right/prohibition statements per clause.

    Returns a mapping: clause_id -> {obligations:[], rights:[], prohibitions:[]}
    with short sentence snippets.
    """

    out: dict[str, dict[str, Any]] = {}
    for c in clauses:
        cid = str(c.get("id"))
        text = str(c.get("text", ""))
        snippets = _split_sentences(text)

        obligations: list[str] = []
        rights: list[str] = []
        prohibitions: list[str] = []

        for s in snippets:
            k = s.strip()
            if len(k) < 12:
                continue

            if _is_prohibition(k, lang=lang):
                prohibitions.append(_clip(k))
                continue
            if _is_obligation(k, lang=lang):
                obligations.append(_clip(k))
                continue
            if _is_right(k, lang=lang):
                rights.append(_clip(k))

        out[cid] = {
            "obligations": obligations[:10],
            "rights": rights[:10],
            "prohibitions": prohibitions[:10],
        }

    return out


def _split_sentences(text: str) -> list[str]:
    # Cheap sentence segmentation that works reasonably for contracts.
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    # Keep numbered subclauses as separate lines
    parts = re.split(r"(?<=[\.;])\s+|\n+", t)
    return [p.strip() for p in parts if p and p.strip()]


def _is_obligation(s: str, *, lang: str) -> bool:
    sl = s.lower()
    if lang == "hi":
        return any(re.search(p, s) for p in _HI_OBLIGATION)
    return any(re.search(p, sl) for p in _OBLIGATION_PATTERNS)


def _is_right(s: str, *, lang: str) -> bool:
    sl = s.lower()
    if lang == "hi":
        return any(re.search(p, s) for p in _HI_RIGHT)
    return any(re.search(p, sl) for p in _RIGHT_PATTERNS)


def _is_prohibition(s: str, *, lang: str) -> bool:
    sl = s.lower()
    if lang == "hi":
        return any(re.search(p, s) for p in _HI_PROHIBITION)
    return any(re.search(p, sl) for p in _PROHIBITION_PATTERNS)


def _clip(s: str, max_len: int = 240) -> str:
    s = " ".join(s.split())
    return s if len(s) <= max_len else s[: max_len - 1].rstrip() + "…"

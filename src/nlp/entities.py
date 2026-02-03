from __future__ import annotations

import re
from typing import Any

import spacy


_AMOUNT_RE = re.compile(r"(?i)\b(?:INR|Rs\.?|₹)\s?([0-9][0-9,]*(?:\.[0-9]{1,2})?)\b")
_DATE_RE = re.compile(
    r"\b(\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4}|\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b",
    re.IGNORECASE,
)


def _get_nlp(lang: str):
    # Keep this forgiving; if model not present, use blank pipeline.
    if lang == "en":
        try:
            return spacy.load("en_core_web_sm")
        except Exception:
            return spacy.blank("en")
    return spacy.blank("xx")


def extract_entities(text: str, *, lang: str) -> dict[str, Any]:
    nlp = _get_nlp(lang)
    doc = nlp(text[:200000])  # safety cap

    parties: list[str] = []
    dates: list[str] = []
    money: list[str] = []
    jurisdictions: list[str] = []

    # spaCy entities (best effort)
    for ent in getattr(doc, "ents", []):
        if ent.label_ in {"ORG", "PERSON"}:
            parties.append(ent.text)
        if ent.label_ in {"GPE", "LOC"}:
            jurisdictions.append(ent.text)
        if ent.label_ in {"DATE"}:
            dates.append(ent.text)
        if ent.label_ in {"MONEY"}:
            money.append(ent.text)

    # regex backups
    for m in _AMOUNT_RE.finditer(text):
        money.append(m.group(0))
    for m in _DATE_RE.finditer(text):
        dates.append(m.group(0))

    jurisdictions += _extract_jurisdiction_lines(text)

    return {
        "parties": _uniq(parties)[:30],
        "dates": _uniq(dates)[:30],
        "amounts": _uniq(money)[:30],
        "jurisdiction": _uniq(jurisdictions)[:20],
    }


def _extract_jurisdiction_lines(text: str) -> list[str]:
    hits: list[str] = []
    for line in text.splitlines():
        if re.search(r"(?i)governing law|jurisdiction|courts at|seat of arbitration", line):
            hits.append(line.strip())
    return [h for h in hits if h]


def _uniq(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        key = " ".join(x.split()).strip()
        if not key:
            continue
        if key.lower() in seen:
            continue
        seen.add(key.lower())
        out.append(key)
    return out

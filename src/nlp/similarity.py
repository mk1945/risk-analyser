from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

from src.nlp.sectioning import extract_clauses


_TEMPLATE_MAP = {
    "service": "service_agreement_sme_friendly.md",
    "employment": "employment_agreement_sme_friendly.md",
    "vendor": "vendor_supply_agreement_sme_friendly.md",
    "lease": "lease_agreement_sme_friendly.md",
    "partnership": "partnership_deed_sme_friendly.md",
}


def match_to_templates(*, clauses: list[dict[str, Any]], contract_type: str) -> dict[str, dict[str, Any]]:
    """Match each extracted clause to the closest clause from a standard SME-friendly template.

    Similarity uses a lightweight cosine similarity over token counts (no external embeddings).

    Returns: clause_id -> {template_clause_id, template_title, score}
    """

    template = _load_template(contract_type)
    if not template:
        return {str(c.get("id")): {"available": False} for c in clauses}

    template_clauses = extract_clauses(template)
    if not template_clauses:
        return {str(c.get("id")): {"available": False} for c in clauses}

    t_vectors = [(tc, _vectorize(tc.get("text", ""))) for tc in template_clauses]

    out: dict[str, dict[str, Any]] = {}
    for c in clauses:
        cid = str(c.get("id"))
        v = _vectorize(str(c.get("text", "")))

        best_score = 0.0
        best = None
        for tc, tv in t_vectors:
            score = _cosine(v, tv)
            if score > best_score:
                best_score = score
                best = tc

        out[cid] = {
            "available": True,
            "template_clause_id": str(best.get("id")) if best else None,
            "template_title": str(best.get("title")) if best else None,
            "score": round(float(best_score), 3),
        }

    return out


def _load_template(contract_type: str) -> str | None:
    name = _TEMPLATE_MAP.get(contract_type)
    if not name:
        return None

    p = Path("data") / "templates" / name
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8")


def _tokenize(text: str) -> list[str]:
    text = text.lower()
    tokens = re.findall(r"[a-z0-9]{2,}", text)
    # tiny stopword list to reduce noise
    stop = {
        "the",
        "and",
        "or",
        "to",
        "of",
        "in",
        "for",
        "a",
        "an",
        "by",
        "on",
        "with",
        "as",
        "shall",
        "will",
        "may",
        "must",
        "party",
        "parties",
        "agreement",
        "clause",
    }
    return [t for t in tokens if t not in stop]


def _vectorize(text: str) -> Counter[str]:
    return Counter(_tokenize(text))


def _cosine(a: Counter[str], b: Counter[str]) -> float:
    if not a or not b:
        return 0.0

    dot = 0.0
    for k, av in a.items():
        bv = b.get(k)
        if bv:
            dot += float(av * bv)

    na = sum(v * v for v in a.values()) ** 0.5
    nb = sum(v * v for v in b.values()) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return float(dot / (na * nb))

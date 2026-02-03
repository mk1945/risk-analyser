from __future__ import annotations

import re
from typing import Any


_HEADING_RE = re.compile(
    r"^(?P<num>(?:\d+\.)+\d+|\d+)\s+(?P<title>[A-Z][^\n]{0,120})$",
    re.MULTILINE,
)


def extract_clauses(text: str) -> list[dict[str, Any]]:
    """Best-effort clause segmentation for typical Indian SME contracts.

    Works on:
    - numbered headings: `1. Definitions`, `2.1 Term`, etc.
    - uppercase headings: `TERMINATION`, `CONFIDENTIALITY`

    Returns a list of {id, title, text}.
    """
    normalized = _normalize(text)

    # Prefer numbered headings
    matches = list(_HEADING_RE.finditer(normalized))
    if not matches:
        return _fallback_blocks(normalized)

    clauses: list[dict[str, Any]] = []
    for idx, m in enumerate(matches):
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(normalized)
        clause_text = normalized[start:end].strip()
        clauses.append(
            {
                "id": m.group("num"),
                "title": m.group("title").strip(),
                "text": clause_text if clause_text else m.group(0),
            }
        )

    return _postprocess(clauses)


def _normalize(text: str) -> str:
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _fallback_blocks(text: str) -> list[dict[str, Any]]:
    # Split by blank lines; treat each block as a clause-like unit.
    parts = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    clauses: list[dict[str, Any]] = []
    for i, p in enumerate(parts, start=1):
        title = p.split("\n", 1)[0][:80]
        clauses.append({"id": str(i), "title": title, "text": p})
    return _postprocess(clauses)


def _postprocess(clauses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for c in clauses:
        text = c["text"].strip()
        if len(text) < 20:
            continue
        out.append({"id": c["id"], "title": c["title"], "text": text})
    return out

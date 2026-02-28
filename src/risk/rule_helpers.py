from __future__ import annotations

import re
from typing import Any

from src.risk.rules import _RULES


def match_clause_flags(clause_text: str) -> list[dict[str, Any]]:
    t = clause_text.lower()
    out: list[dict[str, Any]] = []
    for r in _RULES:
        for p in r["patterns"]:
            if re.search(p, t):
                out.append({"rule_id": r["id"], "label": r["label"], "severity": r["severity"]})
                break
    return out

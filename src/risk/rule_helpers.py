from __future__ import annotations

import re
from typing import Any


_CLAUSE_RULES = [
    {
        "id": "penalty",
        "label": "Penalty / Liquidated damages",
        "severity": "high",
        "patterns": [r"liquidated damages", r"penalt(y|ies)", r"late fee", r"interest at .*%"],
    },
    {
        "id": "indemnity",
        "label": "Broad indemnity",
        "severity": "high",
        "patterns": [r"indemnif(y|ies)", r"hold harmless"],
    },
    {
        "id": "unilateral_termination",
        "label": "Unilateral termination",
        "severity": "high",
        "patterns": [r"terminate .* without cause", r"at any time .* terminate", r"sole discretion"],
    },
    {
        "id": "arbitration_jurisdiction",
        "label": "Arbitration / Jurisdiction constraints",
        "severity": "medium",
        "patterns": [r"arbitration", r"seat of arbitration", r"exclusive jurisdiction", r"courts at"],
    },
    {
        "id": "auto_renew_lockin",
        "label": "Auto-renewal / Lock-in",
        "severity": "medium",
        "patterns": [r"auto[- ]renew", r"automatically renew", r"lock[- ]in", r"minimum term"],
    },
    {
        "id": "non_compete",
        "label": "Non-compete / restraint",
        "severity": "high",
        "patterns": [r"non[- ]compete", r"restraint of trade", r"shall not .* compete"],
    },
    {
        "id": "ip_assignment",
        "label": "IP assignment / transfer",
        "severity": "high",
        "patterns": [r"assign(s|ment)? of intellectual property", r"all ip .* shall vest", r"work for hire"],
    },
]


def match_clause_flags(clause_text: str) -> list[dict[str, Any]]:
    t = clause_text.lower()
    out: list[dict[str, Any]] = []
    for r in _CLAUSE_RULES:
        for p in r["patterns"]:
            if re.search(p, t):
                out.append({"rule_id": r["id"], "label": r["label"], "severity": r["severity"]})
                break
    return out

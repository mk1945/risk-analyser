from __future__ import annotations

import re


def classify_contract_type(text: str) -> str:
    t = text.lower()

    signals = {
        "employment": [
            r"employment", r"employee", r"employer", r"salary", r"notice period", r"probation",
        ],
        "vendor": [r"vendor", r"purchase order", r"supply", r"deliverables", r"invoice"],
        "lease": [r"lease", r"lessor", r"lessee", r"rent", r"security deposit", r"premises"],
        "partnership": [r"partnership", r"partner", r"profit sharing", r"capital contribution"],
        "service": [r"services", r"service levels", r"sla", r"statement of work", r"scope of work"],
    }

    scores: dict[str, int] = {k: 0 for k in signals}
    for kind, pats in signals.items():
        for p in pats:
            if re.search(p, t):
                scores[kind] += 1

    best = max(scores.items(), key=lambda kv: kv[1])
    return best[0] if best[1] > 0 else "unknown"

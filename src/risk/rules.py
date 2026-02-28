from __future__ import annotations

import re
from typing import Any

from src.risk.compliance import run_compliance_checks


_RULES = [
    {
        "id": "penalty",
        "label": "Penalty / Liquidated damages",
        "severity": "high",
        "patterns": [
            r"liquidated damages",
            r"penalt(y|ies)",
            r"late fee",
            r"interest at .*%",
            r"(?i)\b(?:damages|penalty)\b",
            r"(?i)दंड|जुर्माना|क्षतिपूर्ति",
            r"(?i)அபராதம்|தாமதக் கட்டணம்|இழப்பீடு",
        ],
    },
    {
        "id": "indemnity",
        "label": "Broad indemnity",
        "severity": "high",
        "patterns": [r"indemnif(y|ies)", r"hold harmless", r"(?i)क्षतिपूर्ति|हानिपूर्ति", r"(?i)இழப்பீடு ஈடு|பாதுகாப்பளித்தல்"],
    },
    {
        "id": "unilateral_termination",
        "label": "Unilateral termination",
        "severity": "high",
        "patterns": [
            r"terminate .* without cause",
            r"at any time .* terminate",
            r"sole discretion",
            r"(?i)किसी भी समय.*समाप्त",
            r"(?i)எந்த நேரத்திலும்.*ரத்து",
        ],
    },
    {
        "id": "arbitration_jurisdiction",
        "label": "Arbitration / Jurisdiction constraints",
        "severity": "medium",
        "patterns": [
            r"arbitration",
            r"seat of arbitration",
            r"exclusive jurisdiction",
            r"courts at",
            r"(?i)मध्यस्थता|पंचाट|क्षेत्राधिकार|अधिकार क्षेत्र",
            r"(?i)நடுவர்|நீதிமன்ற வரம்பு|ஆளுகை எல்லை",
        ],
    },
    {
        "id": "auto_renew_lockin",
        "label": "Auto-renewal / Lock-in",
        "severity": "medium",
        "patterns": [
            r"auto[- ]renew",
            r"automatically renew",
            r"lock[- ]in",
            r"minimum term",
            r"(?i)स्वतः.*नवीनीकरण|लॉक[- ]?इन|न्यूनतम अवधि",
            r"(?i)தானாகப் புதுப்பித்தல்|குறைந்தபட்ச காலம்",
        ],
    },
    {
        "id": "non_compete",
        "label": "Non-compete / restraint",
        "severity": "high",
        "patterns": [r"non[- ]compete", r"restraint of trade", r"shall not .* compete", r"(?i)प्रतिस्पर्धा.*नहीं", r"(?i)போட்டியிடக் கூடாது"],
    },
    {
        "id": "ip_assignment",
        "label": "IP assignment / transfer",
        "severity": "high",
        "patterns": [
            r"assign(s|ment)? of intellectual property",
            r"all ip .* shall vest",
            r"work for hire",
            r"(?i)बौद्धिक संपदा|आईपी.*हस्तांतरण|स्वामित्व.*स्थानांतर",
            r"(?i)அறிவுசார் சொத்துரிமை|உரிமை மாற்றம்",
        ],
    },
    {
        "id": "confidentiality",
        "label": "Confidentiality / NDA",
        "severity": "low",
        "patterns": [r"confidential", r"nda", r"non[- ]disclosure", r"(?i)गोपनीय|गैर प्रकटीकरण", r"(?i)ரகசியமானது|வெளிப்படுத்தாமை"],
    },
]


def score_contract(*, doc_text: str, clauses: list[dict[str, Any]], contract_type: str, lang: str) -> dict[str, Any]:
    t = doc_text.lower()
    clause_flags: list[dict[str, Any]] = []

    high = 0
    medium = 0
    low = 0

    for rule in _RULES:
        matched = False
        for p in rule["patterns"]:
            if re.search(p, t):
                matched = True
                break
        if not matched:
            continue

        if rule["severity"] == "high":
            high += 1
        elif rule["severity"] == "medium":
            medium += 1
        else:
            low += 1

        clause_flags.append({"rule_id": rule["id"], "label": rule["label"], "severity": rule["severity"]})

    composite = _composite_score(high=high, medium=medium, low=low, contract_type=contract_type)

    summary_plain = _plain_summary(contract_type=contract_type, composite=composite, high=high, medium=medium)

    return {
        "contract_type": contract_type,
        "clause_level": "computed in clause explanations",
        "contract_risk": composite,
        "high_flags": high,
        "medium_flags": medium,
        "low_flags": low,
        "matched_flags": clause_flags,
        "summary_plain": summary_plain,
        "risk_mitigation": _mitigation_suggestions(clause_flags),
        "compliance_checks": run_compliance_checks(doc_text=doc_text, contract_type=contract_type, lang=lang),
        "unfavorable_terms": _unfavorable_terms(clause_flags),
    }


def _composite_score(*, high: int, medium: int, low: int, contract_type: str) -> dict[str, Any]:
    # Simple weighted scoring; adjust later.
    score = high * 25 + medium * 12 + low * 4
    score = max(0, min(100, score))

    if score >= 60:
        level = "High"
    elif score >= 30:
        level = "Medium"
    else:
        level = "Low"

    return {"score": score, "level": level}


def _plain_summary(*, contract_type: str, composite: dict[str, Any], high: int, medium: int) -> str:
    return (
        f"Contract type: {contract_type}. Overall risk: {composite['level']} (score {composite['score']}/100). "
        f"Key risk signals found: {high} high-risk and {medium} medium-risk themes. "
        "Review highlighted clauses and consider renegotiation for high-risk items."
    )


def _mitigation_suggestions(flags: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for f in flags:
        rid = f["rule_id"]
        if rid == "indemnity":
            out.append("Narrow indemnity to third-party claims, cap liability, exclude indirect/consequential loss.")
        if rid == "penalty":
            out.append("Replace penalties with reasonable liquidated damages tied to actual loss and add cure periods.")
        if rid == "unilateral_termination":
            out.append("Ask for mutual termination rights, notice periods, and compensation for committed costs.")
        if rid == "auto_renew_lockin":
            out.append("Add opt-out notice window, reduce lock-in, and add early-exit fees only if reasonable.")
        if rid == "ip_assignment":
            out.append("Clarify IP ownership: pre-existing IP remains with owner; grant limited license for use.")
        if rid == "non_compete":
            out.append("Limit non-compete scope/duration/territory; prefer non-solicit + confidentiality instead.")
    return _uniq(out)


def _unfavorable_terms(flags: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """High-level unfavorable term themes derived from matched flags."""
    ranked = {"high": 3, "medium": 2, "low": 1}
    out: list[dict[str, Any]] = []
    for f in flags:
        out.append(
            {
                "theme": f.get("label"),
                "severity": f.get("severity"),
                "why_it_matters": _why_it_matters(f.get("rule_id")),
            }
        )
    out.sort(key=lambda x: ranked.get(str(x.get("severity")), 0), reverse=True)
    return out[:20]


def _why_it_matters(rule_id: str | None) -> str:
    if rule_id == "indemnity":
        return "Indemnities can create open-ended liability; SMEs usually need caps and clear scope."
    if rule_id == "penalty":
        return "Penalty/interest clauses can quickly escalate costs; prefer reasonable, measurable remedies."
    if rule_id == "unilateral_termination":
        return "One-sided termination can strand investments and staff; seek notice and cost recovery."
    if rule_id == "auto_renew_lockin":
        return "Auto-renewal/lock-in can trap cashflow; ensure opt-out windows and fair exit terms."
    if rule_id == "arbitration_jurisdiction":
        return "Unfavorable seat/jurisdiction can raise cost and delay; choose neutral and predictable forum."
    if rule_id == "non_compete":
        return "Broad restraints can block future business; limit to reasonable confidentiality/non-solicit."
    if rule_id == "ip_assignment":
        return "IP transfer can unintentionally give away core know-how; separate pre-existing vs created IP."
    return "Review scope, exceptions, and business impact."


def _uniq(items: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for i in items:
        key = i.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(i.strip())
    return out

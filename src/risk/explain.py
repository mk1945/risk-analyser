from __future__ import annotations

import re
from typing import Any

from src.risk.rule_helpers import match_clause_flags
from src.llm.llm_stub import maybe_llm_enhance_clause
from src.audit.redaction import redact_text


def build_plain_explanations(
    *,
    clauses: list[dict[str, Any]],
    contract_type: str,
    lang: str,
    llm_enabled: bool,
    llm_provider: str,
    redact_before_llm: bool,
    entities: dict[str, Any],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    for c in clauses:
        flags = match_clause_flags(c["text"])
        risk_level = _risk_level(flags)

        explanation = _plain_explain_clause(c["title"], c["text"], flags, contract_type)
        alternatives = _suggest_alternatives(flags)

        enhanced = None
        if llm_enabled:
            text_for_llm = redact_text(c["text"], entities) if redact_before_llm else c["text"]
            enhanced = maybe_llm_enhance_clause(
                clause_title=c["title"],
                clause_text=text_for_llm,
                contract_type=contract_type,
                provider=llm_provider,
                lang=lang,
                flags=flags,
            )

        out.append(
            {
                "id": c["id"],
                "title": c["title"],
                "text": c["text"],
                "flags": flags,
                "risk": risk_level,
                "explanation_plain": enhanced or explanation,
                "suggested_alternatives": alternatives,
            }
        )

    return out


def _plain_explain_clause(title: str, text: str, flags: list[dict[str, Any]], contract_type: str) -> str:
    base = f"This clause is about: {title}. "

    if not flags:
        return base + "No obvious red flags detected by the rule-based checker. Read for scope, timelines, and exceptions."

    themes = ", ".join(f["label"] for f in flags[:4])
    return (
        base
        + f"Potential risk themes detected: {themes}. "
        + "If this is one-sided, ask for caps, clear timelines, cure periods, and mutual rights."
    )


def _risk_level(flags: list[dict[str, Any]]) -> str:
    sev = {f["severity"] for f in flags}
    if "high" in sev:
        return "High"
    if "medium" in sev:
        return "Medium"
    if "low" in sev:
        return "Low"
    return "Low"


def _suggest_alternatives(flags: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for f in flags:
        rid = f["rule_id"]
        if rid == "indemnity":
            out.append("Indemnity limited to third-party claims; liability capped at fees paid in last 3–12 months.")
        if rid == "penalty":
            out.append("Replace penalty with reasonable liquidated damages and add a 15–30 day cure period.")
        if rid == "unilateral_termination":
            out.append("Mutual termination with 30 days' notice; reimburse committed costs if terminated for convenience.")
        if rid == "arbitration_jurisdiction":
            out.append("Choose a neutral seat and non-exclusive jurisdiction; add escalation/mediation before arbitration.")
        if rid == "auto_renew_lockin":
            out.append("Auto-renew only with written consent; clear opt-out window (e.g., 30–60 days).")
        if rid == "non_compete":
            out.append("Use confidentiality + non-solicit instead of broad non-compete; limit duration/territory.")
        if rid == "ip_assignment":
            out.append("Pre-existing IP remains with owner; customer gets limited license for internal use.")

    return _uniq(out)


def _uniq(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        k = re.sub(r"\s+", " ", x).strip().lower()
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(x.strip())
    return out

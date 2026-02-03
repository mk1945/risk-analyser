from __future__ import annotations

from typing import Any

from langdetect import detect

from src.nlp.sectioning import extract_clauses
from src.nlp.entities import extract_entities
from src.nlp.semantics import extract_obligation_right_prohibition
from src.nlp.ambiguity import detect_ambiguities
from src.nlp.similarity import match_to_templates
from src.risk.rules import score_contract
from src.risk.classify import classify_contract_type
from src.risk.explain import build_plain_explanations
from src.kb.knowledge_base import update_kb


def _detect_language(doc_text: str, lang_hint: str) -> str:
    if lang_hint == "English":
        return "en"
    if lang_hint == "Hindi":
        return "hi"
    try:
        code = detect(doc_text[:2000])
    except Exception:
        code = "en"
    return "hi" if code.startswith("hi") else "en"


def analyze_contract(
    *,
    doc_text: str,
    filename: str,
    lang_hint: str,
    llm_enabled: bool,
    llm_provider: str,
    redact_before_llm: bool,
) -> dict[str, Any]:
    lang = _detect_language(doc_text, lang_hint)
    clauses = extract_clauses(doc_text)
    entities = extract_entities(doc_text, lang=lang)
    contract_type = classify_contract_type(doc_text)

    semantics = extract_obligation_right_prohibition(clauses=clauses, lang=lang)
    ambiguity = detect_ambiguities(clauses=clauses, lang=lang)
    template_matches = match_to_templates(clauses=clauses, contract_type=contract_type)

    risk = score_contract(doc_text=doc_text, clauses=clauses, contract_type=contract_type, lang=lang)
    clauses_with_explanations = build_plain_explanations(
        clauses=clauses,
        contract_type=contract_type,
        lang=lang,
        llm_enabled=llm_enabled,
        llm_provider=llm_provider,
        redact_before_llm=redact_before_llm,
        entities=entities,
    )

    # Merge additional signals into per-clause output (preserve order).
    for c in clauses_with_explanations:
        cid = str(c.get("id"))
        c["semantic_roles"] = semantics.get(cid, {"obligations": [], "rights": [], "prohibitions": []})
        c["ambiguity_flags"] = ambiguity.get(cid, [])
        c["template_match"] = template_matches.get(cid, {"available": False})

    plain_summary = risk["summary_plain"]

    result: dict[str, Any] = {
        "filename": filename,
        "language": lang,
        "contract_type": contract_type,
        "risk_summary": risk,
        "entities": entities,
        "plain_summary": plain_summary,
        "clauses": clauses_with_explanations,
        "unfavorable_terms": risk.get("unfavorable_terms", []),
        "generated_templates": risk.get("generated_templates", []),
        "risk_mitigation": risk.get("risk_mitigation", []),
        "disclaimer": "Not legal advice. Use this report to prepare for a licensed advocate review.",
    }

    update_kb(result)
    return result

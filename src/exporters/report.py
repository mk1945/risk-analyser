from __future__ import annotations

from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


def build_report_pdf(*, result: dict[str, Any], out_path: str) -> None:
    doc = SimpleDocTemplate(out_path, pagesize=A4)
    styles = getSampleStyleSheet()

    story = []
    story.append(Paragraph("Contract Analysis Report (GiviAI)", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"File: {result.get('filename','')}", styles["Normal"]))
    story.append(Paragraph(f"Type: {result.get('contract_type','')}", styles["Normal"]))
    risk = result.get("risk_summary", {}).get("contract_risk", {})
    story.append(Paragraph(f"Overall Risk: {risk.get('level','')} ({risk.get('score','')}/100)", styles["Normal"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Summary", styles["Heading2"]))
    story.append(Paragraph(result.get("plain_summary", ""), styles["BodyText"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Risk Mitigation", styles["Heading2"]))
    for s in result.get("risk_mitigation", [])[:20]:
        story.append(Paragraph(f"• {s}", styles["BodyText"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Unfavorable Terms (Themes)", styles["Heading2"]))
    for t in result.get("unfavorable_terms", [])[:20]:
        theme = t.get("theme", "")
        sev = t.get("severity", "")
        why = t.get("why_it_matters", "")
        story.append(Paragraph(f"• [{sev}] {theme} — {why}", styles["BodyText"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Compliance Checklist (Heuristic)", styles["Heading2"]))
    for c in result.get("risk_summary", {}).get("compliance_checks", [])[:30]:
        story.append(
            Paragraph(
                f"• [{c.get('status','')}] {c.get('topic','')}: {c.get('note','')}",
                styles["BodyText"],
            )
        )
    story.append(Spacer(1, 10))

    story.append(Paragraph("Clause Highlights", styles["Heading2"]))
    for c in result.get("clauses", [])[:50]:
        story.append(Paragraph(f"{c.get('id','')} — {c.get('title','')}", styles["Heading3"]))
        story.append(Paragraph(f"Risk: {c.get('risk','')}", styles["Normal"]))
        tm = c.get("template_match") or {}
        if tm.get("available"):
            story.append(
                Paragraph(
                    f"Template match: {tm.get('template_title','')} (score {tm.get('score','')})",
                    styles["Normal"],
                )
            )
        amb = c.get("ambiguity_flags") or []
        if amb:
            story.append(Paragraph("Ambiguity signals: " + ", ".join(a.get("term", "") for a in amb[:6]), styles["Normal"]))
        story.append(Paragraph(c.get("explanation_plain", ""), styles["BodyText"]))
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 12))
    story.append(Paragraph(result.get("disclaimer", ""), styles["Italic"]))

    doc.build(story)

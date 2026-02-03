from __future__ import annotations

import re
from typing import Any


def run_compliance_checks(*, doc_text: str, contract_type: str, lang: str) -> list[dict[str, Any]]:
    """Local, non-authoritative compliance checklist for Indian SMEs.

    Restrictions:
    - No external legal databases or statute text.
    - This is a best-effort heuristic checklist to help identify missing/unclear clauses.

    Output schema:
    - id: stable identifier
    - topic: what is being checked
    - status: "ok" | "flag" | "info"
    - note: plain-language guidance
    """

    t = doc_text.lower()
    checks: list[dict[str, Any]] = []

    def has(p: str) -> bool:
        return re.search(p, t) is not None

    def add(check_id: str, topic: str, status: str, note: str) -> None:
        checks.append({"id": check_id, "topic": topic, "status": status, "note": note})

    # Cross-cutting basics
    add(
        "governing_law",
        "Governing law / jurisdiction",
        "ok" if has(r"governing law|jurisdiction|courts at|seat of arbitration|arbitration") else "flag",
        "Specify governing law and dispute forum (and escalation steps) to reduce uncertainty and costs.",
    )

    add(
        "confidentiality",
        "Confidentiality / NDA",
        "ok" if has(r"confidential|non[- ]disclosure|nda|गोपनीय|गैर प्रकटीकरण") else "flag",
        "Add confidentiality scope, permitted disclosures, duration, and return/destruction obligations.",
    )

    add(
        "liability_cap",
        "Limitation of liability",
        "ok" if has(r"limit(ation)? of liability|liability shall not exceed|cap on liability") else "flag",
        "SMEs typically need a clear liability cap (fees paid / specific amount) and exclusions for indirect loss.",
    )

    add(
        "termination_notice",
        "Termination + notice period",
        "ok" if has(r"termination|terminate|notice period|notice of") else "flag",
        "Ensure termination grounds, notice, cure periods, and final settlement/hand-over steps are written.",
    )

    add(
        "payment_terms",
        "Payment terms",
        "ok" if has(r"payment|invoice|fees|consideration|due within|net \d+") else "flag",
        "Clarify pricing, invoicing, due dates, taxes (e.g., GST if relevant), and late payment consequences.",
    )

    # Type-specific checks
    if contract_type == "employment" or has(r"employee|employment|employer|salary|probation"):
        add(
            "employment_role",
            "Role, location, working arrangements",
            "ok" if has(r"designation|role|duties|place of work|work from") else "flag",
            "Define role, reporting, work location/remote policy, and key responsibilities.",
        )
        add(
            "employment_comp",
            "Compensation structure",
            "ok" if has(r"ctc|salary|gross|basic|allowance|bonus") else "flag",
            "Break down pay components and payment schedule; clarify reimbursements and deductions.",
        )
        add(
            "employment_ip",
            "IP + inventions",
            "ok" if has(r"intellectual property|inventions|work product|assign") else "flag",
            "Clarify ownership of employee-created work; carve out pre-existing IP and personal tools.",
        )
        add(
            "employment_noncompete",
            "Post-employment non-compete risk",
            "flag" if has(r"non[- ]compete|restraint of trade|shall not .* compete|प्रतिस्पर्धा.*नहीं") else "ok",
            "Broad restraints can be risky and hard to enforce; prefer confidentiality + non-solicit and reasonable limits.",
        )

    if contract_type == "lease" or has(r"lease|lessor|lessee|rent|premises"):
        add(
            "lease_premises",
            "Premises description + permitted use",
            "ok" if has(r"premises|address|carpet area|built[- ]up|use of the premises") else "flag",
            "Document premises details, permitted use, common areas, and any restrictions.",
        )
        add(
            "lease_deposit",
            "Security deposit + refunds",
            "ok" if has(r"security deposit|deposit") else "flag",
            "State deposit amount, deductions rules, interest (if any), and refund timeline.",
        )
        add(
            "lease_maintenance",
            "Maintenance + repairs allocation",
            "ok" if has(r"maintenance|repairs|fit[- ]out") else "flag",
            "Clearly allocate who pays for maintenance, utilities, and structural vs minor repairs.",
        )
        add(
            "lease_registration",
            "Registration / stamp duty (commercial practicality)",
            "info" if not has(r"stamp duty|registration") else "ok",
            "Consider mentioning responsibility for registration/stamp duty where applicable (commercial expectation in India).",
        )

    if contract_type in {"vendor", "service"} or has(r"vendor|purchase order|supply|services|sla|statement of work"):
        add(
            "scope_deliverables",
            "Scope + deliverables + acceptance criteria",
            "ok" if has(r"deliverables|scope of work|statement of work|acceptance|milestone|service levels|sla") else "flag",
            "Define deliverables, acceptance tests, timelines, and what happens if acceptance is delayed.",
        )
        add(
            "indemnity_scope",
            "Indemnity scope",
            "flag" if has(r"indemnif(y|ies)|hold harmless|क्षतिपूर्ति|हानिपूर्ति") else "info",
            "If indemnity exists, ensure it's limited (third-party claims), capped, and excludes indirect losses.",
        )
        add(
            "data_handling",
            "Data handling + security (if applicable)",
            "info" if not has(r"data|personal data|security|breach|encrypt") else "ok",
            "If any data is processed, add security controls, breach notice timelines, and deletion/return obligations.",
        )

    if contract_type == "partnership" or has(r"partnership|partner|profit sharing|capital contribution"):
        add(
            "partners_capital",
            "Capital contribution + drawings",
            "ok" if has(r"capital contribution|capital|drawings") else "flag",
            "Specify initial capital, future contributions, drawings, and what happens if a partner defaults.",
        )
        add(
            "partners_profit",
            "Profit/loss sharing",
            "ok" if has(r"profit sharing|profit and loss|ratio") else "flag",
            "Write the sharing ratio and how profits are calculated and distributed.",
        )
        add(
            "partners_exit",
            "Exit + retirement + expulsion",
            "ok" if has(r"retire|retirement|expel|expulsion|exit|buyout") else "flag",
            "Define exit triggers, valuation/buyout method, and handover of responsibilities.",
        )

    return checks

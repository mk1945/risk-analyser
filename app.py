import os
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import streamlit as st

from src.ingest.loaders import load_document
from src.nlp.pipeline import analyze_contract
from src.exporters.report import build_report_pdf
from src.audit.audit_log import write_audit_event

APP_NAME = "GiviAI — SME Contract Risk Assistant"


_THEME_CSS = """
<style>
    :root {
        --bg: #f8fafc;
        --panel: #ffffff;
        --panel2: #ffffff;
        --text: #0f172a;
        --muted: #64748b;
        --border: #e2e8f0;
        --accent: #7c3aed;
        --accent2: #22c55e;
        --warn: #f59e0b;
        --bad: #ef4444;
    }

    .stApp {
        background: radial-gradient(circle at 10% 0%, rgba(124,58,237,0.08), transparent 40%),
                                radial-gradient(circle at 90% 10%, rgba(34,197,94,0.08), transparent 40%),
                                var(--bg);
        color: var(--text);
    }

    /* Global text */
    .stApp, .stApp p, .stApp li, .stApp span, .stApp div {
        color: var(--text);
    }
    .stApp a { color: #6d28d9; }
    .stApp a:hover { color: #5b21b6; }
    .stCaption, [data-testid="stCaptionContainer"], .muted { color: var(--muted) !important; }

    /* Labels */
    label, [data-testid="stWidgetLabel"], .stMarkdown label {
        color: #334155 !important;
        font-weight: 500;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #334155 !important;
    }

    /* Cards/Containers */
    section.main [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--border);
        background: var(--panel);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(148, 163, 184, 0.08);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #f1f5f9;
        border-right: 1px solid var(--border);
    }

    /* Inputs (BaseWeb) */
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea {
        color: var(--text) !important;
        background-color: #ffffff !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text) !important;
    }
    div[data-baseweb="select"] span { color: var(--text) !important; }
    div[data-baseweb="menu"] * { color: var(--text) !important; }

    /* Radio/checkbox */
    [role="radiogroup"] label, [data-testid="stCheckbox"] label {
        color: var(--text) !important;
    }

    /* Headings */
    h1, h2, h3, h4 {
        letter-spacing: -0.02em;
        color: #1e293b;
        font-weight: 700;
    }

    .muted { color: var(--muted); }
    .pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        border: 1px solid var(--border);
        background: #f8fafc;
        color: #475569;
        font-size: 13px;
        font-weight: 500;
        margin-right: 8px;
        margin-bottom: 6px;
    }
    .pill.ok { 
        background-color: #f0fdf4;
        border-color: #bbf7d0;
        color: #166534;
    }
    .pill.warn { 
        background-color: #fffbeb;
        border-color: #fde68a;
        color: #92400e;
    }
    .pill.bad { 
        background-color: #fef2f2;
        border-color: #fecaca;
        color: #991b1b;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 12px;
        border: 1px solid var(--border);
        background-color: #ffffff;
        color: var(--text);
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        font-weight: 600;
    }
    .stButton > button:hover {
        border-color: #cbd5e1;
        background-color: #f8fafc;
        color: var(--accent);
    }
    /* Primary button override */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25);
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 16px rgba(124, 58, 237, 0.35);
        color: white;
    }

    .stDownloadButton > button {
        border-radius: 12px;
        border: 1px solid var(--border);
        background-color: #ffffff;
        color: var(--text);
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }

    /* Expanders */
    details {
        border-radius: 14px;
        border: 1px solid var(--border);
        background: #ffffff;
        padding: 8px 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    summary, summary * { color: var(--text) !important; font-weight: 600; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px;
        color: var(--muted);
        font-size: 16px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent) !important;
        font-weight: 700;
    }

    /* Reduce whitespace a bit */
    .block-container { padding-top: 2rem; }
    
    /* Code blocks */
    code {
        color: #d946ef !important;
        background: #fdf4ff !important;
    }
    .stCodeBlock {
        border: 1px solid var(--border);
        border-radius: 12px;
    }

    /* MOBILE RESPONSIVENESS */
    @media (max-width: 640px) {
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        section.main [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
            padding: 12px;
            border-radius: 12px;
        }
        
        h1 { font-size: 1.75rem !important; }
        h2 { font-size: 1.5rem !important; }
        h3 { font-size: 1.25rem !important; }

        .stTabs [data-baseweb="tab"] {
            font-size: 14px;
            padding: 8px 12px;
        }
        
        /* Make buttons take full width on mobile if needed, or just larger touch target */
        .stButton > button {
            min-height: 44px;
        }
    }
</style>
"""


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _severity_box(level: str):
    lvl = (level or "").strip().lower()
    if lvl.startswith("high"):
        return st.error
    if lvl.startswith("medium"):
        return st.warning
    return st.info


def _bullets(items: list[str]) -> str:
    if not items:
        return ""
    return "\n".join([f"- {x}" for x in items])


def _ensure_dirs() -> None:
    Path("outputs").mkdir(exist_ok=True)
    Path("audit_logs").mkdir(exist_ok=True)


def _pill(level: str) -> str:
    lvl = (level or "").strip().lower()
    cls = "ok"
    if lvl.startswith("high"):
        cls = "bad"
    elif lvl.startswith("medium"):
        cls = "warn"
    label = level.title() if level else ""
    return f"<span class='pill {cls}'>Risk: {label}</span>"


def _safe_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def main() -> None:
    st.set_page_config(page_title=APP_NAME, layout="wide")
    st.markdown(_THEME_CSS, unsafe_allow_html=True)
    _ensure_dirs()

    st.title(APP_NAME)
    st.markdown(
        "<span class='pill ok'>Local-first</span><span class='pill'>English + Hindi</span><span class='pill'>Audit logs</span>",
        unsafe_allow_html=True,
    )
    st.caption("Confidential contract analysis for Indian SMEs (no external calls unless you turn on LLM mode).")

    with st.sidebar:
        st.header("Input")
        input_mode = st.radio("How do you want to input the contract?", ["Upload file", "Paste text"], index=0)
        uploaded = None
        pasted_text = ""
        if input_mode == "Upload file":
            uploaded = st.file_uploader("Upload contract", type=["pdf", "doc", "docx", "txt"])
        else:
            pasted_text = st.text_area(
                "Paste contract text",
                height=220,
                placeholder="Paste the contract text here...",
            )

        lang_hint = st.selectbox("Language hint", ["Auto", "English", "Hindi"], index=0)

        st.divider()
        st.header("Privacy")
        redact_before_llm = st.checkbox("Redact sensitive fields before LLM", value=True)

        st.divider()
        st.header("LLM (optional)")
        st.write("Default: OFF (no external calls).")
        llm_enabled = st.checkbox("Enable LLM-enhanced explanations", value=False)
        llm_provider = st.selectbox("Provider", ["GPT-4", "Claude 3"], index=0)

        st.divider()
        run_btn = st.button("Analyze", type="primary", use_container_width=True)

        st.divider()
        st.header("Advanced")
        show_raw = st.checkbox("Show raw JSON / extracted text", value=False)
    if input_mode == "Upload file" and not uploaded:
        st.info("Upload a contract to begin.")
        return
    if input_mode == "Paste text" and not pasted_text.strip():
        st.info("Paste contract text to begin.")
        return

    if not run_btn:
        st.stop()

    request_id = str(uuid.uuid4())
    started_at = _now_utc_iso()

    write_audit_event(
        request_id=request_id,
        event_type="analysis_started",
        payload={
            "filename": uploaded.name if uploaded else "pasted_text.txt",
            "size": uploaded.size if uploaded else len(pasted_text.encode("utf-8")),
            "lang_hint": lang_hint,
            "llm_enabled": llm_enabled,
            "llm_provider": llm_provider,
            "redact_before_llm": redact_before_llm,
            "started_at": started_at,
        },
    )

    doc_text = ""
    filename = ""

    if input_mode == "Upload file":
        try:
            with st.spinner("Parsing document..."):
                doc = load_document(uploaded.name, uploaded.getvalue())
            doc_text = doc.text
            filename = uploaded.name
        except Exception as e:
            st.error(str(e))
            write_audit_event(
                request_id=request_id,
                event_type="analysis_failed",
                payload={"error": str(e)},
            )
            return
    else:
        doc_text = pasted_text.strip()
        filename = "pasted_text.txt"

    with st.spinner("Running extraction + risk checks..."):
        result = analyze_contract(
            doc_text=doc_text,
            filename=filename,
            lang_hint=lang_hint,
            llm_enabled=llm_enabled,
            llm_provider=llm_provider,
            redact_before_llm=redact_before_llm,
        )

    write_audit_event(
        request_id=request_id,
        event_type="analysis_completed",
        payload={
            "contract_type": result["contract_type"],
            "risk": result["risk_summary"],
            "completed_at": _now_utc_iso(),
        },
    )

    st.success("Analysis completed")

    tabs = st.tabs(["Overview", "Clauses", "Templates", "Exports", "Audit"])


    with tabs[0]:
        left, right = st.columns([0.62, 0.38])

        with left:
            st.subheader("Executive summary")
            st.write(result.get("plain_summary", ""))

            overall = result.get("risk_summary", {}).get("contract_risk", {}) or {}
            level = str(overall.get("level", ""))
            score = _safe_int(overall.get("score", 0), 0)

            m1, m2, m3 = st.columns(3)
            m1.metric("Contract type", str(result.get("contract_type", "")))
            m2.metric("Overall risk", level)
            m3.metric("Risk score", f"{score}/100")
            st.progress(min(max(score, 0), 100) / 100.0)

            st.subheader("Top risk themes")
            terms = result.get("unfavorable_terms", []) or []
            if terms:
                for t in terms[:10]:
                    sev = str(t.get("severity", ""))
                    theme = str(t.get("theme", ""))
                    why = str(t.get("why_it_matters", ""))
                    _severity_box(sev)(f"{sev.title()} — {theme}")
                    if why:
                        st.caption(why)
            else:
                st.info("No obvious red flags detected by the rule-based scanner.")

            st.subheader("What to ask for (risk mitigation)")
            mitigations = result.get("risk_mitigation", []) or []
            st.markdown(_bullets(mitigations[:14]) or "(none)")

        with right:
            st.subheader("Key entities")
            ent = result.get("entities", {}) or {}
            st.markdown("**Parties**")
            st.markdown(_bullets(ent.get("parties", [])[:10]) or "(not detected)")
            st.markdown("**Dates**")
            st.markdown(_bullets(ent.get("dates", [])[:10]) or "(not detected)")
            st.markdown("**Amounts**")
            st.markdown(_bullets(ent.get("amounts", [])[:10]) or "(not detected)")
            st.markdown("**Jurisdiction / forum lines**")
            st.markdown(_bullets(ent.get("jurisdiction", [])[:6]) or "(not detected)")

            st.subheader("Compliance checklist")
            checks = result.get("risk_summary", {}).get("compliance_checks", []) or []
            flagged = [c for c in checks if str(c.get("status")) == "flag"]
            if flagged:
                st.warning(f"{len(flagged)} items need attention")
                for c in flagged[:10]:
                    st.write(f"- {c.get('topic')}: {c.get('note')}")
            else:
                st.info("No major missing-clause signals detected.")

            if show_raw:
                st.markdown("**Raw entities JSON**")
                st.json(ent, expanded=False)
                st.markdown("**Raw compliance JSON**")
                st.json(checks, expanded=False)

    with tabs[1]:
        st.subheader("Clause-by-clause review")
        st.caption("Search, filter by risk, and review suggested alternatives.")

        clauses = result.get("clauses", []) or []
        q = st.text_input("Search clauses", value="", placeholder="e.g., termination, indemnity, penalty, rent...")
        risk_filter = st.multiselect("Risk level", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])

        def _matches(c: dict[str, Any]) -> bool:
            if str(c.get("risk", "")) not in set(risk_filter):
                return False
            if not q.strip():
                return True
            s = (str(c.get("title", "")) + "\n" + str(c.get("text", "")) + "\n" + str(c.get("explanation_plain", ""))).lower()
            return q.strip().lower() in s

        # High-risk first
        order = {"High": 0, "Medium": 1, "Low": 2}
        filtered = [c for c in clauses if _matches(c)]
        filtered.sort(key=lambda c: order.get(str(c.get("risk", "Low")), 9))

        st.write(f"Showing {len(filtered)} of {len(clauses)} clauses")

        for clause in filtered:
            title = f"{clause.get('id','')} — {clause.get('title','')}"
            risk_level = str(clause.get("risk", ""))
            with st.expander(title, expanded=False):
                st.markdown(_pill(risk_level), unsafe_allow_html=True)
                st.markdown("**What it means (plain language)**")
                st.write(clause.get("explanation_plain", ""))

                flags = clause.get("flags", []) or []
                if flags:
                    st.markdown("**Why it may be risky**")
                    st.markdown(_bullets([f"{f.get('label')} ({f.get('severity')})" for f in flags[:10]]))

                tm = clause.get("template_match") or {}
                if tm.get("available"):
                    st.markdown("**SME-friendly template comparison**")
                    st.write(f"Closest template clause: {tm.get('template_title')} (similarity {tm.get('score')})")

                sem = clause.get("semantic_roles") or {}
                if sem and (sem.get("obligations") or sem.get("rights") or sem.get("prohibitions")):
                    st.markdown("**Key obligations / rights / prohibitions**")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown("**Obligations**")
                        st.markdown(_bullets(sem.get("obligations", [])[:8]) or "(none)")
                    with c2:
                        st.markdown("**Rights**")
                        st.markdown(_bullets(sem.get("rights", [])[:8]) or "(none)")
                    with c3:
                        st.markdown("**Prohibitions**")
                        st.markdown(_bullets(sem.get("prohibitions", [])[:8]) or "(none)")

                amb = clause.get("ambiguity_flags") or []
                if amb:
                    st.markdown("**Ambiguity to clarify**")
                    st.markdown(_bullets([f"{a.get('term')}: {a.get('evidence')}" for a in amb[:8]]))

                st.markdown("**Suggested renegotiation alternatives**")
                st.markdown(_bullets(clause.get("suggested_alternatives", [])[:10]) or "(none)")

                if show_raw:
                    st.markdown("**Extracted text (raw)**")
                    st.code(clause.get("text", ""), language="text")
                    st.markdown("**Raw clause JSON**")
                    st.json(clause, expanded=False)

    with tabs[2]:
        st.subheader("Standard SME-friendly templates")
        st.caption("Use these as starting points; customize with a licensed advocate for your business.")

        tmpl_dir = Path("data") / "templates"
        available = sorted([p for p in tmpl_dir.glob("*.md")]) if tmpl_dir.exists() else []
        if not available:
            st.info("No templates found.")
        else:
            for p in available:
                with st.expander(p.stem.replace("_", " ").title(), expanded=False):
                    st.download_button(
                        "Download template (Markdown)",
                        data=p.read_bytes(),
                        file_name=p.name,
                        mime="text/markdown",
                    )
                    if show_raw:
                        st.code(p.read_text(encoding="utf-8"), language="markdown")

    with tabs[3]:
        st.subheader("Exports")
        st.caption("Share with your advocate for review (not legal advice).")

        json_bytes = json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8")
        st.download_button("Download JSON", data=json_bytes, file_name=f"{request_id}.json")

        pdf_path = Path("outputs") / f"{request_id}.pdf"
        build_report_pdf(result=result, out_path=str(pdf_path))
        st.download_button("Download PDF report", data=pdf_path.read_bytes(), file_name=pdf_path.name)

    with tabs[4]:
        st.subheader("Audit trail")
        st.caption("Local JSONL audit log is written for every analysis.")
        audit_path = Path("audit_logs") / f"{request_id}.jsonl"
        if audit_path.exists():
            st.download_button("Download audit log", data=audit_path.read_bytes(), file_name=audit_path.name)
            if show_raw:
                st.code(audit_path.read_text(encoding="utf-8"), language="json")
        else:
            st.info("Audit log file not found (unexpected).")

    if show_raw:
        st.subheader("Raw full result")
        st.json(result, expanded=False)


if __name__ == "__main__":
    main()

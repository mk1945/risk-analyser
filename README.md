# GiviAI — SME Contract Risk Assistant (Local)

Local-first GenAI-assisted contract analyzer for Indian SMEs.

## What it does (MVP)
- Upload PDF/DOCX/TXT
- Detect contract type (employment / vendor / lease / partnership / service)
- Extract clauses + key entities (parties, dates, amounts, jurisdiction)
- Flag risky clauses (penalty, indemnity, unilateral termination, arbitration/jurisdiction, auto-renewal/lock-in, non-compete, IP transfer)
- Produce clause-by-clause plain-English explanations
- Generate a summary report + PDF export
- Create audit logs (local JSON)
- Build a local knowledge base of common issues (anonymized patterns)

## Privacy / confidentiality
- Default mode runs fully locally (no external calls).
- Optional LLM mode can be enabled via env var to improve explanations and suggestions.
  If enabled, the app can redact sensitive data before sending text.

## Run
1) Create a venv
2) Install deps:

```powershell
pip install -r requirements.txt
```

3) (Optional) download spaCy model:

```powershell
python -m spacy download en_core_web_sm
```

4) Start:

```powershell
streamlit run app.py
```

## Notes
- This tool is not a substitute for a licensed advocate. Use exports for consultation.

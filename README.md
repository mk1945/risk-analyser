# GiviAI — SME Contract Risk Assistant (Local & AI-Powered)

Local-first GenAI-assisted contract analyzer for Indian SMEs with native English, Hindi, and Tamil support.

## What it does (MVP)
- Upload PDF/DOCX/TXT
- Native risk scanning in **English, Hindi, and Tamil** (No internet required)
- Detect contract type (employment / vendor / lease / partnership / service)
- Extract clauses + key entities (parties, dates, amounts, jurisdiction)
- Flag risky clauses (penalty, indemnity, unilateral termination, arbitration/jurisdiction, auto-renewal/lock-in, non-compete, IP transfer)
- Produce clause-by-clause plain-English (or Tamil/Hindi) explanations
- Optional **Google Gemini** integration for high-precision, context-aware AI risk analysis
- Generate a summary report + PDF export
- Create audit logs (local JSON)
- Build a local knowledge base of common issues (anonymized patterns)

## Privacy / confidentiality
- **Default mode runs fully locally** (no external calls). Risk analysis uses regex-based NLP.
- Optional LLM mode can be enabled to dramatically improve explanations and suggestions using the **Gemini 1.5 Flash (Free Tier)** API.
- If AI is enabled, the app can automatically redact sensitive data (names, amounts, dates) before sending text to Google's servers.

## Quickstart

1) Clone the repository and navigate to the project directory.
2) Create and activate a virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) Install dependencies:
```powershell
pip install -r requirements.txt
```

4) (Optional) Download spaCy model:
```powershell
python -m spacy download en_core_web_sm
```

5) **Optional: Enable Gemini AI Analysis**
If you want highly precise AI-generated risk context:
- Create a completely free API key at [Google AI Studio](https://aistudio.google.com/)
- Create a file named `.env` in the root of this project.
- Add your key to the file: `GEMINI_API_KEY=your-api-key-here`

6) Start the application:
```powershell
streamlit run app.py
```

## Notes
- This tool is not a substitute for a licensed advocate. Use exports for consultation before signing any documents.

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def maybe_llm_enhance_clause(
    *,
    clause_title: str,
    clause_text: str,
    contract_type: str,
    provider: str,
    lang: str,
    flags: list[dict[str, Any]],
) -> str | None:
    """Uses LLM to generate precise, context-aware risk explanations."""

    if not flags:
        return None

    # Format the flagged risks
    flag_details = "\n".join([f"- {f['label']} (Risk: {f['severity']})" for f in flags])

    sys_prompt = f"""You are an expert corporate lawyer advising a Small/Medium Enterprise (SME).
    Review the following contract clause from a {contract_type} agreement. Keep your answer under 4 sentences.
    Focus exclusively on explaining the practical risks associated with these flagged issues:
    {flag_details}
    
    Provide the explanation in {lang}. Be concise, practical, and highly precise."""

    if provider == "Gemini (Free)":
        return _call_gemini(sys_prompt, clause_text)
    
    return None


def _call_gemini(sys_prompt: str, user_text: str) -> str | None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ Gemini API key not found in environment."
        
    try:
        from google import genai
        # Initialize client using environment variable
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[sys_prompt, user_text],
            config={
                'temperature': 0.3,
                'max_output_tokens': 250
            }
        )
        return response.text
    except Exception as e:
        return f"⚠️ Gemini API Error: {str(e)}"

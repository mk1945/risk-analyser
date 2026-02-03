from __future__ import annotations

from typing import Any


def maybe_llm_enhance_clause(
    *,
    clause_title: str,
    clause_text: str,
    contract_type: str,
    provider: str,
    lang: str,
    flags: list[dict[str, Any]],
) -> str | None:
    """Stub for LLM integration.

    Tooling restrictions: no integrations by default.
    This function intentionally returns None unless you later wire in an API client.

    If you want LLM mode:
    - Add a local adapter that calls GPT-4 or Claude 3 using an API key.
    - Keep it off by default for confidentiality.
    - Prefer redaction before sending.
    """
    return None

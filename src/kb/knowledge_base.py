from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def update_kb(result: dict[str, Any]) -> None:
    """Store anonymized issue patterns for Indian SME contract KB (local).

    Stores only:
    - contract_type
    - matched flag ids
    - risk level
    - timestamp

    No raw contract text is persisted.
    """
    Path("data").mkdir(exist_ok=True)
    kb_path = Path("data") / "kb_common_issues.jsonl"

    matched = result.get("risk_summary", {}).get("matched_flags", [])
    flags = [m.get("rule_id") for m in matched if m.get("rule_id")]

    entry = {
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "contract_type": result.get("contract_type"),
        "risk_level": result.get("risk_summary", {}).get("contract_risk", {}).get("level"),
        "flags": flags,
    }

    with kb_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

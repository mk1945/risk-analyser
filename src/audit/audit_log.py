from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def write_audit_event(*, request_id: str, event_type: str, payload: dict[str, Any]) -> None:
    Path("audit_logs").mkdir(exist_ok=True)
    entry = {
        "request_id": request_id,
        "event_type": event_type,
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "payload": payload,
    }

    path = Path("audit_logs") / f"{request_id}.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

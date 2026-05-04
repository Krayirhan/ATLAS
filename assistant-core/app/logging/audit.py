"""Append-only JSONL audit log."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

_SENSITIVE_KEYS = {"password", "token", "secret", "api_key", "authorization"}


def _scrub(obj: Any) -> Any:
    if isinstance(obj, Mapping):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            if str(k).lower() in _SENSITIVE_KEYS:
                out[str(k)] = "[redacted]"
            else:
                out[str(k)] = _scrub(v)
        return out
    if isinstance(obj, list):
        return [_scrub(x) for x in obj]
    return obj


def write_audit(
    *,
    event: str,
    payload: Mapping[str, Any],
    logs_root: Path | None = None,
    stream: str = "tool-calls",
) -> Path:
    root = logs_root
    if root is None:
        from app.paths import get_logs_dir

        root = get_logs_dir()
    sub = root / stream
    sub.mkdir(parents=True, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = sub / f"{day}.jsonl"
    line = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "payload": _scrub(dict(payload)),
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")
    return path

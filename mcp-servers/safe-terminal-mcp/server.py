"""Safe-terminal MCP helper (Sprint 17): check / preview / gated run.

- No run without matching ATLAS_SAFE_TERMINAL_APPROVAL_TOKEN env + CLI token.
- Only registry-resolved commands for --type build|test|lint|status.
- Blocked / approval-required evaluation via assistant-core safety module.
- JSONL audit via app.logging.audit; optional SQLite tool_calls row.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _atlas_root() -> Path:
    env = os.environ.get("ATLAS_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


def _assistant_core() -> Path:
    return _atlas_root() / "assistant-core"


def _bootstrap_imports() -> None:
    ac = _assistant_core()
    if str(ac) not in sys.path:
        sys.path.insert(0, str(ac))


def _default_project(registry: dict) -> str | None:
    env = os.environ.get("ATLAS_SAFE_TERMINAL_PROJECT", "").strip()
    if env:
        return env
    projects = registry.get("projects") or []
    if len(projects) == 1:
        return str(projects[0].get("name") or "")
    return None


def _resolve_command(registry: dict, project: str, command_type: str) -> tuple[str, Path]:
    item = next((p for p in registry.get("projects", []) if p.get("name") == project), None)
    if not item:
        raise ValueError(f"Unknown project: {project}")
    root = Path(str(item.get("root", "")))
    key = command_type.strip().lower()
    mapping = {
        "build": (item.get("build_command") or "").strip(),
        "test": (item.get("test_command") or "").strip(),
        "lint": (item.get("lint_command") or "").strip(),
        "status": "git status",
    }
    if key not in mapping:
        raise ValueError("type must be one of: build, test, lint, status")
    cmd = mapping[key]
    if not cmd:
        raise ValueError(f"{project} has no `{key}_command` in registry")
    return cmd, root.resolve()


def _shell_injection(cmd: str) -> bool:
    return any(ch in cmd for ch in (";", "|", "&", "\n", "\r", "`"))


def _audit(payload: dict) -> None:
    _bootstrap_imports()
    from app.logging.audit import write_audit
    from app.paths import get_logs_dir

    write_audit(event="safe_terminal_mcp", payload=payload, logs_root=get_logs_dir(), stream="tool-calls")


def _log_tool_call_sqlite(project: str, command: str, mode: str, result: str) -> None:
    _bootstrap_imports()
    from app.memory.repository import log_tool_call
    from app.paths import get_memory_db_path

    db = get_memory_db_path()
    if not db.is_file():
        return
    try:
        log_tool_call(db, project, command, mode, result)
    except Exception as exc:  # noqa: BLE001
        _audit({"sqlite_tool_call_error": str(exc), "project": project, "mode": mode})


def _run(cmd: str, cwd: Path) -> tuple[int, str]:
    if _shell_injection(cmd):
        raise ValueError("command rejected: shell metacharacters not allowed")
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        capture_output=True,
        text=True,
        timeout=600,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out[:8000]


def main() -> None:
    parser = argparse.ArgumentParser(description="ATLAS safe-terminal MCP helper")
    parser.add_argument(
        "action",
        choices=["check", "preview", "run"],
        help="check/preview never execute; run requires approval token",
    )
    parser.add_argument("--project", help="Registry project name (default: ATLAS_SAFE_TERMINAL_PROJECT or single project)")
    parser.add_argument("--type", dest="ctype", default="status", help="build | test | lint | status")
    parser.add_argument("--approval-token", dest="approval_token", default="", help="Required for run; must match env")
    args = parser.parse_args()

    root = _atlas_root()
    reg_path = root / "configs" / "project-registry.json"
    registry = json.loads(reg_path.read_text(encoding="utf-8-sig"))
    project = args.project or _default_project(registry)
    if not project:
        raise SystemExit("Specify --project or set ATLAS_SAFE_TERMINAL_PROJECT or keep exactly one project in registry")

    cmd, cwd = _resolve_command(registry, project, args.ctype)
    _bootstrap_imports()
    from app.safety.command_guard import check_command
    from app.safety.policy import get_safety_policy

    policy = get_safety_policy()
    result = check_command(cmd, policy)
    payload = {
        "action": args.action,
        "project": project,
        "type": args.ctype,
        "cmd": cmd,
        "cwd": str(cwd),
        "safety": result,
    }

    if args.action in ("check", "preview"):
        _audit(payload)
        _log_tool_call_sqlite(project, cmd, args.action, json.dumps(result))
        print(json.dumps({"ok": True, **payload}, ensure_ascii=False, indent=2))
        if result.get("blocked"):
            raise SystemExit(2)
        return

    # run
    expected = os.environ.get("ATLAS_SAFE_TERMINAL_APPROVAL_TOKEN", "")
    if not expected or not args.approval_token or args.approval_token != expected:
        payload["error"] = "missing_or_invalid_approval_token"
        _audit(payload)
        print(json.dumps({"ok": False, **payload}, ensure_ascii=False, indent=2))
        raise SystemExit(3)
    if result.get("blocked"):
        payload["error"] = "blocked_command"
        _audit(payload)
        print(json.dumps({"ok": False, **payload}, ensure_ascii=False, indent=2))
        raise SystemExit(2)
    try:
        code, snippet = _run(cmd, cwd)
    except Exception as exc:  # noqa: BLE001
        payload["error"] = str(exc)
        _audit(payload)
        _log_tool_call_sqlite(project, cmd, "run", str(exc))
        print(json.dumps({"ok": False, **payload}, ensure_ascii=False, indent=2))
        raise SystemExit(1) from exc

    payload["exit_code"] = code
    payload["output_excerpt"] = snippet
    payload["finished_at"] = datetime.now(timezone.utc).isoformat()
    _audit(payload)
    _log_tool_call_sqlite(project, cmd, "run", f"exit={code}\n{snippet}")
    print(json.dumps({"ok": code == 0, **payload}, ensure_ascii=False, indent=2))
    if code != 0:
        raise SystemExit(code)


if __name__ == "__main__":
    main()

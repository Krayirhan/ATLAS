"""Demo report formatter for Sprint 50.

Produces Markdown and JSON-compatible reports from DemoReport objects.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.demo.models import DemoReport, DemoResult


def _result_badge(result: DemoResult) -> str:
    return "PASS" if result.passed else "FAIL"


def build_markdown(report: DemoReport) -> str:
    lines: list[str] = []
    lines.append("# ATLAS Sprint 50 — End-to-End Personal Assistant Demo Report")
    lines.append("")
    lines.append(f"**Project**: {report.project_name}")
    lines.append(f"**Report ID**: `{report.report_id}`")
    lines.append(f"**Generated**: {report.created_at.isoformat()}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Scenarios | {report.total_scenarios} |")
    lines.append(f"| Passed | {report.passed_scenarios} |")
    lines.append(f"| Failed | {report.failed_scenarios} |")
    ss = report.safety_summary
    lines.append(f"| Safe Scenarios | {ss.get('safe_scenarios', 0)} |")
    lines.append(f"| Unsafe Scenarios | {ss.get('unsafe_scenarios', 0)} |")
    lines.append("")

    lines.append("## Scenario Results")
    lines.append("")
    lines.append("| # | Scenario | Category | Response Type | Result | Warnings |")
    lines.append("|---|----------|----------|---------------|--------|----------|")
    for i, result in enumerate(report.results, 1):
        badge = _result_badge(result)
        warnings_str = "; ".join(result.warnings[:2]) if result.warnings else "-"
        lines.append(
            f"| {i} | {result.title} | `{result.command_surface.value}` "
            f"| `{result.response_type}` | **{badge}** | {warnings_str} |"
        )
    lines.append("")

    lines.append("## Safety Boundary Summary")
    lines.append("")
    lines.append(
        "> All demo scenarios are preview-only. "
        "No real PC, home, calendar, notification, voice, or shell execution occurs."
    )
    lines.append("")
    exec_boundary = ss.get("execution_boundary", {})
    lines.append("| Safety Flag | Value |")
    lines.append("|-------------|-------|")
    for flag, value in exec_boundary.items():
        lines.append(f"| `{flag}` | `{value}` |")
    lines.append("")

    violations = ss.get("violations", [])
    if violations:
        lines.append("### Safety Violations")
        lines.append("")
        for v in violations:
            lines.append(f"- **{v['scenario_id']}**: {v['violation']}")
        lines.append("")
    else:
        lines.append("### No Safety Violations")
        lines.append("")
        lines.append("All scenarios passed safety validation.")
        lines.append("")

    lines.append("## Known Limitations")
    lines.append("")
    lines.append("- Chrome / browser does NOT actually open.")
    lines.append("- Lights / home devices are NOT actually toggled.")
    lines.append("- Reminders are drafts; OS scheduler is NOT activated.")
    lines.append("- Calendar events are drafts; no external Calendar API is called.")
    lines.append("- Notifications are preview copies; OS notification is NOT sent.")
    lines.append("- Voice uses Mock STT/TTS; real microphone is NOT accessed.")
    lines.append("- Wake word detection does NOT run.")
    lines.append("- No credentials, .env, or token files are read.")
    lines.append("- No shell/subprocess commands are executed.")
    lines.append("")

    lines.append("## Next Sprint Recommendations")
    lines.append("")
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    lines.append("")

    lines.append("## Sprint 51 Dependency")
    lines.append("")
    lines.append(
        "Sprint 51 — Safety / Latency / UX Hardening: "
        "tighten safety regression tests, measure intent routing latency, "
        "and improve CLI output for end users."
    )
    lines.append("")

    return "\n".join(lines)


def build_json(report: DemoReport) -> str:
    return report.model_dump_json(indent=2)


def write_report(report: DemoReport, output_path: Path, *, as_markdown: bool = True) -> None:
    """Write a report to disk. Path must be inside workspace/outputs/demo/."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if as_markdown:
        output_path.write_text(build_markdown(report), encoding="utf-8")
    else:
        output_path.write_text(build_json(report), encoding="utf-8")


def validate_output_path(path: Path, workspace_root: Path) -> None:
    """Raise ValueError if path escapes workspace/outputs/demo/."""
    allowed_prefix = workspace_root / "workspace" / "outputs" / "demo"
    try:
        path.resolve().relative_to(allowed_prefix.resolve())
    except ValueError as exc:
        raise ValueError(
            f"Output path must be inside workspace/outputs/demo/. Got: {path}"
        ) from exc

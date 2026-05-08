from __future__ import annotations

from pathlib import Path

from app.quality.models import HardeningReport


def build_markdown(report: HardeningReport) -> str:
    lines: list[str] = []
    lines.append("# ATLAS Sprint 51 - Safety / Latency / UX Hardening")
    lines.append("")
    lines.append(f"**Project**: {report.project_name}")
    lines.append(f"**Generated**: {report.created_at.isoformat()}")
    lines.append(f"**Modes**: {', '.join(report.modes) if report.modes else 'none'}")
    lines.append("")

    if report.safety_report is not None:
        safety = report.safety_report
        lines.append("## Safety Summary")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Checks | {safety.total_checks} |")
        lines.append(f"| Passed | {safety.passed} |")
        lines.append(f"| Failed | {safety.failed} |")
        lines.append("")
        lines.append("| Check | Surface | Passed |")
        lines.append("|-------|---------|--------|")
        for check in safety.checks:
            lines.append(f"| {check.name} | `{check.command_surface}` | `{check.passed}` |")
        lines.append("")

    if report.latency_report is not None:
        latency = report.latency_report
        lines.append("## Latency Summary")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Measurements | {latency.total_measurements} |")
        lines.append(f"| Passed | {latency.passed} |")
        lines.append(f"| Failed | {latency.failed} |")
        lines.append("")
        lines.append("| Measurement | Surface | Duration (ms) | Threshold (ms) | Passed |")
        lines.append("|-------------|---------|---------------|----------------|--------|")
        for measurement in latency.measurements:
            lines.append(
                f"| {measurement.name} | `{measurement.command_surface}` | "
                f"{measurement.duration_ms} | {measurement.threshold_ms} | `{measurement.passed}` |"
            )
        lines.append("")

    lines.append("## Execution Boundary")
    lines.append("")
    lines.append("- Gercek PC execution yok.")
    lines.append("- Gercek home execution yok.")
    lines.append("- Gercek scheduler yok.")
    lines.append("- Gercek OS notification yok.")
    lines.append("- Gercek calendar API yok.")
    lines.append("- Gercek microphone capture yok.")
    lines.append("- Wake word / always-listening yok.")
    lines.append("- Shell / terminal executor yok.")
    lines.append("")

    lines.append("## Recommendations")
    lines.append("")
    for recommendation in report.recommendations:
        lines.append(f"- {recommendation}")
    lines.append("")
    return "\n".join(lines)


def build_json(report: HardeningReport) -> str:
    return report.model_dump_json(indent=2)


def write_report(report: HardeningReport, output_path: Path, *, as_markdown: bool = True) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if as_markdown:
        output_path.write_text(build_markdown(report), encoding="utf-8")
    else:
        output_path.write_text(build_json(report), encoding="utf-8")


def validate_output_path(path: Path, workspace_root: Path) -> None:
    allowed_prefix = workspace_root / "workspace" / "outputs" / "hardening"
    try:
        path.resolve().relative_to(allowed_prefix.resolve())
    except ValueError as exc:
        raise ValueError(f"Output path must be inside workspace/outputs/hardening/. Got: {path}") from exc

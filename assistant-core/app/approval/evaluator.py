"""Evaluate proposed actions into preview-only approval decisions."""

from __future__ import annotations

import re
from pathlib import Path

from app.approval.models import (
    ApprovalDecision,
    ApprovalFinding,
    ApprovalPreview,
    ApprovalRequirement,
    ProposedAction,
    ProposedCommand,
    ProposedFileChange,
    ProposedToolCall,
)
from app.approval.policy import (
    APPROVAL_REQUIRED_EXTRAS,
    BLOCKED_FILE_TOKENS,
    BLOCKED_PATH_TOKENS,
    PREVIEW_ALLOWED_PREFIXES,
    SAFE_READONLY_PREFIXES,
    load_approval_policy,
)
from app.config.models import SafetyPolicyModel
from app.projects.registry import get_project
from app.safety.path_guard import is_allowed_workspace_path, is_blocked_path


class ApprovalEvaluator:
    def __init__(self, policy: SafetyPolicyModel | None = None) -> None:
        self._policy = policy or load_approval_policy()

    def evaluate(self, action: ProposedAction) -> ApprovalDecision:
        if isinstance(action, ProposedCommand):
            return self.evaluate_command(action)
        if isinstance(action, ProposedFileChange):
            return self.evaluate_file_change(action)
        if isinstance(action, ProposedToolCall):
            return self.evaluate_tool_call(action)
        return self._decision(
            status="unknown",
            risk_level="medium",
            reason="Unknown action type. Preview only; explicit user review is required.",
            findings=[ApprovalFinding(severity="medium", category="unknown", detail=f"Unsupported action_type={action.action_type}")],
            action=action,
            suggested_next_step="Dar bir action modeli ile tekrar degerlendirin.",
        )

    def evaluate_command(self, action: ProposedCommand) -> ApprovalDecision:
        findings: list[ApprovalFinding] = []
        norm = self._norm(action.command)
        blocked_rules = self._match_policy_tokens(norm, self._policy.blocked_commands)
        approval_rules = self._match_policy_tokens(norm, self._policy.approval_required_commands)
        blocked_path_hits = self._blocked_path_hits(action.command)
        blocked_file_hits = self._blocked_file_hits(action.command)
        registry_hits = self._registry_forbidden_hits(action.project_name, action.command)

        for hit in blocked_rules:
            findings.append(ApprovalFinding(severity="critical", category="command", detail=f"blocked_commands match: {hit}"))
        for hit in blocked_path_hits:
            findings.append(ApprovalFinding(severity="critical", category="path", detail=hit))
        for hit in blocked_file_hits:
            findings.append(ApprovalFinding(severity="critical", category="secret-path", detail=hit))
        for hit in registry_hits:
            findings.append(ApprovalFinding(severity="high", category="registry", detail=hit))

        if blocked_rules or blocked_path_hits or blocked_file_hits:
            return self._decision(
                status="blocked",
                risk_level="critical",
                reason="Command violates ATLAS safety policy. It must not be executed.",
                findings=findings,
                action=action,
                suggested_next_step="Komutu daraltin veya read-only bir alternatif preview isteyin.",
                preview=ApprovalPreview(
                    summary="Blocked command preview only.",
                    command_preview=action.command,
                    working_directory=self._working_directory(action),
                ),
            )

        for hit in approval_rules:
            findings.append(ApprovalFinding(severity="high", category="command", detail=f"approval_required_commands match: {hit}"))
        extra_approval = self._approval_required_extra_hits(norm)
        for hit in extra_approval:
            findings.append(ApprovalFinding(severity="high", category="workflow", detail=hit))

        if self._is_safe_readonly(norm):
            return self._decision(
                status="safe_readonly",
                risk_level="info",
                reason="Command is classified as read-only and safe for preview discussion only.",
                findings=findings or [ApprovalFinding(severity="info", category="readonly", detail="Safe read-only command pattern matched.")],
                action=action,
                suggested_next_step="Komut yine otomatik calistirilmaz; sadece preview ve onay akisinda kullanilir.",
                preview=ApprovalPreview(
                    summary="Safe read-only command preview.",
                    command_preview=action.command,
                    working_directory=self._working_directory(action),
                ),
            )

        if self._is_preview_allowed(norm):
            return self._decision(
                status="preview_allowed",
                risk_level="low",
                reason="Command is acceptable as a preview candidate but still will not be executed automatically.",
                findings=findings or [ApprovalFinding(severity="low", category="preview", detail="Preview-allowed command pattern matched.")],
                action=action,
                suggested_next_step="Gerekirse ayri kullanici onayi ile manuel calistirma degerlendirilebilir.",
                preview=ApprovalPreview(
                    summary="Preview-allowed command.",
                    command_preview=action.command,
                    working_directory=self._working_directory(action),
                ),
            )

        if approval_rules or extra_approval:
            return self._decision(
                status="approval_required",
                risk_level="high",
                reason="Command is not blocked, but it needs explicit user approval before any manual execution.",
                findings=findings,
                action=action,
                suggested_next_step="Acilan riskleri kullaniciya gosterin ve acik onay alin.",
                requirements=[ApprovalRequirement(requirement_type="user_approval", detail="Explicit user approval required.")],
                preview=ApprovalPreview(
                    summary="Approval-required command preview.",
                    command_preview=action.command,
                    working_directory=self._working_directory(action),
                ),
            )

        return self._decision(
            status="approval_required",
            risk_level="medium",
            reason="Command is not in the blocked list, but it is not a known safe read-only preview either.",
            findings=[ApprovalFinding(severity="medium", category="review", detail="Unknown command pattern; defaulting to manual approval.")],
            action=action,
            suggested_next_step="Komutu daha dar ve read-only bir forma indirin veya kullanici onayi alin.",
            requirements=[ApprovalRequirement(requirement_type="manual_review", detail="Manual review required for unknown command pattern.")],
            preview=ApprovalPreview(
                summary="Unknown command preview.",
                command_preview=action.command,
                working_directory=self._working_directory(action),
            ),
        )

    def evaluate_file_change(self, action: ProposedFileChange) -> ApprovalDecision:
        path = Path(action.file_path)
        blocked, reason = is_blocked_path(path, self._policy)
        findings: list[ApprovalFinding] = []
        if blocked:
            findings.append(ApprovalFinding(severity="critical", category="path", detail=reason or "Blocked path"))
            return self._decision(
                status="blocked",
                risk_level="critical",
                reason="File change targets a blocked path or file pattern.",
                findings=findings,
                action=action,
                suggested_next_step="Blocked path disina cikin veya degisikligi iptal edin.",
            )
        if not is_allowed_workspace_path(path, self._policy):
            return self._decision(
                status="approval_required",
                risk_level="high",
                reason="File change is outside the allowed workspace roots.",
                findings=[ApprovalFinding(severity="high", category="path", detail=f"Outside allowed workspace: {action.file_path}")],
                action=action,
                suggested_next_step="Workspace icindeki dokuman/test alanlari ile sinirlandirin.",
            )
        if action.change_type in {"documentation_write", "test_write"}:
            return self._decision(
                status="preview_allowed",
                risk_level="low",
                reason="Docs/test write is previewable, but not auto-executable in this sprint.",
                findings=[ApprovalFinding(severity="low", category="file-change", detail=f"Preview-only file change type: {action.change_type}")],
                action=action,
                suggested_next_step="Gerekirse kullanici onayi sonrasi ayri uygulama sprintinde ele alin.",
            )
        return self._decision(
            status="approval_required",
            risk_level="high",
            reason="Non-doc/test file changes require explicit approval and are not executed here.",
            findings=[ApprovalFinding(severity="high", category="file-change", detail=f"Restricted change_type: {action.change_type}")],
            action=action,
            suggested_next_step="Degisikligi gerekcelendirip acik kullanici onayi alin.",
        )

    def evaluate_tool_call(self, action: ProposedToolCall) -> ApprovalDecision:
        tool_name = action.tool_name.strip().lower()
        if "mcp" in tool_name:
            return self._decision(
                status="blocked",
                risk_level="critical",
                reason="MCP tool calls are blocked in this sprint.",
                findings=[ApprovalFinding(severity="critical", category="tool-call", detail=f"Blocked tool_name={action.tool_name}")],
                action=action,
                suggested_next_step="Tool call yerine preview-only plan veya review uretin.",
            )
        return self._decision(
            status="approval_required",
            risk_level="high",
            reason="Tool calls require explicit design approval and are not executed here.",
            findings=[ApprovalFinding(severity="high", category="tool-call", detail=f"Tool call proposed: {action.tool_name}")],
            action=action,
            suggested_next_step="Tool approval tasarimi tamamlanana kadar tool cagrisi yapmayin.",
        )

    def _decision(
        self,
        *,
        status,
        risk_level,
        reason,
        findings,
        action: ProposedAction,
        suggested_next_step,
        preview: ApprovalPreview | None = None,
        requirements: list[ApprovalRequirement] | None = None,
    ) -> ApprovalDecision:
        return ApprovalDecision(
            status=status,
            risk_level=risk_level,
            reason=reason,
            findings=findings,
            approval_required=status == "approval_required",
            blocked=status == "blocked",
            safe_preview=status in {"preview_allowed", "safe_readonly"},
            suggested_next_step=suggested_next_step,
            audit_metadata={
                "project": action.project_name,
                "action_type": action.action_type,
                "source_agent": action.source_agent,
                "status": status,
                "risk_level": risk_level,
                "reason_length": len(action.reason or ""),
                "user_goal_length": len(action.user_goal or ""),
            },
            preview=preview,
            requirements=requirements or [],
        )

    def _norm(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.strip()).lower()

    def _match_policy_tokens(self, norm_command: str, tokens: list[str]) -> list[str]:
        hits: list[str] = []
        for token in tokens:
            t = self._norm(token)
            if not t:
                continue
            if self._token_present(norm_command, t):
                hits.append(token)
        return hits

    def _token_present(self, norm_command: str, token: str) -> bool:
        if " " in token or "\\" in token or "/" in token or "-" in token:
            return token in norm_command
        return re.search(rf"(?<!\w){re.escape(token)}(?!\w)", norm_command) is not None

    def _blocked_path_hits(self, command: str) -> list[str]:
        low = command.lower()
        hits: list[str] = []
        for token in BLOCKED_PATH_TOKENS:
            if token in low:
                hits.append(f"Blocked path token matched: {token}")
        if "full disk" in low:
            hits.append("Full disk access intent detected.")
        return hits

    def _blocked_file_hits(self, command: str) -> list[str]:
        low = command.lower()
        hits: list[str] = []
        for token in BLOCKED_FILE_TOKENS:
            if token in low:
                hits.append(f"Blocked file or secret token matched: {token}")
        return hits

    def _approval_required_extra_hits(self, norm_command: str) -> list[str]:
        return [token for token in APPROVAL_REQUIRED_EXTRAS if token in norm_command]

    def _registry_forbidden_hits(self, project_name: str, command: str) -> list[str]:
        project = get_project(project_name)
        if not project:
            return []
        low = command.lower()
        hits: list[str] = []
        for rule in project.forbidden_changes:
            r = rule.lower()
            if ".env" in r and ".env" in low:
                hits.append(rule)
            elif "d:\\atlas" in r and "d:\\atlas" in low:
                hits.append(rule)
            elif "private keys" in r and any(token in low for token in ("id_rsa", "id_ed25519", ".pem", ".key", ".jks", "keystore")):
                hits.append(rule)
            elif "git push automation" in r and "git push" in low:
                hits.append(rule)
            elif "full disk mcp access" in r and ("full disk" in low or "c:\\users" in low):
                hits.append(rule)
        return hits

    def _is_safe_readonly(self, norm_command: str) -> bool:
        return any(norm_command.startswith(prefix) for prefix in SAFE_READONLY_PREFIXES)

    def _is_preview_allowed(self, norm_command: str) -> bool:
        return any(norm_command.startswith(prefix) for prefix in PREVIEW_ALLOWED_PREFIXES)

    def _working_directory(self, action: ProposedCommand) -> str:
        if action.working_directory.strip():
            return action.working_directory
        project = get_project(action.project_name)
        if project and project.command_workdir:
            return str(project.command_workdir)
        return ""

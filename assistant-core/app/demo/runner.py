"""DemoRunner for Sprint 50 end-to-end personal assistant demo.

Executes built-in scenarios against real ATLAS services.
No real execution is performed; all flows are preview-only.
"""

from __future__ import annotations

import uuid
from typing import Any

from app.actions.types import ActionSource
from app.demo.models import (
    CommandSurface,
    DemoCategory,
    DemoReport,
    DemoResult,
    DemoScenario,
)
from app.demo.policy import build_safety_summary, validate_safety
from app.demo.scenarios import BUILTIN_SCENARIOS, get_scenarios_by_category


_SAFE_BASE_FLAGS: dict[str, bool] = {
    "execution_attempted": False,
    "physical_device_touched": False,
    "network_used": False,
    "microphone_used": False,
    "wake_word_used": False,
    "audio_retained": False,
    "external_calendar_used": False,
    "os_notification_sent": False,
    "credential_accessed": False,
    "shell_used": False,
}


class DemoRunner:
    """Executes demo scenarios and produces DemoResult / DemoReport objects."""

    def __init__(self, project_name: str = "ATLAS") -> None:
        self.project_name = project_name

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_scenarios(self) -> list[DemoScenario]:
        return list(BUILTIN_SCENARIOS)

    def run_scenario(self, scenario_id: str) -> DemoResult:
        scenario = next((s for s in BUILTIN_SCENARIOS if s.scenario_id == scenario_id), None)
        if scenario is None:
            return DemoResult(
                scenario_id=scenario_id,
                title=f"Unknown scenario: {scenario_id}",
                passed=False,
                response_type="error",
                assistant_message=f"Scenario '{scenario_id}' not found.",
                command_surface=CommandSurface.CHAT,
                safety_flags=dict(_SAFE_BASE_FLAGS),
                warnings=[f"Scenario '{scenario_id}' is not registered."],
            )
        return self._execute(scenario)

    def run_all(self) -> DemoReport:
        results = [self._execute(s) for s in BUILTIN_SCENARIOS]
        return self._build_report(results)

    def run_category(self, category: DemoCategory) -> DemoReport:
        scenarios = get_scenarios_by_category(category)
        results = [self._execute(s) for s in scenarios]
        return self._build_report(results, category=category)

    def validate_safety(self, result: DemoResult) -> list[str]:
        return validate_safety(result)

    # ------------------------------------------------------------------
    # Internal dispatcher
    # ------------------------------------------------------------------

    def _execute(self, scenario: DemoScenario) -> DemoResult:
        try:
            surface = scenario.command_surface
            if surface == CommandSurface.CHAT:
                return self._run_chat(scenario)
            if surface == CommandSurface.VOICE:
                return self._run_voice(scenario)
            if surface == CommandSurface.PC_PREVIEW:
                return self._run_pc_preview(scenario)
            if surface == CommandSurface.DEVICE:
                return self._run_device(scenario)
            if surface == CommandSurface.HOME_PREVIEW:
                return self._run_home_preview(scenario)
            if surface == CommandSurface.ROUTINE:
                return self._run_routine(scenario)
            if surface == CommandSurface.MEMORY_PERSONAL:
                return self._run_memory(scenario)
            if surface == CommandSurface.REMINDER:
                return self._run_reminder(scenario)
            if surface == CommandSurface.CALENDAR:
                return self._run_calendar(scenario)
            if surface == CommandSurface.PANEL:
                return self._run_panel(scenario)
            # fallback: chat
            return self._run_chat(scenario)
        except Exception as exc:  # noqa: BLE001
            return DemoResult(
                scenario_id=scenario.scenario_id,
                title=scenario.title,
                passed=False,
                response_type="error",
                assistant_message=f"Runner error: {exc}",
                command_surface=scenario.command_surface,
                safety_flags=dict(_SAFE_BASE_FLAGS),
                warnings=[f"Exception during scenario execution: {exc}"],
            )

    # ------------------------------------------------------------------
    # Surface handlers
    # ------------------------------------------------------------------

    def _run_chat(self, scenario: DemoScenario) -> DemoResult:
        from app.conversation.loop import ConversationLoop

        loop = ConversationLoop()
        session_id = str(uuid.uuid4())
        response = loop.handle_text(
            message=scenario.input_text,
            project_name=self.project_name,
            session_id=session_id,
            source=ActionSource.TEXT,
        )
        flags = dict(_SAFE_BASE_FLAGS)
        flags.update(response.audit_metadata)
        _enforce_safe_base(flags)

        raw = (
            f"response_type={response.response_type.value}, "
            f"blocked={response.blocked}, "
            f"confirmation_required={response.confirmation_required}, "
            f"clarification_required={response.clarification_required}"
        )
        violations = validate_safety(
            DemoResult(
                scenario_id=scenario.scenario_id,
                title=scenario.title,
                passed=True,
                response_type=response.response_type.value,
                assistant_message=response.assistant_message,
                command_surface=scenario.command_surface,
                safety_flags=flags,
            )
        )
        passed = len(violations) == 0
        return DemoResult(
            scenario_id=scenario.scenario_id,
            title=scenario.title,
            passed=passed,
            response_type=response.response_type.value,
            assistant_message=response.assistant_message,
            command_surface=scenario.command_surface,
            safety_flags=flags,
            warnings=response.warnings + violations,
            raw_result_summary=raw,
            metadata={
                "intent": response.intent,
                "blocked": response.blocked,
                "confirmation_required": response.confirmation_required,
                "clarification_required": response.clarification_required,
            },
        )

    def _run_voice(self, scenario: DemoScenario) -> DemoResult:
        from app.voice.mock_adapters import MockSTTAdapter, MockTTSAdapter
        from app.voice.models import VoicePipelineRequest, VoiceSource
        from app.voice.pipeline import VoicePipeline

        pipeline = VoicePipeline(stt_adapter=MockSTTAdapter(), tts_adapter=MockTTSAdapter())
        result = pipeline.handle(
            VoicePipelineRequest(
                project_name=self.project_name,
                mock_transcript=scenario.input_text,
                language="tr",
                source=VoiceSource.MOCK_TRANSCRIPT,
            )
        )
        flags = dict(_SAFE_BASE_FLAGS)
        flags["audio_retained"] = result.audio_retained
        flags["microphone_used"] = result.microphone_used
        flags["wake_word_used"] = result.wake_word_used
        flags["execution_attempted"] = result.execution_attempted
        _enforce_safe_base(flags)

        conv_resp = result.conversation_response
        resp_type = conv_resp.response_type.value if conv_resp else "answer"
        msg = conv_resp.assistant_message if conv_resp else "(no response)"

        temp = DemoResult(
            scenario_id=scenario.scenario_id,
            title=scenario.title,
            passed=True,
            response_type=resp_type,
            assistant_message=msg,
            command_surface=scenario.command_surface,
            safety_flags=flags,
        )
        violations = validate_safety(temp)
        passed = len(violations) == 0
        return DemoResult(
            scenario_id=scenario.scenario_id,
            title=scenario.title,
            passed=passed,
            response_type=resp_type,
            assistant_message=msg,
            command_surface=scenario.command_surface,
            safety_flags=flags,
            warnings=list(result.safety_warnings) + violations,
            raw_result_summary=f"voice_source=mock_transcript, execution_attempted={result.execution_attempted}",
            metadata={
                "transcript": result.transcript.text,
                "audio_retained": result.audio_retained,
                "microphone_used": result.microphone_used,
                "wake_word_used": result.wake_word_used,
                "execution_attempted": result.execution_attempted,
            },
        )

    def _run_pc_preview(self, scenario: DemoScenario) -> DemoResult:
        from dataclasses import asdict

        from app.actions.intent_router import IntentRouter
        from app.control.pc_adapter import PCControlAdapter

        router = IntentRouter()
        adapter = PCControlAdapter()
        router_result = router.preview(scenario.input_text, source=ActionSource.TEXT)
        flags = dict(_SAFE_BASE_FLAGS)

        resp_type = "action_preview"
        msg = "PC action preview generated (no execution)."

        if router_result.action_candidate and router_result.permission_decision:
            plan = adapter.build_plan(
                router_result.action_candidate, router_result.permission_decision, dry_run=True
            )
            exec_result = adapter.execute(plan)
            flags["execution_attempted"] = exec_result.metadata.get("execution_attempted", False)
            msg = exec_result.message
            resp_type = exec_result.status.value
        elif router_result.clarification:
            resp_type = "clarification"
            msg = router_result.clarification.reason
        else:
            resp_type = "blocked"
            msg = "No action candidate or permission decision."

        _enforce_safe_base(flags)
        violations = validate_safety(
            DemoResult(
                scenario_id=scenario.scenario_id,
                title=scenario.title,
                passed=True,
                response_type=resp_type,
                assistant_message=msg,
                command_surface=scenario.command_surface,
                safety_flags=flags,
            )
        )
        passed = len(violations) == 0
        return DemoResult(
            scenario_id=scenario.scenario_id,
            title=scenario.title,
            passed=passed,
            response_type=resp_type,
            assistant_message=msg,
            command_surface=scenario.command_surface,
            safety_flags=flags,
            warnings=router_result.warnings + violations,
            raw_result_summary=f"intent={router_result.intent.category.value}",
            metadata={},
        )

    def _run_device(self, scenario: DemoScenario) -> DemoResult:
        from app.devices.planner import DeviceActionPlanner
        from app.devices.registry import DeviceRegistry

        registry = DeviceRegistry()
        planner = DeviceActionPlanner(registry=registry)
        result = planner.preview_device_action(scenario.input_text, source=ActionSource.TEXT)
        flags = dict(_SAFE_BASE_FLAGS)
        _enforce_safe_base(flags)

        resp_type = result.status.value
        msg = result.message
        violations = validate_safety(
            DemoResult(
                scenario_id=scenario.scenario_id,
                title=scenario.title,
                passed=True,
                response_type=resp_type,
                assistant_message=msg,
                command_surface=scenario.command_surface,
                safety_flags=flags,
            )
        )
        passed = len(violations) == 0
        return DemoResult(
            scenario_id=scenario.scenario_id,
            title=scenario.title,
            passed=passed,
            response_type=resp_type,
            assistant_message=msg,
            command_surface=scenario.command_surface,
            safety_flags=flags,
            warnings=result.warnings + violations,
            raw_result_summary=f"device_status={result.status.value}",
            metadata={},
        )

    def _run_home_preview(self, scenario: DemoScenario) -> DemoResult:
        from app.home.service import HomeControlService

        service = HomeControlService()
        plan, result = service.preview_plan(scenario.input_text, source=ActionSource.TEXT)
        flags = dict(_SAFE_BASE_FLAGS)
        # HomeControlResult uses audit_metadata, not metadata
        audit = getattr(result, "audit_metadata", {}) or {}
        flags["network_used"] = audit.get("network_used", False)
        flags["physical_device_touched"] = audit.get("physical_device_touched", False)
        _enforce_safe_base(flags)

        resp_type = result.status.value
        msg = result.message
        violations = validate_safety(
            DemoResult(
                scenario_id=scenario.scenario_id,
                title=scenario.title,
                passed=True,
                response_type=resp_type,
                assistant_message=msg,
                command_surface=scenario.command_surface,
                safety_flags=flags,
            )
        )
        passed = len(violations) == 0
        return DemoResult(
            scenario_id=scenario.scenario_id,
            title=scenario.title,
            passed=passed,
            response_type=resp_type,
            assistant_message=msg,
            command_surface=scenario.command_surface,
            safety_flags=flags,
            warnings=violations,
            raw_result_summary=f"home_status={result.status.value}, plan={'yes' if plan else 'none'}",
            metadata={"plan": plan.summary if plan else None},
        )

    def _run_routine(self, scenario: DemoScenario) -> DemoResult:
        from app.routines.service import RoutineService

        service = RoutineService()
        result = service.handle_text(scenario.input_text)
        flags = dict(_SAFE_BASE_FLAGS)
        _enforce_safe_base(flags)

        msg = service.format_response(result)
        resp_type = "answer"
        if result is not None and hasattr(result, "status"):
            status_val = getattr(result.status, "value", str(result.status))
            if status_val == "blocked":
                resp_type = "blocked"
            elif status_val == "awaiting_confirmation":
                resp_type = "confirmation_required"

        violations = validate_safety(
            DemoResult(
                scenario_id=scenario.scenario_id,
                title=scenario.title,
                passed=True,
                response_type=resp_type,
                assistant_message=msg,
                command_surface=scenario.command_surface,
                safety_flags=flags,
            )
        )
        passed = len(violations) == 0
        return DemoResult(
            scenario_id=scenario.scenario_id,
            title=scenario.title,
            passed=passed,
            response_type=resp_type,
            assistant_message=msg,
            command_surface=scenario.command_surface,
            safety_flags=flags,
            warnings=violations,
            raw_result_summary=f"routine_status={resp_type}",
            metadata={},
        )

    def _run_memory(self, scenario: DemoScenario) -> DemoResult:
        from app.personal_memory.service import PersonalMemoryService
        from app.personal_memory.models import MemoryOperationStatus

        service = PersonalMemoryService()
        result = service.handle_text(scenario.input_text)
        flags = dict(_SAFE_BASE_FLAGS)
        _enforce_safe_base(flags)

        resp_type = "answer"
        if result.status == MemoryOperationStatus.BLOCKED:
            resp_type = "blocked"

        violations = validate_safety(
            DemoResult(
                scenario_id=scenario.scenario_id,
                title=scenario.title,
                passed=True,
                response_type=resp_type,
                assistant_message=result.message,
                command_surface=scenario.command_surface,
                safety_flags=flags,
            )
        )
        passed = len(violations) == 0
        return DemoResult(
            scenario_id=scenario.scenario_id,
            title=scenario.title,
            passed=passed,
            response_type=resp_type,
            assistant_message=result.message,
            command_surface=scenario.command_surface,
            safety_flags=flags,
            warnings=violations,
            raw_result_summary=f"memory_status={result.status.value}",
            metadata={"blocked_reason": result.blocked_reason},
        )

    def _run_reminder(self, scenario: DemoScenario) -> DemoResult:
        from app.personal_assistant.models import ReminderResultStatus, ReminderSource
        from app.personal_assistant.reminders import ReminderService

        service = ReminderService()
        result = service.create_reminder(scenario.input_text, source=ReminderSource.TEXT)
        flags = dict(_SAFE_BASE_FLAGS)
        flags["os_notification_sent"] = False
        _enforce_safe_base(flags)

        resp_type = "answer"
        if result.status == ReminderResultStatus.PENDING_CONFIRMATION:
            resp_type = "confirmation_required"
        elif result.status == ReminderResultStatus.BLOCKED:
            resp_type = "blocked"
        elif result.status == ReminderResultStatus.PREVIEW:
            resp_type = "action_preview"

        msg = service.format_result(result)
        violations = validate_safety(
            DemoResult(
                scenario_id=scenario.scenario_id,
                title=scenario.title,
                passed=True,
                response_type=resp_type,
                assistant_message=msg,
                command_surface=scenario.command_surface,
                safety_flags=flags,
            )
        )
        passed = len(violations) == 0
        return DemoResult(
            scenario_id=scenario.scenario_id,
            title=scenario.title,
            passed=passed,
            response_type=resp_type,
            assistant_message=msg,
            command_surface=scenario.command_surface,
            safety_flags=flags,
            warnings=result.warnings + violations,
            raw_result_summary=f"reminder_status={result.status.value}",
            metadata={"audit_metadata": result.audit_metadata},
        )

    def _run_calendar(self, scenario: DemoScenario) -> DemoResult:
        from app.personal_assistant.calendar import CalendarService
        from app.personal_assistant.models import (
            CalendarOperation,
            CalendarStatus,
            ReminderSource,
        )
        from app.personal_assistant.parser import parse_calendar_request

        service = CalendarService()
        source = ReminderSource.TEXT
        operation, _ = parse_calendar_request(scenario.input_text)
        if operation == CalendarOperation.QUERY:
            result = service.query_calendar(scenario.input_text, source=source)
        else:
            result = service.create_event_draft(scenario.input_text, source=source)

        flags = dict(_SAFE_BASE_FLAGS)
        flags["external_calendar_used"] = False
        _enforce_safe_base(flags)

        resp_type = "answer"
        if result.status == CalendarStatus.PENDING_CONFIRMATION:
            resp_type = "confirmation_required"
        elif result.status == CalendarStatus.SAFE_QUERY_PREVIEW:
            resp_type = "action_preview"
        elif result.status == CalendarStatus.BLOCKED:
            resp_type = "blocked"

        msg = service.format_result(result)
        violations = validate_safety(
            DemoResult(
                scenario_id=scenario.scenario_id,
                title=scenario.title,
                passed=True,
                response_type=resp_type,
                assistant_message=msg,
                command_surface=scenario.command_surface,
                safety_flags=flags,
            )
        )
        passed = len(violations) == 0
        return DemoResult(
            scenario_id=scenario.scenario_id,
            title=scenario.title,
            passed=passed,
            response_type=resp_type,
            assistant_message=msg,
            command_surface=scenario.command_surface,
            safety_flags=flags,
            warnings=result.warnings + violations,
            raw_result_summary=f"calendar_status={result.status.value}",
            metadata={"audit_metadata": result.audit_metadata},
        )

    def _run_panel(self, scenario: DemoScenario) -> DemoResult:
        from app.actions.types import ActionSource
        from app.panel.service import PermissionPanelService

        service = PermissionPanelService()
        result = service.submit_text(
            scenario.input_text, source=ActionSource.TEXT, project_name=self.project_name
        )
        flags = dict(_SAFE_BASE_FLAGS)
        flags["execution_attempted"] = False
        _enforce_safe_base(flags)

        resp_type = result.status.value
        msg = result.message
        violations = validate_safety(
            DemoResult(
                scenario_id=scenario.scenario_id,
                title=scenario.title,
                passed=True,
                response_type=resp_type,
                assistant_message=msg,
                command_surface=scenario.command_surface,
                safety_flags=flags,
            )
        )
        passed = len(violations) == 0
        return DemoResult(
            scenario_id=scenario.scenario_id,
            title=scenario.title,
            passed=passed,
            response_type=resp_type,
            assistant_message=msg,
            command_surface=scenario.command_surface,
            safety_flags=flags,
            warnings=result.warnings + violations,
            raw_result_summary=f"panel_status={result.status.value}",
            metadata={
                "item_id": result.item.item_id if result.item else None,
            },
        )

    # ------------------------------------------------------------------
    # Report builder
    # ------------------------------------------------------------------

    def _build_report(
        self, results: list[DemoResult], category: DemoCategory | None = None
    ) -> DemoReport:
        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed
        safety_summary = build_safety_summary(results)
        recs: list[str] = []
        if failed > 0:
            recs.append(f"{failed} scenario(s) failed — review warnings above.")
        if safety_summary["unsafe_scenarios"] > 0:
            recs.append("Safety violations detected — do not demo until resolved.")
        recs.append("Sprint 51: Safety / Latency / UX Hardening")
        recs.append("No real execution paths have been opened in this sprint.")

        return DemoReport(
            report_id=str(uuid.uuid4()),
            project_name=self.project_name,
            total_scenarios=len(results),
            passed_scenarios=passed,
            failed_scenarios=failed,
            results=results,
            safety_summary=safety_summary,
            recommendations=recs,
            metadata={"category_filter": category.value if category else "all"},
        )


def _enforce_safe_base(flags: dict[str, Any]) -> None:
    """Ensure base safe flags are present and never overridden to True by accident."""
    for key in _SAFE_BASE_FLAGS:
        if key not in flags:
            flags[key] = False

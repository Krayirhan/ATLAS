from __future__ import annotations

from dataclasses import asdict

from app.actions.types import ActionSource
from app.devices.planner import DeviceActionPlanner
from app.home.mock_adapter import MockHomeControlAdapter
from app.home.models import HomeControlResult
from app.home.planner import HomeControlPlanner


class HomeControlService:
    def __init__(self) -> None:
        self.device_planner = DeviceActionPlanner()
        self.planner = HomeControlPlanner(device_planner=self.device_planner)
        self.adapter = MockHomeControlAdapter(registry=self.device_planner.registry)

    def preview_text(self, text: str, source: ActionSource = ActionSource.TEXT) -> HomeControlResult:
        device_result = self.device_planner.preview_device_action(text, source=source)
        if device_result.plan is None:
            return self.planner.preview_from_text(text, source=source)
        home_plan = self.adapter.build_plan(device_result.plan)
        return self.adapter.execute(home_plan)

    def preview_plan(self, text: str, source: ActionSource = ActionSource.TEXT):
        device_result = self.device_planner.preview_device_action(text, source=source)
        if device_result.plan is None:
            return None, self.planner.preview_from_text(text, source=source)
        home_plan = self.adapter.build_plan(device_result.plan)
        return home_plan, self.adapter.execute(home_plan)

    def list_capabilities(self) -> list[dict[str, object]]:
        return [asdict(item) for item in self.adapter.capabilities()]

    def adapter_status(self) -> dict[str, object]:
        return self.adapter.health_check()

    def format_response(self, result: HomeControlResult) -> str:
        return result.message

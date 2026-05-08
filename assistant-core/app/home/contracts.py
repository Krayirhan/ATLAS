from __future__ import annotations

from typing import Protocol

from app.devices.models import DeviceActionPlan
from app.home.models import (
    HomeAdapterCapability,
    HomeControlPlan,
    HomeControlResult,
    HomeStateReadRequest,
    HomeStateReadResult,
    HomeStateWriteRequest,
    HomeStateWriteResult,
)


class HomeControlAdapter(Protocol):
    def name(self) -> str: ...

    def health_check(self) -> dict[str, object]: ...

    def capabilities(self) -> list[HomeAdapterCapability]: ...

    def build_plan(self, device_action_plan: DeviceActionPlan) -> HomeControlPlan: ...

    def read_state(self, request: HomeStateReadRequest) -> HomeStateReadResult: ...

    def write_state(self, request: HomeStateWriteRequest) -> HomeStateWriteResult: ...

    def execute(self, plan: HomeControlPlan) -> HomeControlResult: ...

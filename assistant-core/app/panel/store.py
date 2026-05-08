from __future__ import annotations

import json
import os
from pathlib import Path

from app.panel.models import (
    PanelDecision,
    PanelDecisionType,
    PanelItemStatus,
    PermissionPanelItem,
)
from app.panel.policy import MAX_STORED_ITEMS, ensure_status


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _default_store_path() -> Path:
    configured = os.environ.get("ATLAS_PANEL_STORE_PATH")
    if configured:
        return Path(configured).resolve()
    return (_repo_root() / "workspace" / "state" / "permission-panel.json").resolve()


class InMemoryPanelStore:
    def __init__(self) -> None:
        self._items: dict[str, PermissionPanelItem] = {}

    def add(self, item: PermissionPanelItem) -> PermissionPanelItem:
        self._items[item.item_id] = ensure_status(item)
        return item

    def list(self, status: str | None = None) -> list[PermissionPanelItem]:
        self.prune_expired()
        items = list(self._items.values())
        if status is not None:
            items = [item for item in items if item.status.value == status]
        return sorted(items, key=lambda item: item.created_at, reverse=True)

    def get(self, item_id: str) -> PermissionPanelItem | None:
        item = self._items.get(item_id)
        return ensure_status(item) if item is not None else None

    def update(self, item: PermissionPanelItem) -> PermissionPanelItem:
        self._items[item.item_id] = ensure_status(item)
        return item

    def approve(self, item_id: str, decision: PanelDecision) -> PermissionPanelItem | None:
        item = self.get(item_id)
        if item is None:
            return None
        item.status = PanelItemStatus.APPROVED
        item.last_decision = decision
        self.update(item)
        return item

    def deny(self, item_id: str, decision: PanelDecision) -> PermissionPanelItem | None:
        item = self.get(item_id)
        if item is None:
            return None
        item.status = PanelItemStatus.DENIED
        item.last_decision = decision
        self.update(item)
        return item

    def cancel(self, item_id: str, decision: PanelDecision) -> PermissionPanelItem | None:
        item = self.get(item_id)
        if item is None:
            return None
        item.status = PanelItemStatus.CANCELLED
        item.last_decision = decision
        self.update(item)
        return item

    def clear(self) -> int:
        count = len(self._items)
        self._items.clear()
        return count

    def prune_expired(self) -> int:
        changed = 0
        for item in self._items.values():
            original = item.status
            ensure_status(item)
            if item.status is not original:
                changed += 1
        return changed


class LocalJsonPanelStore(InMemoryPanelStore):
    def __init__(self, path: Path | None = None) -> None:
        super().__init__()
        self.path = (path or _default_store_path()).resolve()
        self._validate_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _validate_path(self) -> None:
        if self.path.suffix.lower() != ".json":
            raise ValueError("panel store path must be a .json file")
        blocked_parts = {".env", ".pem", ".key", ".keystore", ".jks"}
        if any(part.lower() in blocked_parts for part in self.path.parts):
            raise ValueError("blocked panel store path")

    def _load(self) -> None:
        if not self.path.exists():
            return
        raw = self.path.read_text(encoding="utf-8").strip()
        if not raw:
            return
        payload = json.loads(raw)
        items = payload.get("items", [])
        for raw in items[:MAX_STORED_ITEMS]:
            item = PermissionPanelItem.model_validate(raw)
            self._items[item.item_id] = ensure_status(item)

    def _save(self) -> None:
        items = self.list()[:MAX_STORED_ITEMS]
        payload = {"items": [item.model_dump(mode="json") for item in items]}
        temp_path = self.path.with_suffix(".tmp")
        temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_path.replace(self.path)

    def add(self, item: PermissionPanelItem) -> PermissionPanelItem:
        result = super().add(item)
        self._truncate()
        self._save()
        return result

    def update(self, item: PermissionPanelItem) -> PermissionPanelItem:
        result = super().update(item)
        self._save()
        return result

    def clear(self) -> int:
        count = super().clear()
        self._save()
        return count

    def prune_expired(self) -> int:
        changed = super().prune_expired()
        if changed:
            self._save()
        return changed

    def approve(self, item_id: str, decision: PanelDecision) -> PermissionPanelItem | None:
        item = super().approve(item_id, decision)
        self._save()
        return item

    def deny(self, item_id: str, decision: PanelDecision) -> PermissionPanelItem | None:
        item = super().deny(item_id, decision)
        self._save()
        return item

    def cancel(self, item_id: str, decision: PanelDecision) -> PermissionPanelItem | None:
        item = super().cancel(item_id, decision)
        self._save()
        return item

    def _truncate(self) -> None:
        items = self.list()
        if len(items) <= MAX_STORED_ITEMS:
            return
        keep_ids = {item.item_id for item in items[:MAX_STORED_ITEMS]}
        self._items = {item_id: item for item_id, item in self._items.items() if item_id in keep_ids}

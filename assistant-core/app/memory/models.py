"""Memory layer data models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Decision:
    project_name: str
    title: str
    body: str

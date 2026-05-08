"""Sprint 50 — End-to-End Personal Assistant Demo package.

This package provides:
- DemoScenario / DemoResult / DemoReport models
- Built-in demo scenarios covering all major ATLAS preview flows
- DemoRunner that executes scenarios against real services (no real execution)
- Safety policy validation for every result
- Markdown/JSON report generation
"""

from app.demo.models import (
    CommandSurface,
    DemoCategory,
    DemoReport,
    DemoResult,
    DemoScenario,
    DemoStep,
)
from app.demo.runner import DemoRunner
from app.demo.scenarios import BUILTIN_SCENARIOS

__all__ = [
    "CommandSurface",
    "DemoCategory",
    "DemoReport",
    "DemoResult",
    "DemoRunner",
    "DemoScenario",
    "DemoStep",
    "BUILTIN_SCENARIOS",
]

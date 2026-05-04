from __future__ import annotations

import json
from pathlib import Path

from app.config.loader import load_assistant_settings, load_and_validate_configs


def test_ai_settings_default_provider_ollama(isolated_atlas: Path) -> None:
    root = isolated_atlas
    settings_path = root / "configs" / "assistant.settings.json"
    data = json.loads(settings_path.read_text(encoding="utf-8"))
    data["ai"] = {
        "default_provider": "ollama",
        "ollama": {
            "base_url": "http://localhost:11434",
            "default_model": "qwen2.5:7b",
            "timeout_seconds": 300,
            "stream": False,
            "keep_alive": "30m",
        },
    }
    settings_path.write_text(json.dumps(data) + "\n", encoding="utf-8")

    settings = load_assistant_settings(root / "configs")
    assert settings.ai.default_provider == "ollama"
    assert settings.ai.ollama.default_model == "qwen2.5:7b"
    assert settings.ai.ollama.keep_alive == "30m"


def test_ai_settings_do_not_break_full_config_validation(isolated_atlas: Path) -> None:
    settings, _, _, _ = load_and_validate_configs(isolated_atlas / "configs")
    assert settings.ai.default_provider == "ollama"
    assert settings.ai.ollama.timeout_seconds == 300

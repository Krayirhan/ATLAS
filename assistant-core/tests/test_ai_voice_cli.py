from __future__ import annotations

import json
import os

from typer.testing import CliRunner

from app.cli import app


def test_ai_voice_mock_transcript_exit_code_zero() -> None:
    result = CliRunner().invoke(
        app,
        ["ai", "voice", "--project", "ATLAS", "--mock-transcript", "Chrome'u ac"],
        env=os.environ,
    )
    assert result.exit_code == 0, result.output
    assert "action_preview" in result.output


def test_ai_voice_json_outputs_valid_json() -> None:
    result = CliRunner().invoke(
        app,
        ["ai", "voice", "--project", "ATLAS", "--mock-transcript", "Sifrelerimi oku", "--json"],
        env=os.environ,
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["conversation_response"]["response_type"] == "blocked"
    assert payload["execution_attempted"] is False


def test_ai_voice_show_transcript() -> None:
    result = CliRunner().invoke(
        app,
        ["ai", "voice", "--project", "ATLAS", "--mock-transcript", "Isigi ac", "--show-transcript"],
        env=os.environ,
    )
    assert result.exit_code == 0, result.output
    assert "Transcript" in result.output


def test_ai_voice_show_safety() -> None:
    result = CliRunner().invoke(
        app,
        ["ai", "voice", "--project", "ATLAS", "--mock-transcript", "Salon isigini ac", "--show-safety"],
        env=os.environ,
    )
    assert result.exit_code == 0, result.output
    assert "audio_retained: False" in result.output
    assert "mock ses akisi" in result.output.lower()
    assert "gercek mikrofon kullanilmadi" in result.output.lower()


def test_ai_voice_speak_shows_mock_tts() -> None:
    result = CliRunner().invoke(
        app,
        ["ai", "voice", "--project", "ATLAS", "--mock-transcript", "Calisma modunu baslat", "--speak"],
        env=os.environ,
    )
    assert result.exit_code == 0, result.output
    assert "TTS" in result.output


def test_ai_voice_audio_path_without_real_stt_returns_safe_warning() -> None:
    result = CliRunner().invoke(
        app,
        ["ai", "voice", "--project", "ATLAS", "--audio-path", "E:/ATLAS/workspace/fake.wav", "--show-safety"],
        env=os.environ,
    )
    assert result.exit_code == 0, result.output
    assert "audio_path provided but real STT is disabled" in result.output

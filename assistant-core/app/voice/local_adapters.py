from __future__ import annotations

from app.voice.models import SpeechInput, TranscriptResult, TTSRequest, TTSResult


class FasterWhisperSTTAdapter:
    def transcribe(self, input: SpeechInput) -> TranscriptResult:
        return TranscriptResult(
            text="",
            language=input.language,
            confidence=0.0,
            warnings=["faster_whisper_not_installed"],
            error_code="unavailable",
        )

    def health_check(self) -> dict[str, object]:
        return {"ok": False, "engine": "faster_whisper", "reason": "not_installed"}

    def supported_languages(self) -> list[str]:
        return ["tr", "en"]

    def estimated_latency(self) -> dict[str, object]:
        return {"mode": "unavailable"}


class PiperTTSAdapter:
    def synthesize(self, request: TTSRequest) -> TTSResult:
        return TTSResult(
            text=request.text,
            engine="piper",
            success=False,
            spoken=False,
            warnings=["piper_not_installed"],
            error_code="unavailable",
        )

    def speak(self, request: TTSRequest) -> TTSResult:
        return self.synthesize(request)

    def health_check(self) -> dict[str, object]:
        return {"ok": False, "engine": "piper", "reason": "not_installed"}

    def supported_voices(self) -> list[str]:
        return []

    def estimated_latency(self) -> dict[str, object]:
        return {"mode": "unavailable"}


class WindowsTTSAdapter:
    def synthesize(self, request: TTSRequest) -> TTSResult:
        return TTSResult(
            text=request.text,
            engine="windows_tts",
            success=False,
            spoken=False,
            warnings=["windows_tts_not_implemented"],
            error_code="unavailable",
        )

    def speak(self, request: TTSRequest) -> TTSResult:
        return self.synthesize(request)

    def health_check(self) -> dict[str, object]:
        return {"ok": False, "engine": "windows_tts", "reason": "not_implemented"}

    def supported_voices(self) -> list[str]:
        return []

    def estimated_latency(self) -> dict[str, object]:
        return {"mode": "unavailable"}

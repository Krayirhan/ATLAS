from __future__ import annotations

from typing import Protocol

from app.voice.models import SpeechInput, TranscriptResult, TTSRequest, TTSResult


class STTAdapter(Protocol):
    def transcribe(self, input: SpeechInput) -> TranscriptResult:
        ...

    def health_check(self) -> dict[str, object]:
        ...

    def supported_languages(self) -> list[str]:
        ...

    def estimated_latency(self) -> dict[str, object]:
        ...


class TTSAdapter(Protocol):
    def synthesize(self, request: TTSRequest) -> TTSResult:
        ...

    def speak(self, request: TTSRequest) -> TTSResult:
        ...

    def health_check(self) -> dict[str, object]:
        ...

    def supported_voices(self) -> list[str]:
        ...

    def estimated_latency(self) -> dict[str, object]:
        ...

from __future__ import annotations

from app.voice.models import SpeechInput, TranscriptResult, TranscriptSegment, TTSRequest, TTSResult


class MockSTTAdapter:
    def __init__(self, default_confidence: float = 0.95) -> None:
        self.default_confidence = default_confidence

    def transcribe(self, input: SpeechInput) -> TranscriptResult:
        warnings: list[str] = []
        mock_transcript = str(input.metadata.get("mock_transcript", "")).strip()

        if input.audio_path and not mock_transcript:
            warnings.append("audio_path provided but real STT is disabled; mock transcript required")
            return TranscriptResult(
                text="",
                language=input.language,
                confidence=0.0,
                warnings=warnings,
                error_code="mock_transcript_required",
                metadata={"audio_path_ignored": True, "microphone_used": False},
            )

        if input.audio_path:
            warnings.append("audio_path provided; real audio reading is disabled in Sprint 45")

        if not mock_transcript:
            warnings.append("empty mock transcript")
            return TranscriptResult(
                text="",
                language=input.language,
                confidence=0.0,
                warnings=warnings,
                error_code="empty_transcript",
                metadata={"microphone_used": False},
            )

        return TranscriptResult(
            text=mock_transcript,
            language=input.language,
            confidence=float(input.metadata.get("confidence", self.default_confidence)),
            segments=[
                TranscriptSegment(
                    start_ms=0,
                    end_ms=input.duration_ms,
                    text=mock_transcript,
                    confidence=float(input.metadata.get("confidence", self.default_confidence)),
                )
            ],
            is_final=True,
            warnings=warnings,
            metadata={"microphone_used": False, "engine": "mock_stt"},
        )

    def health_check(self) -> dict[str, object]:
        return {"ok": True, "engine": "mock_stt", "microphone_used": False}

    def supported_languages(self) -> list[str]:
        return ["tr", "en"]

    def estimated_latency(self) -> dict[str, object]:
        return {"mode": "mock", "expected_ms": 10}


class MockTTSAdapter:
    def synthesize(self, request: TTSRequest) -> TTSResult:
        return TTSResult(
            text=request.text,
            audio_output_path=None,
            engine="mock_tts",
            duration_ms=0,
            success=True,
            spoken=False,
            warnings=["mock_tts_no_audio_output"],
            metadata={"played_audio": False},
        )

    def speak(self, request: TTSRequest) -> TTSResult:
        result = self.synthesize(request)
        result.warnings.append("mock_tts_speak_no_playback")
        return result

    def health_check(self) -> dict[str, object]:
        return {"ok": True, "engine": "mock_tts", "audio_output": False}

    def supported_voices(self) -> list[str]:
        return ["default"]

    def estimated_latency(self) -> dict[str, object]:
        return {"mode": "mock", "expected_ms": 10}

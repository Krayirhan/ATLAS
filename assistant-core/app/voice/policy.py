from __future__ import annotations

from app.voice.models import TranscriptResult


def should_accept_transcript(transcript: TranscriptResult) -> bool:
    return bool(transcript.text.strip()) and transcript.confidence >= 0.60 and not transcript.error_code


def requires_clarification(transcript: TranscriptResult) -> bool:
    if not transcript.text.strip():
        return True
    return transcript.confidence < 0.80 or bool(transcript.error_code)


def build_low_confidence_message(transcript: TranscriptResult) -> str:
    return (
        f"Sesli komut dusuk guvenle algilandi (confidence={transcript.confidence:.2f}). "
        "Lutfen komutu tekrar soyle veya metin olarak belirt."
    )


def voice_safety_metadata(transcript: TranscriptResult) -> dict[str, object]:
    return {
        "audio_retained": False,
        "microphone_used": False,
        "wake_word_used": False,
        "execution_attempted": False,
        "transcript_confidence": transcript.confidence,
        "transcript_error_code": transcript.error_code,
    }

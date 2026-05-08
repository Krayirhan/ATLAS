from __future__ import annotations

from app.conversation.models import ConversationResponse, ConversationResponseType
from app.voice.models import TranscriptResult


def should_accept_transcript(transcript: TranscriptResult) -> bool:
    return bool(transcript.text.strip()) and transcript.confidence >= 0.60 and not transcript.error_code


def requires_clarification(transcript: TranscriptResult) -> bool:
    if not transcript.text.strip():
        return True
    return transcript.confidence < 0.80 or bool(transcript.error_code)


def build_low_confidence_message(transcript: TranscriptResult) -> str:
    return (
        f"Sesli komut olarak algilandi ancak guven dusuk (confidence={transcript.confidence:.2f}). "
        "Lutfen komutu daha acik tekrar soyle veya metin olarak belirt. Gercek islem yapilmadi."
    )


def voice_safety_metadata(transcript: TranscriptResult) -> dict[str, object]:
    return {
        "audio_retained": False,
        "microphone_used": False,
        "wake_word_used": False,
        "execution_attempted": False,
        "transcript_confidence": transcript.confidence,
        "transcript_error_code": transcript.error_code,
        "mock_voice_pipeline": True,
    }


def apply_runtime_voice_safety(response: ConversationResponse) -> ConversationResponse:
    metadata = dict(response.metadata)
    warnings = list(response.warnings)
    risk_level = ""
    if response.permission_decision is not None:
        risk_level = getattr(response.permission_decision.risk_level, "value", str(response.permission_decision.risk_level))
    elif response.metadata.get("risk_level"):
        risk_level = str(response.metadata.get("risk_level"))

    metadata["voice_confirmation_policy"] = {
        "explicit_confirmation_required": response.response_type is ConversationResponseType.CONFIRMATION_REQUIRED,
        "simple_yes_allowed": False if response.response_type is ConversationResponseType.CONFIRMATION_REQUIRED else True,
        "target_repeat_required": risk_level == "high",
    }
    metadata["voice_runtime_note"] = "Sesli komut olarak algilandi."

    if not response.assistant_message.startswith("Sesli komut olarak algilandi."):
        response.assistant_message = f"Sesli komut olarak algilandi. {response.assistant_message}"

    if response.response_type is ConversationResponseType.CONFIRMATION_REQUIRED:
        warnings.append("Voice kaynagi icin acik confirmation gerekiyor; gercek islem yapilmadi.")
        if risk_level == "high":
            warnings.append("Yuksek riskli voice isteginde kisa 'evet' kabul edilmez.")
        else:
            warnings.append("Bu voice isteginde hedefi ve islemi belirten net bir onay beklenir.")

    response.warnings = warnings
    response.metadata = metadata
    return response

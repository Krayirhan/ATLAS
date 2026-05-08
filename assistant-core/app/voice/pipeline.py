from __future__ import annotations

import uuid

from app.actions.types import ActionSource
from app.conversation.loop import ConversationLoop
from app.conversation.models import ConversationResponse, ConversationResponseType
from app.voice.contracts import STTAdapter, TTSAdapter
from app.voice.models import SpeechInput, TTSRequest, VoicePipelineRequest, VoicePipelineResult
from app.voice.policy import (
    apply_runtime_voice_safety,
    build_low_confidence_message,
    requires_clarification,
    should_accept_transcript,
    voice_safety_metadata,
)


class VoicePipeline:
    def __init__(self, stt_adapter: STTAdapter, tts_adapter: TTSAdapter, conversation_loop: ConversationLoop | None = None) -> None:
        self.stt_adapter = stt_adapter
        self.tts_adapter = tts_adapter
        self.conversation_loop = conversation_loop or ConversationLoop()

    def handle(self, request: VoicePipelineRequest) -> VoicePipelineResult:
        session_id = request.session_id or str(uuid.uuid4())
        speech_input = SpeechInput(
            source=request.source,
            audio_path=request.audio_path,
            audio_format=self._detect_audio_format(request.audio_path),
            language=request.language,
            duration_ms=0,
            push_to_talk=True,
            metadata={"mock_transcript": request.mock_transcript or "", **request.metadata},
        )
        transcript = self.stt_adapter.transcribe(speech_input)
        safety_warnings = list(transcript.warnings)
        metadata = voice_safety_metadata(transcript)
        metadata.update({"session_id": session_id, "project_name": request.project_name, "source": request.source.value})

        if not should_accept_transcript(transcript) or requires_clarification(transcript):
            assistant_message = build_low_confidence_message(transcript)
            if not transcript.text.strip() and transcript.error_code:
                assistant_message = "Sesli komut guvenli sekilde islenemedi. Mock transcript sagla veya metin komutu kullan."
            response = ConversationResponse(
                session_id=session_id,
                user_message=transcript.text,
                assistant_message=assistant_message,
                response_type=ConversationResponseType.CLARIFICATION if transcript.text.strip() else ConversationResponseType.ERROR,
                clarification_required=True,
                warnings=safety_warnings,
                metadata={"voice_source": request.source.value, "transcript_confidence": transcript.confidence},
            )
            tts_result = self._build_tts_result(request, response.assistant_message)
            return VoicePipelineResult(
                transcript=transcript,
                conversation_response=response,
                tts_result=tts_result,
                safety_warnings=safety_warnings,
                audio_retained=False,
                microphone_used=False,
                wake_word_used=False,
                execution_attempted=False,
                metadata=metadata,
            )

        response = self.conversation_loop.handle_text(
            message=transcript.text,
            project_name=request.project_name,
            session_id=session_id,
            source=ActionSource.VOICE,
        )
        response = apply_runtime_voice_safety(response)
        response.metadata["voice_source"] = request.source.value
        response.metadata["transcript_confidence"] = transcript.confidence
        tts_result = self._build_tts_result(request, response.assistant_message)

        return VoicePipelineResult(
            transcript=transcript,
            conversation_response=response,
            tts_result=tts_result,
            safety_warnings=safety_warnings,
            audio_retained=False,
            microphone_used=False,
            wake_word_used=False,
            execution_attempted=False,
            metadata=metadata,
        )

    def _build_tts_result(self, request: VoicePipelineRequest, text: str):
        if not request.speak:
            return None
        return self.tts_adapter.speak(TTSRequest(text=text, language=request.language, metadata={"mock": True}))

    def _detect_audio_format(self, audio_path: str | None) -> str:
        if not audio_path:
            return "mock"
        return audio_path.rsplit(".", 1)[-1].lower() if "." in audio_path else "unknown"

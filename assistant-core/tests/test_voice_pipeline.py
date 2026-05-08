from app.conversation.models import ConversationResponseType
from app.voice.mock_adapters import MockSTTAdapter, MockTTSAdapter
from app.voice.pipeline import VoicePipeline
from app.voice.models import VoicePipelineRequest, VoiceSource
from app.voice.policy import requires_clarification, should_accept_transcript, voice_safety_metadata


def test_mock_stt_returns_transcript() -> None:
    result = MockSTTAdapter().transcribe(
        input=__import__("app.voice.models", fromlist=["SpeechInput"]).SpeechInput(
            source=VoiceSource.MOCK_TRANSCRIPT,
            language="tr",
            metadata={"mock_transcript": "Chrome'u ac"},
        )
    )
    assert result.text == "Chrome'u ac"
    assert result.confidence == 0.95


def test_mock_tts_does_not_create_audio() -> None:
    result = MockTTSAdapter().speak(__import__("app.voice.models", fromlist=["TTSRequest"]).TTSRequest(text="Merhaba"))
    assert result.success is True
    assert result.audio_output_path is None
    assert result.spoken is False


def test_voice_policy_accepts_high_confidence() -> None:
    transcript = __import__("app.voice.models", fromlist=["TranscriptResult"]).TranscriptResult(text="Chrome'u ac", confidence=0.95)
    assert should_accept_transcript(transcript) is True
    assert requires_clarification(transcript) is False


def test_voice_policy_requires_clarification_for_low_confidence() -> None:
    transcript = __import__("app.voice.models", fromlist=["TranscriptResult"]).TranscriptResult(text="Chrome'u ac", confidence=0.40)
    assert should_accept_transcript(transcript) is False
    assert requires_clarification(transcript) is True
    metadata = voice_safety_metadata(transcript)
    assert metadata["audio_retained"] is False
    assert metadata["microphone_used"] is False
    assert metadata["wake_word_used"] is False


def test_voice_pipeline_chrome_returns_action_preview() -> None:
    pipeline = VoicePipeline(MockSTTAdapter(), MockTTSAdapter())
    result = pipeline.handle(VoicePipelineRequest(project_name="ATLAS", mock_transcript="Chrome'u aç"))
    assert result.conversation_response is not None
    assert result.conversation_response.response_type == ConversationResponseType.ACTION_PREVIEW
    assert result.execution_attempted is False
    assert result.audio_retained is False
    assert result.microphone_used is False
    assert result.wake_word_used is False


def test_voice_pipeline_device_turn_on_requires_confirmation() -> None:
    pipeline = VoicePipeline(MockSTTAdapter(), MockTTSAdapter())
    result = pipeline.handle(VoicePipelineRequest(project_name="ATLAS", mock_transcript="Salon ışığını aç"))
    assert result.conversation_response is not None
    assert result.conversation_response.response_type == ConversationResponseType.CONFIRMATION_REQUIRED
    assert "Sesli komut olarak algilandi." in result.conversation_response.assistant_message
    assert any("confirmation gerekiyor" in warning for warning in result.conversation_response.warnings)


def test_voice_pipeline_ambiguous_requires_clarification() -> None:
    pipeline = VoicePipeline(MockSTTAdapter(), MockTTSAdapter())
    result = pipeline.handle(VoicePipelineRequest(project_name="ATLAS", mock_transcript="Işığı aç"))
    assert result.conversation_response is not None
    assert result.conversation_response.response_type == ConversationResponseType.CLARIFICATION


def test_voice_pipeline_blocked_stays_blocked() -> None:
    pipeline = VoicePipeline(MockSTTAdapter(), MockTTSAdapter())
    result = pipeline.handle(VoicePipelineRequest(project_name="ATLAS", mock_transcript="Şifrelerimi oku"))
    assert result.conversation_response is not None
    assert result.conversation_response.response_type == ConversationResponseType.BLOCKED


def test_voice_pipeline_routine_requires_confirmation() -> None:
    pipeline = VoicePipeline(MockSTTAdapter(), MockTTSAdapter())
    result = pipeline.handle(VoicePipelineRequest(project_name="ATLAS", mock_transcript="Çalışma modunu başlat"))
    assert result.conversation_response is not None
    assert result.conversation_response.response_type == ConversationResponseType.CONFIRMATION_REQUIRED


def test_voice_pipeline_with_speak_returns_mock_tts() -> None:
    pipeline = VoicePipeline(MockSTTAdapter(), MockTTSAdapter())
    result = pipeline.handle(VoicePipelineRequest(project_name="ATLAS", mock_transcript="Chrome'u aç", speak=True))
    assert result.tts_result is not None
    assert result.tts_result.audio_output_path is None


def test_voice_pipeline_audio_path_without_real_stt_is_safe_error() -> None:
    pipeline = VoicePipeline(MockSTTAdapter(), MockTTSAdapter())
    result = pipeline.handle(VoicePipelineRequest(project_name="ATLAS", audio_path="E:/ATLAS/workspace/fake.wav", source=VoiceSource.AUDIO_FILE))
    assert result.conversation_response is not None
    assert result.conversation_response.response_type == ConversationResponseType.ERROR
    assert result.execution_attempted is False


def test_voice_pipeline_low_confidence_requires_clarification_message() -> None:
    pipeline = VoicePipeline(MockSTTAdapter(), MockTTSAdapter())
    result = pipeline.handle(
        VoicePipelineRequest(
            project_name="ATLAS",
            mock_transcript="Chrome'u ac",
            metadata={"confidence": 0.40},
        )
    )
    assert result.conversation_response is not None
    assert result.conversation_response.response_type == ConversationResponseType.CLARIFICATION
    assert "guven dusuk" in result.conversation_response.assistant_message.lower()


def test_voice_pipeline_high_risk_short_yes_not_allowed() -> None:
    pipeline = VoicePipeline(MockSTTAdapter(), MockTTSAdapter())
    result = pipeline.handle(VoicePipelineRequest(project_name="ATLAS", mock_transcript="Bilgisayari kapat"))
    assert result.conversation_response is not None
    assert result.conversation_response.response_type == ConversationResponseType.CONFIRMATION_REQUIRED
    assert any("kisa 'evet'" in warning for warning in result.conversation_response.warnings)

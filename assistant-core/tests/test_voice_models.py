from app.voice.models import SpeechInput, TTSRequest, TTSResult, TranscriptResult, VoicePipelineRequest, VoicePipelineResult, VoiceSource


def test_speech_input_can_be_created() -> None:
    model = SpeechInput(source=VoiceSource.MOCK_TRANSCRIPT, language="tr", push_to_talk=True)
    assert model.source is VoiceSource.MOCK_TRANSCRIPT


def test_transcript_result_can_be_created() -> None:
    result = TranscriptResult(text="Chrome'u ac", confidence=0.95)
    assert result.text == "Chrome'u ac"
    assert result.confidence == 0.95


def test_tts_request_and_result_can_be_created() -> None:
    request = TTSRequest(text="Merhaba")
    result = TTSResult(text=request.text, success=True, spoken=False)
    assert result.text == "Merhaba"
    assert result.audio_output_path is None


def test_voice_pipeline_request_and_result_can_be_created() -> None:
    request = VoicePipelineRequest(project_name="ATLAS", mock_transcript="Chrome'u ac")
    result = VoicePipelineResult(
        transcript=TranscriptResult(text="Chrome'u ac", confidence=0.95),
        conversation_response=None,
    )
    assert request.project_name == "ATLAS"
    assert result.audio_retained is False

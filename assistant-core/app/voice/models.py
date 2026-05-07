from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.conversation.models import ConversationResponse


class VoiceSource(str, Enum):
    PUSH_TO_TALK = "push_to_talk"
    MOCK_TRANSCRIPT = "mock_transcript"
    AUDIO_FILE = "audio_file"
    UNKNOWN = "unknown"


class TranscriptSegment(BaseModel):
    start_ms: int = 0
    end_ms: int = 0
    text: str = ""
    confidence: float = 0.0


class SpeechInput(BaseModel):
    source: VoiceSource = VoiceSource.UNKNOWN
    audio_path: str | None = None
    audio_format: str = "unknown"
    language: str = "tr"
    duration_ms: int = 0
    push_to_talk: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class TranscriptResult(BaseModel):
    text: str = ""
    language: str = "tr"
    confidence: float = 0.0
    segments: list[TranscriptSegment] = Field(default_factory=list)
    is_final: bool = True
    warnings: list[str] = Field(default_factory=list)
    error_code: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class TTSRequest(BaseModel):
    text: str
    language: str = "tr"
    voice: str = "default"
    speed: float = 1.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class TTSResult(BaseModel):
    text: str
    audio_output_path: str | None = None
    engine: str = "mock"
    duration_ms: int = 0
    success: bool = True
    spoken: bool = False
    warnings: list[str] = Field(default_factory=list)
    error_code: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class VoicePipelineRequest(BaseModel):
    project_name: str
    mock_transcript: str | None = None
    audio_path: str | None = None
    language: str = "tr"
    session_id: str | None = None
    speak: bool = False
    source: VoiceSource = VoiceSource.MOCK_TRANSCRIPT
    metadata: dict[str, Any] = Field(default_factory=dict)


class VoiceTurn(BaseModel):
    transcript: TranscriptResult
    response: ConversationResponse | None = None
    tts_result: TTSResult | None = None
    safety_warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class VoicePipelineResult(BaseModel):
    transcript: TranscriptResult
    conversation_response: ConversationResponse | None = None
    tts_result: TTSResult | None = None
    safety_warnings: list[str] = Field(default_factory=list)
    audio_retained: bool = False
    microphone_used: bool = False
    wake_word_used: bool = False
    execution_attempted: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

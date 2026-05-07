# 36 Conversation Loop MVP

## Sprint 41
The goal of Sprint 41 was to implement the first conversational loop for ATLAS, focusing on text-first personal control. This integrates the IntentRouter, PermissionManager, and PCControlAdapter into a state-aware conversation loop.

### ConversationLoop Role
The `ConversationLoop` is the central component that coordinates the user's input with the rest of the system. It handles parsing the intent, validating permissions, building a PC control plan, generating a safe response, and maintaining session state.

### Response Types
The loop produces `ConversationResponse` objects with `ConversationResponseType` to indicate the nature of the reply:
- `answer`: A direct response to a question or status inquiry.
- `action_preview`: A preview of a low-risk action that would be executed (mocked in MVP).
- `clarification`: A request for more information when the intent is ambiguous or unknown.
- `confirmation_required`: A prompt for explicit confirmation for medium/high-risk actions.
- `blocked`: A notification that the requested action is blocked by safety policies.
- `unsupported`: The intent cannot be safely classified.

### Conversation State
The `ConversationState` is an in-memory representation of the session, tracking:
- `session_id`
- `last_intent`
- `last_action`
- `pending_clarification`
- `pending_confirmation`
- List of `ConversationTurn` representing interaction history.

### CLI
The `ai chat` CLI command exposes the ConversationLoop:
```bash
python -m app.cli ai chat --project ATLAS "Chrome'u aç"
python -m app.cli ai chat --project ATLAS "Işığı aç"
python -m app.cli ai chat --project ATLAS "Şifrelerimi oku"
```
It supports `--json`, `--show-state`, `--session-id`, and `--reset-session`.

### Execution Boundary
- **Real App/Browser/Folder open**: NO
- **Home Control Execution**: NO
- **Voice/STT/TTS**: NO
- **Terminal Execution**: NO

### Sprint 42 Outcome
Personal Memory & Preferences now feed the ConversationLoop before the normal action path.

### Sprint 43 Outcome
RoutineEngine preview support is now integrated into the ConversationLoop:

- `Calisma modunu baslat` returns routine preview / confirmation-safe output
- `Rutinleri goster` returns built-in routine list
- routine requests stay preview-only

### Sprint 44 Dependency Result
Sprint 44 now defines how a future voice layer will feed `ConversationLoop`:

- push-to-talk transcript becomes the input message
- low transcript confidence returns clarification before action routing
- no direct microphone runtime exists yet

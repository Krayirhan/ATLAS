# 37 Personal Memory & Preferences

## Sprint 42
The objective of Sprint 42 was to implement a privacy-first, local-only memory and preference management system for ATLAS.

### PersonalMemoryService Role
The `PersonalMemoryService` coordinates operations to read, write, and forget personal memory items based on conversational inputs or explicit CLI requests. It evaluates intents using the `MemoryIntentParser` and enforces safety through `SensitiveMemoryPolicy`.

### Memory Types
- `preference`
- `device_alias`
- `room_alias`
- `routine_preference`
- `reminder_preference`
- `assistant_setting`
- `user_note`

### Sensitivity Model
- `public`
- `normal`
- `private`
- `sensitive`
- `blocked`

### Sensitive Memory Policy
The system blocks the storage of highly sensitive data. Blocked examples include:
- `şifre`, `password`, `token`, `api key`
- `tc kimlik`, `kredi kartı`, `banka şifresi`, `seed phrase`

Blocked memory is never stored.

### ConversationLoop Integration
- **Remember flow**: Triggered by "bunu hatırla: ...". Safe items are stored.
- **Forget flow**: Triggered by "... unut". Finds and deletes the item.
- **Show flow**: Triggered by "Neleri hatırlıyorsun?". Displays non-blocked memory summary.
- The normal execution flow (`pc.open_app` etc.) remains functional and is evaluated after the memory layer.

### CLI
The `ai memory-personal` command enables explicit interaction.
```bash
python -m app.cli ai memory-personal --project ATLAS "Bunu hatırla: Chrome kullanırım"
python -m app.cli ai memory-personal --project ATLAS "Neleri hatırlıyorsun?"
```

### Privacy Rules
- **No automatic write**: The system never records conversation history into memory without an explicit "remember" intent.
- **Local only**: No cloud syncing, no external DB.
- **Forget policy**: Explicit removal purges the item completely.

### Sprint 43 Dependency
Sprint 43 will introduce the `RoutineEngine MVP`, which will consume `routine_preference` memory items to execute multi-step personal routines.

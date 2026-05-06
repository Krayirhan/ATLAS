# ATLAS - Risk List

## Product Direction Risks

1. **Target drift** - ATLAS can drift back into developer-tooling if CodeReviewer, ReportAgent, Git hygiene, or coding-agent ideas drive the roadmap again.
2. **Too-early coding automation** - CodeBuilder, BugFix, Refactor, or autonomous coding work can bypass the personal control assistant goal.
3. **Premature UI or RAG work** - Desktop UI or vector/RAG work can consume time before action, permission, and privacy contracts are ready.

## Intent and Voice Risks

4. **Wrong intent extraction** - A user command can be mapped to the wrong action.
5. **Voice misrecognition** - Speech-to-text can mishear Turkish commands or action targets.
6. **Wake word / always-listening privacy** - Continuous microphone listening can create privacy risk and user trust loss.
7. **Conversation state drift** - Multi-turn context can cause the assistant to apply an old target or stale user intent.

## Action and Control Risks

8. **Risky PC action** - File operations, shutdown, installs, admin commands, or registry edits can damage the user environment.
9. **Wrong home device control** - A room/device alias can resolve to the wrong physical device.
10. **Unauthorized action** - Medium/high risk actions can run without explicit confirmation if permission gates are incomplete.
11. **Irreversible action** - Destructive action may not be reversible or auditable.
12. **Windows permission issues** - UAC, focus control, app launch, media control, and file system permissions may fail or behave inconsistently.

## Privacy and Data Risks

13. **Secret leakage via AI path** - `.env`, keys, keystores, browser profiles, and raw logs must remain blocked.
14. **Personal data leakage** - Personal memory, preferences, routines, devices, and command history can expose sensitive behavior.
15. **NotebookLM data mistake** - Manual exports can accidentally include private or secret data.
16. **Full disk exposure** - MCP or future file adapters must not expose `C:\Users`, full disks, or blocked roots.
17. **D: drive legacy problem** - `D:\ATLAS` and writes to `D:` remain blocked by policy.

## Runtime and Reliability Risks

18. **Local model latency** - Ollama model load or slow generation can make the assistant feel unresponsive.
19. **Ollama warmup/load time** - Cold model start can delay the first answer.
20. **Agent route error** - MainAgent or future IntentRouter can choose the wrong sub-agent or action route.
21. **Audit depth mismatch** - Static audits can pass while a future runtime action path is unsafe.
22. **Knowledge-base drift** - Roadmap/status docs can become stale and mislead AI answers.

## Current Controls

- Safety policy blocks secret files, dangerous commands, blocked paths, and `D:\ATLAS`.
- Current agents are read-only.
- MCP filesystem config is bounded to `E:\ATLAS\workspace`.
- AI context loader uses bounded selected sources.
- ToolApprovalAgent previews command/file/tool proposals and blocks known dangerous commands.
- SecurityAuditorAgent checks agent capability, MCP exposure, approval policy, context, and docs.

## Missing Controls

- Intent confidence model.
- Action schema.
- PermissionManager.
- Voice confirmation policy.
- PC control adapter safety contract.
- Device registry and room model.
- Personal memory privacy policy.
- Routine preview and cancellation.
- Desktop permission panel.

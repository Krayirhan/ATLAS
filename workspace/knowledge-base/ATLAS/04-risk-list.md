# ATLAS - Risk List

## Product Direction Risks

1. **Target drift** - ATLAS can drift back into developer-tooling if CodeReviewer, ReportAgent, Git hygiene, or coding-agent ideas drive the roadmap again.
2. **Too-early coding automation** - CodeBuilder, BugFix, Refactor, or autonomous coding work can bypass the personal control assistant goal.
3. **Premature UI or RAG work** - Desktop UI or vector/RAG work can consume time before action, permission, and privacy contracts are ready.

## Intent and Voice Risks

4. **Wrong intent extraction** - A user command can be mapped to the wrong action.
5. **Ambiguous intent** - A vague command such as `Isigi ac` may omit room, device, or value and must not produce an executable action.
6. **Wrong target resolution** - An alias may resolve to the wrong folder, app, routine, or physical device.
7. **Low confidence routing** - Low confidence classification may still look plausible and must be routed to clarification or safe fallback.
8. **Voice misrecognition** - Speech-to-text can mishear Turkish commands or action targets.
9. **Voice-source action risk** - A risky voice command can be confirmed accidentally if repeat-back, timeout, and cancel are weak.
10. **Wake word / always-listening privacy** - Continuous microphone listening can create privacy risk and user trust loss.
11. **Conversation state drift** - Multi-turn context can cause the assistant to apply an old target or stale user intent.

## Action and Control Risks

12. **Action risk misclassification** - A medium/high or blocked action can be classified as low and bypass approval.
13. **Permission decision mismatch** - `PermissionDecision` can disagree with the candidate risk or preview if contracts drift.
14. **Action preview wrong information** - A preview can show the wrong target, expected effect, or reversibility.
15. **Stale risk classification** - A previously low-risk action can become risky after target, source, or parameters change.
16. **Risky PC action** - File operations, shutdown, installs, admin commands, or registry edits can damage the user environment.
17. **Wrong home device control** - A room/device alias can resolve to the wrong physical device.
18. **Unauthorized action** - Medium/high risk actions can run without explicit confirmation if permission gates are incomplete.
19. **Confirmation bypass** - A future adapter could run an action without a valid `ActionPreview` and approval decision.
20. **Voice confirmation ambiguity** - A user may confirm a misunderstood voice action if repeat-back or confidence handling is weak.
21. **Blocked action bypass** - A blocked action such as `secret.read`, `file.delete`, or unrestricted shell execution could reach an adapter.
22. **Adapter execution before PermissionManager** - Adapter code could be added before permission decisions are mandatory.
23. **Adapter execution without preview** - Medium/high actions could execute without showing target, effect, risk, and warnings.
24. **Medium/high action accidental execution** - A future action may execute after preview but before explicit confirmation.
25. **Action result/audit missing** - Future actions could complete without durable status, error, or audit metadata.
26. **Audit metadata missing fields** - `action_id`, risk, source, decision, target summary, or `execution_attempted=false` could be omitted.
27. **Irreversible action** - Destructive action may not be reversible or auditable.
28. **Windows permission issues** - UAC, focus control, app launch, media control, and file system permissions may fail or behave inconsistently.

## Privacy and Data Risks

29. **Secret leakage via AI path** - `.env`, keys, keystores, browser profiles, and raw logs must remain blocked.
30. **Personal data leakage** - Personal memory, preferences, routines, devices, and command history can expose sensitive behavior.
31. **NotebookLM data mistake** - Manual exports can accidentally include private or secret data.
32. **Full disk exposure** - MCP or future file adapters must not expose `C:\Users`, full disks, or blocked roots.
33. **D: drive legacy problem** - `D:\ATLAS` and writes to `D:` remain blocked by policy.

## Runtime and Reliability Risks

34. **Local model latency** - Ollama model load or slow generation can make the assistant feel unresponsive.
35. **Ollama warmup/load time** - Cold model start can delay the first answer.
36. **Agent route error** - MainAgent or future IntentRouter can choose the wrong sub-agent or action route.
37. **Audit depth mismatch** - Static audits can pass while a future runtime action path is unsafe.
38. **Knowledge-base drift** - Roadmap/status docs can become stale and mislead AI answers.

## Current Controls

- Safety policy blocks secret files, dangerous commands, blocked paths, and `D:\ATLAS`.
- Current agents are read-only.
- MCP filesystem config is bounded to `E:\ATLAS\workspace`.
- AI context loader uses bounded selected sources.
- ToolApprovalAgent previews command/file/tool proposals and blocks known dangerous commands.
- SecurityAuditorAgent checks agent capability, MCP exposure, approval policy, context, and docs.
- Sprint 37 `app/actions` schema marks blocked actions as non-executable by contract.
- Sprint 37 risk model requires confirmation for medium/high actions by contract.
- Sprint 37 clarification model sets ambiguous commands to `no_action`.
- Sprint 38 PermissionManager turns action candidates into preview, confirmation, block, clarification, deny, cancel, and audit-ready decisions.
- Sprint 38 audit metadata sets `execution_attempted=false`.

## Missing Controls

- Runtime `IntentRouter`.
- Runtime `ActionRouter`.
- Adapter allowlist and execution guard.
- Confirmation timeout/cancel implementation.
- Voice confirmation policy runtime.
- PC control adapter safety contract implementation.
- Device registry and room model runtime.
- Personal memory privacy runtime.
- Routine preview and cancellation runtime.
- Desktop permission panel.
- Durable action audit log.

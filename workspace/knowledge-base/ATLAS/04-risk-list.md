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
12. **Entity extraction error** - App, room, folder, routine, date, or numeric value extraction can be wrong.
13. **Malicious phrasing** - User text may look like a natural request while attempting shell-like, destructive, or policy-bypass behavior.
14. **Command injection-like user text** - Symbols or phrasing such as `;`, `&&`, `|`, or PowerShell-like text must not be treated as executable intent.
15. **Overconfident routing** - Deterministic matches can classify too aggressively and skip clarification.

## Action and Control Risks

16. **Intent misclassification** - A supported phrase can be mapped to the wrong intent category.
17. **Ambiguous target execution** - A vague request may accidentally resolve to a concrete target later if guardrails regress.
18. **Action risk misclassification** - A medium/high or blocked action can be classified as low and bypass approval.
19. **Permission decision mismatch** - `PermissionDecision` can disagree with the candidate risk or preview if contracts drift.
20. **Action preview wrong information** - A preview can show the wrong target, expected effect, or reversibility.
21. **Stale risk classification** - A previously low-risk action can become risky after target, source, or parameters change.
22. **Risky PC action** - File operations, shutdown, installs, admin commands, or registry edits can damage the user environment.
23. **Wrong home device control** - A room/device alias can resolve to the wrong physical device.
24. **Unauthorized action** - Medium/high risk actions can run without explicit confirmation if permission gates are incomplete.
25. **Confirmation bypass** - A future adapter could run an action without a valid `ActionPreview` and approval decision.
26. **Voice confirmation ambiguity** - A user may confirm a misunderstood voice action if repeat-back or confidence handling is weak.
27. **Blocked intent bypass** - A blocked phrase such as `secret.read`, `file.delete`, or shell-like text could slip through the router.
28. **Blocked action bypass** - A blocked action such as `secret.read`, `file.delete`, or unrestricted shell execution could reach an adapter.
29. **Adapter execution before PermissionManager** - Adapter code could be added before permission decisions are mandatory.
30. **Adapter execution without preview** - Medium/high actions could execute without showing target, effect, risk, and warnings.
31. **Medium/high action accidental execution** - A future action may execute after preview but before explicit confirmation.
32. **Action result/audit missing** - Future actions could complete without durable status, error, or audit metadata.
33. **Audit metadata missing fields** - `action_id`, risk, source, decision, target summary, or `execution_attempted=false` could be omitted.
34. **Irreversible action** - Destructive action may not be reversible or auditable.
35. **Windows permission issues** - UAC, focus control, app launch, media control, and file system permissions may fail or behave inconsistently.
36. **Adapter bypass** - Execution could happen outside of the PCControlAdapter safety gates.
37. **Arbitrary command injection** - User input could be injected into shell execution or app arguments.
38. **Unsafe app launch** - Launching unintended or dangerous applications.
39. **Unsafe folder path** - Opening restricted directories.
40. **Full disk scan** - File search could hit unbounded system paths causing slowdowns or crashes.
41. **Shell executor creep** - Expanding shell usage beyond bounded safe commands.
42. **Dry-run and execution mixup** - An action marked as dry-run might accidentally perform side effects.
43. **Permission decision ignored** - Adapter executing an action that is blocked or lacking allowed status.
44. **Unsupported action accidentally executed** - Adapter attempting to execute an action it doesn't officially support.
45. **Media/volume side effect risk** - Unintended playback or system-wide volume changes without user visibility.

## Privacy and Data Risks

36. **Secret leakage via AI path** - `.env`, keys, keystores, browser profiles, and raw logs must remain blocked.
37. **Personal data leakage** - Personal memory, preferences, routines, devices, and command history can expose sensitive behavior.
38. **NotebookLM data mistake** - Manual exports can accidentally include private or secret data.
39. **Full disk exposure** - MCP or future file adapters must not expose `C:\Users`, full disks, or blocked roots.
40. **D: drive legacy problem** - `D:\ATLAS` and writes to `D:` remain blocked by policy.

## Runtime and Reliability Risks

41. **Local model latency** - Ollama model load or slow generation can make the assistant feel unresponsive.
42. **Ollama warmup/load time** - Cold model start can delay the first answer.
43. **Agent route error** - MainAgent or future IntentRouter can choose the wrong sub-agent or action route.
44. **Audit depth mismatch** - Static audits can pass while a future runtime action path is unsafe.
45. **Knowledge-base drift** - Roadmap/status docs can become stale and mislead AI answers.

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
- Sprint 39 IntentRouter keeps MVP parsing deterministic and local; no LLM or adapter path is used.
- Sprint 39 blocks shell-like or secret-reading phrasing at the router layer before any execution boundary exists.
- Sprint 40 PCControlAdapter enforces safety gates, `PermissionDecision` adherence, and returns dry-run plans without arbitrary shell execution.

## Missing Controls

- Runtime `IntentRouter`.
- Runtime `ActionRouter`.
- Adapter allowlist and execution guard.
- Confirmation timeout/cancel implementation.
- Voice confirmation policy runtime.
- Device registry and room model runtime.
- Personal memory privacy runtime.
- Routine preview and cancellation runtime.
- Desktop permission panel.
- Durable action audit log.

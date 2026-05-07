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
16. **STT misrecognition** - Spoken Turkish input can be transcribed into the wrong command, target, or number.
17. **Low transcript confidence** - A plausible-looking transcript can still be too uncertain for safe action preview.
18. **False positive wake word** - A future wake detector may activate unintentionally and route unwanted speech.
19. **Raw audio retention** - Stored microphone captures could become a privacy and secret-handling risk.
20. **Transcript contains sensitive data** - Spoken secrets may appear in transcript text even if the user did not intend memory storage.
21. **Background noise** - Environmental sound can corrupt targets, confirmations, or cancellation phrases.
22. **Language mismatch** - The STT engine may detect or transcribe the wrong language under mixed Turkish/English utterances.
23. **Voice command injection** - Spoken shell-like or destructive phrasing may look natural but still map to blocked intent classes.
24. **Transcript hallucination** - The STT layer may produce a fluent but incorrect transcript that looks trustworthy.
25. **Mock vs real STT confusion** - Users or developers may treat mock transcript results as evidence of real audio support.
26. **Audio path privacy** - An audio path handed to the CLI may be mistaken for approved file ingestion even though audio reading is disabled.
27. **Accidental audio retention** - Future debugging changes may start retaining raw audio unexpectedly.
28. **TTS output misleading execution status** - Spoken feedback may sound like an action was executed when only preview happened.
29. **Wake word creep** - Convenience pressure may reintroduce wake word before false-positive and privacy controls are ready.
30. **Always-listening creep** - Background listening may slip into scope before opt-in and retention controls are stable.

## Action and Control Risks

31. **Intent misclassification** - A supported phrase can be mapped to the wrong intent category.
32. **Ambiguous target execution** - A vague request may accidentally resolve to a concrete target later if guardrails regress.
33. **Action risk misclassification** - A medium/high or blocked action can be classified as low and bypass approval.
34. **Permission decision mismatch** - `PermissionDecision` can disagree with the candidate risk or preview if contracts drift.
35. **Action preview wrong information** - A preview can show the wrong target, expected effect, or reversibility.
36. **Stale risk classification** - A previously low-risk action can become risky after target, source, or parameters change.
37. **Risky PC action** - File operations, shutdown, installs, admin commands, or registry edits can damage the user environment.
38. **Wrong home device control** - A room/device alias can resolve to the wrong physical device.
39. **Unauthorized action** - Medium/high risk actions can run without explicit confirmation if permission gates are incomplete.
40. **Confirmation bypass** - A future adapter could run an action without a valid `ActionPreview` and approval decision.
41. **Voice confirmation ambiguity** - A user may confirm a misunderstood voice action if repeat-back or confidence handling is weak.
42. **Blocked intent bypass** - A blocked phrase such as `secret.read`, `file.delete`, or shell-like text could slip through the router.
43. **Blocked action bypass** - A blocked action such as `secret.read`, `file.delete`, or unrestricted shell execution could reach an adapter.
44. **Adapter execution before PermissionManager** - Adapter code could be added before permission decisions are mandatory.
45. **Adapter execution without preview** - Medium/high actions could execute without showing target, effect, risk, and warnings.
46. **Medium/high action accidental execution** - A future action may execute after preview but before explicit confirmation.
47. **Action result/audit missing** - Future actions could complete without durable status, error, or audit metadata.
48. **Audit metadata missing fields** - `action_id`, risk, source, decision, target summary, or `execution_attempted=false` could be omitted.
49. **Irreversible action** - Destructive action may not be reversible or auditable.
50. **Windows permission issues** - UAC, focus control, app launch, media control, and file system permissions may fail or behave inconsistently.
51. **Routine step risk aggregation error** - A medium/high or blocked step may be summarized as a safe routine.
52. **High-risk routine accidental approval** - A routine such as `evden cikiyorum` may appear harmless if confirmation rules drift.
53. **Routine preview mistaken for execution** - Users may think dry-run routine planning already changed PC or home state.
54. **Stale preference affects routine** - Old personal memory preferences may select the wrong default app or routine target.
55. **Wrong routine selected** - Similar routine names or aliases may resolve to the wrong built-in workflow.
56. **Ambiguous routine name** - Partial mode commands such as `modu baslat` must not select a routine automatically.
57. **Routine contains blocked step** - A future template or custom routine may include blocked actions.
58. **Scheduler creep before safety** - Automatic routine scheduling may arrive before audit and confirmation boundaries are ready.
59. **Home step accidentally executed** - Device-oriented routine steps may execute before home adapters are safe.
60. **PC adapter execute accidentally called** - Routine planning may call a future execution path instead of dry-run preview only.
61. **Wrong device resolved** - A device alias may map to the wrong canonical device id.
62. **Wrong room resolved** - A room alias may map to the wrong room.
63. **Stale alias** - A stored alias may no longer match the intended device layout.
64. **Duplicate alias** - Two rooms or devices may claim the same alias and create ambiguity.
65. **Unsupported capability treated as supported** - Planner or adapter code may skip capability validation.
66. **Device state write without confirmation** - Medium-risk home write actions may lose confirmation enforcement.
67. **Home adapter accidentally called** - Preview-only device planning may accidentally call a future runtime adapter.
68. **Network discovery creep** - Convenience work may add LAN discovery before policy and privacy review.
69. **Physical world side effect risk** - Device writes can change lights, climate, locks, or security state in the real world.
70. **Room/device privacy** - Registry data can reveal home layout, devices, and behavioral patterns.

## Privacy and Data Risks

71. **Secret leakage via AI path** - `.env`, keys, keystores, browser profiles, and raw logs must remain blocked.
72. **Personal data leakage** - Personal memory, preferences, routines, devices, and command history can expose sensitive behavior.
73. **NotebookLM data mistake** - Manual exports can accidentally include private or secret data.
74. **Full disk exposure** - MCP or future file adapters must not expose `C:\Users`, full disks, or blocked roots.
75. **D: drive legacy problem** - `D:\ATLAS` and writes to `D:` remain blocked by policy.

## Runtime and Reliability Risks

76. **Local model latency** - Ollama model load or slow generation can make the assistant feel unresponsive.
77. **Ollama warmup/load time** - Cold model start can delay the first answer.
78. **Agent route error** - MainAgent or future IntentRouter can choose the wrong sub-agent or action route.
79. **Audit depth mismatch** - Static audits can pass while a future runtime action path is unsafe.
80. **Knowledge-base drift** - Roadmap/status docs can become stale and mislead AI answers.

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

## Missing Controls

- Runtime `ActionRouter`.
- Adapter allowlist and execution guard.
- Confirmation timeout/cancel implementation.
- Voice confirmation policy runtime.
- Transcript confidence enforcement runtime.
- Audio retention/deletion runtime policy enforcement.
- Home adapter runtime on top of device registry and room model.
- Durable personal memory storage policy.
- Routine scheduler and cancellation runtime.
- Desktop permission panel.
- Durable action and routine audit log.

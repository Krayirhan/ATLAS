# ATLAS — Current status

- **Release:** **V1 RC — GO** (control plane only; no AI runtime in V1).
- **Root:** `E:\ATLAS` (canonical). **`D:\ATLAS` is not an operational root.**
- **Pilot / self-project:** **ATLAS**. **BenimFormum is not the pilot** and is not a V1 requirement.
- **Sprints 25–27 (batch):** Documentation + usage guide, pytest coverage hardening, report/audit/context polish — all **pre–AI Layer** work.
- **Sprint 28:** Planned start of **AI Layer Foundation** (interfaces / read-only ask design); **no** provider wiring or autonomous agents in that sprint’s baseline scope without an explicit scope change.
- **Tests:** See latest `python -m pytest -q` from `assistant-core` (recent batch: **34 passed**).
- **Doctor / audit:** `doctor`, `doctor --full`, and `audit v1-rc` are the authoritative health and RC signals on a given machine.

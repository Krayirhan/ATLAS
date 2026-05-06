# 35 PC Control Adapter MVP

## Sprint 40
The goal of Sprint 40 was to build the first PC control adapter layer securely.

### PCControlAdapter Role
The `PCControlAdapter` bridges the gap between the `IntentRouter`/`PermissionManager` and actual PC actions. In this MVP, it primarily focuses on generating dry-run preview plans without executing unsafe actions.

### Supported Action Capability Table
| Action | Supported | Dry-Run | Execution | Risk Level |
|---|---|---|---|---|
| pc.system_info | Yes | Yes | Yes | Low |
| pc.open_app | Yes | Yes | No | Low |
| pc.open_folder | Yes | Yes | No | Low |
| browser.search | Yes | Yes | No | Low |
| file.search | Yes | Yes | No | Low |
| pc.media.* | Yes | Yes | No | Low |
| pc.volume.* | Yes | Yes | No | Low |
| file.delete | No | No | No | Blocked |
| secret.read | No | No | No | Blocked |

### Dry-Run Default
The default execution behavior for the adapter is `dry_run=True`. It evaluates permissions and creates a `PCControlPlan` without performing any side-effects, generating a `PCControlResult` with status `PREVIEWED` or `BLOCKED`.

### Execution Boundary
- **Terminal executor**: NO
- **Arbitrary commands**: NO
- **Home device control**: NO
- **Voice runtime**: NO
- **Actual App Launch**: NO

### Blocked Action List
Actions like `file.delete`, `shell.execute_unrestricted`, and `secret.read` are explicitly listed in `_BLOCKED_ACTIONS` and denied at the safety gate layer.

### CLI Preview
The new `python -m app.cli ai pc-preview` command connects intent routing to adapter plan building and result generation:
```bash
python -m app.cli ai pc-preview --project ATLAS "Chrome'u aç"
python -m app.cli ai pc-preview --project ATLAS --show-plan "Belgeler klasörünü aç"
```

### Sprint 41 Dependency
Sprint 41 will introduce the ConversationLoop MVP, linking the adapter into an interactive loop.

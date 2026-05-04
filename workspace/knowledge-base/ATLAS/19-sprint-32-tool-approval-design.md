# Sprint 32 - ToolApproval Design

## Sprint 32 amaci

ATLAS icine preview-only bir approval workflow tasarimi eklemek.

## ToolApprovalAgent rolu

- Onerilen command / file_change / tool_call actionlarini degerlendirir.
- Risk seviyesini ve approval gereksinimini belirler.
- Preview-only karar uretir.
- Hicbir command veya tool cagrisi yapmaz.

## ProposedAction modelleri

- `ProposedAction`
- `ProposedCommand`
- `ProposedFileChange`
- `ProposedToolCall`

## Approval statuses

- `blocked`
- `approval_required`
- `preview_allowed`
- `safe_readonly`
- `unknown`

## Risk levels

- `critical`
- `high`
- `medium`
- `low`
- `info`

## Blocked examples

- `git reset --hard`
- `git clean -fd`
- `git push --force`
- `Remove-Item -Recurse`
- `format`
- `D:\ATLAS`
- `.env`
- `id_rsa`

## Approval required examples

- `git push`
- `git commit`
- `pip install`
- `npm install`
- `docker run`

## Preview allowed examples

- `python -m pytest -q`
- `python -m app.cli doctor --full`
- `python -m app.cli config validate`

## Safe readonly examples

- `python -m app.cli ai memory --project ATLAS`
- `python -m app.cli ai ask-agent --project ATLAS --provider mock "..."`
- `python -m app.cli ai plan --project ATLAS --provider mock --goal "..."`
- `python -m app.cli ai review --project ATLAS --provider mock --scope safety`

## CLI komutlari

```text
python -m app.cli ai approval command --project ATLAS --cmd "python -m pytest -q"
python -m app.cli ai approval command --project ATLAS --cmd "git reset --hard"
python -m app.cli ai approval command --project ATLAS --cmd "git push"
```

## Guvenlik sinirlari

- Preview only
- Command execution yok
- Dosya yazma yok
- MCP tool call yok
- Approval token yok
- Prompt full logging yok

## Test plani

- Evaluator rule tests
- ToolApprovalAgent decision tests
- CLI output and JSON tests
- Existing ai plan / ai review regression smoke tests

## Acceptance criteria

- Approval modelleri olusur
- Evaluator blocked / approval_required / preview_allowed / safe_readonly ayrimini yapar
- `ai approval command` calisir
- Komutlar gercekten calistirilmaz

## Sprint 33 bagimliligi

- `MainAgent Alpha`

# Sprint 30 - PlannerAgent Alpha

## Sprint 30 amacı

PlannerAgent ile read-only plan üretim katmanını eklemek.

## PlannerAgent rolü

- Kullanıcının hedefini alır
- MemoryAgent snapshot'ını okur
- Riskleri ve sonraki sprintleri dikkate alır
- Bounded sprint/iş planı üretir

## Kapsam

- objective
- scope
- out_of_scope
- expected files
- risks
- acceptance criteria
- test plan
- validation commands

## Kapsam dışı

- kod yazmak
- dosya değiştirmek
- terminal çalıştırmak
- git işlemi yapmak
- MCP tool çağırmak
- patch uygulamak

## CLI komutları

```text
python -m app.cli ai plan --project ATLAS --provider mock --goal "Sprint 31 için CodeReviewerAgent hazırlığı yap"
python -m app.cli ai plan --project ATLAS --provider ollama --goal "ATLAS için test coverage hardening sprinti planla"
python -m app.cli ai plan --project ATLAS --provider mock --show-sources --goal "Sprint 31'e geçmeden önce ne yapılmalı?"
```

## Güvenlik sınırları

- read-only only
- no file writes
- no terminal execution
- no git
- no MCP tool calls
- no prompt full logging

## Test planı

- PlannerAgent unit tests
- ai plan CLI tests
- mock provider path
- ollama provider mocked path
- JSON output validation

## Acceptance criteria

- PlannerAgent oluşmuş olmalı
- read-only capability flag'leri false/true doğru olmalı
- ai plan çalışmalı
- mock provider ile plan üretebilmeli
- kaynak metadata gösterebilmeli
- plan içinde objective/scope/out_of_scope/risks/acceptance criteria/test plan olmalı

## Sprint 31 bağımlılığı

Sprint 31 - CodeReviewerAgent Alpha

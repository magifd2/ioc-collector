# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-03-25

### Added

- CLI tool (`ioc-collector`) for researching security incidents and extracting IoCs
- Two-stage Gemini pipeline:
  - `research()`: Web research via Google Search Grounding (Vertex AI)
  - `extract_report()`: Structured extraction using `response_schema` (Pydantic)
- Support for 9 IoC types: `ipv4-addr`, `domain-name`, `url`, `file-hash-md5`, `file-hash-sha1`, `file-hash-sha256`, `file-name`, `process-name`, `other`
- Markdown report output with defanged IoC values and clickable reference links (`[title](url)`)
- STIX 2.1 Bundle output with refanged IoC values and proper STIX patterns
- Defang/refang module with idempotent conversion (handles pre-defanged input from web articles)
- HTTP 429 exponential backoff retry (base 2s, max 60s, up to 5 retries)
- ADC (Application Default Credentials) authentication via Vertex AI
- CLI options: `--target`, `--file`, stdin, `--non-interactive`, `--output`, `--model`, `--verbose`
- Custom exception hierarchy: `GeminiAuthError`, `GeminiRateLimitError`, `GeminiResponseError`
- Rich spinner progress display during API calls
- Prompt injection countermeasures (input/instruction separation, role anchoring, schema validation)
- Full unit test suite (99 tests, all mocked — no API calls required)

### Technical notes

- Default model: `gemini-2.5-flash`
- STIX JSON output uses `ensure_ascii=False` for human-readable non-ASCII characters
- `OTHER` type IoCs use `pattern_type="sigma"` as a STIX validator workaround

[0.1.0]: https://github.com/magifd2/ioc-collector/releases/tag/v0.1.0

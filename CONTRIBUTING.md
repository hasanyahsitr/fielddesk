# Contributing to FieldDesk

FieldDesk is an early Windows x64 project. Issues in English or Turkish are welcome. Small, focused pull requests are easiest to review.

## Run locally

Use Python 3.13 and Node.js 24 LTS for development:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -X utf8 app/server.py --root "C:\FieldDesk-Dev"
```

Use a separate empty workspace for development. Never use a real drive as a test fixture. A model and llama.cpp are optional; the test suite mocks model and provider responses.

## Before a pull request

```powershell
.venv\Scripts\python -X utf8 -m unittest discover -s tests -v
node tests/test_i18n.js
node tests/test_library_ui.js
.venv\Scripts\python -X utf8 scripts/build_release.py
.venv\Scripts\python -X utf8 scripts/verify_release.py
```

The real OCR integration test is skipped unless `ATOLYE_OCR_TEST_ROOT` points to an explicitly supplied local kit with Tesseract and language data. Ordinary CI does not download large apps, call paid APIs or start a real model. Windows DPAPI tests need Windows.

Describe the user-visible problem, resulting behavior and validation. UI changes should include a screenshot using test data. Add tests for behavior and trust boundaries; documentation and cosmetic changes usually need inspection rather than implementation-mirroring tests.

## Project conventions

- Keep the UI and ordinary startup local; do not add remote fonts, trackers or startup network requests.
- Support English and Turkish UI text. Preserve user text, paths, API payloads and model responses when changing languages.
- Keep session, origin, host, file-path and archive-extraction checks intact. Provider keys must not appear in logs, screenshots or snapshots.
- Preserve existing workspace files. Downloads must retain explicit sources, sizes and verification records. Never run installers automatically.
- Keep release contents explicitly allowlisted. Apps, installers, model weights, personal files and local settings do not belong in this repository.
- Existing ATOLYE paths and identifiers are compatibility details. Discuss a migration before renaming them.

## Catalog changes

Use official publisher sources and check the exact version, Windows x64 architecture, download size, SHA-256, archive layout and executable path. Distinguish portable preparation from installer-only downloads. A version check must not silently change a pinned download. Include publisher licensing/runtime notes and describe the validation actually performed. Do not submit third-party binaries.

## Reports and conduct

Be specific, respectful and constructive. Search existing issues before opening another. For security-sensitive reports, follow [SECURITY.md](SECURITY.md). Contributions are offered under the repository's existing MIT license; third-party assets remain under their own licenses.

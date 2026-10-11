# Changelog

## Unreleased

- Translate PDF preview summaries, warning text and output page counts in the English UI, including singular page counts. File names and paths remain unchanged.
- Announce document search progress, result counts and failures through a separate polite status region. Document excerpts are not live announcements. Older searches cannot overwrite a newer search result.

## 0.8.0 — 2026-10-11 · Preview

This is the first prepared GitHub release of FieldDesk. Earlier development used the ATÖLYE name; existing workspaces remain compatible.

### Added and improved

- FieldDesk name and icon, with English as the default interface language and selectable Turkish.
- Workspace-persisted language preference. Changing languages preserves typed drafts and visible conversation without translating user content.
- General conversation with local models, independent of document search, using bounded recent context and the latest message's language.
- Separate document chat mode and explicit empty-model-response errors.
- English documentation, Turkish README and source/Windows x64 distribution packages.

### Included from earlier development

- App launchers, search, favorites and custom portable app registration.
- A catalog of 30 pinned packages: 25 prepared automatically and 5 downloaded as installer files only.
- Download progress, cancellation, resumable transfers, integrity checks, publisher version checks and reversible managed-package removal.
- Optional API connections, document excerpt preview before cloud export and session/Windows-encrypted key storage.
- Offline library search, PDF merging, image preparation, OCR and project environment launchers.
- Workspace setup, device information and backup status.

### Validation and limitations

61 backend tests and 18 localization checks passed locally, including real OCR. A real Gemma E2B conversation was checked for Turkish replies, prior-turn context and switching to English. A clean Windows ZIP launched with system-only PATH and no separately installed Python. These checks do not guarantee model accuracy or compatibility with every third-party app.

Windows x64 is the target. Model weights, llama.cpp, Tesseract and third-party apps are not bundled. Local inference currently uses CPU. Chat history is page-local and bounded; a reload clears conversational context. The package catalog does not automatically track the newest releases.

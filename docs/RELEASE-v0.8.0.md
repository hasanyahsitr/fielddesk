# FieldDesk v0.8.0 — Preview

A portable local workspace for Windows: apps, projects, documents, file workflows and optional AI in one interface.

## Download and start

Choose **FieldDesk-0.8.0-windows-x64.zip** from the release assets, extract it to a writable folder and run **START.cmd**. A separate Python installation is not required. Choose your workspace folder in the setup screen.

For developers, **FieldDesk-0.8.0-source.zip** contains the source and community files. SHA-256 companion files are provided for both ZIPs. The app and model libraries on a real workspace drive are not part of either download.

## In this preview

- English by default, optional Turkish, with the language preference saved in the workspace.
- Searchable app launchers and 30 selectable packages with progress and verified preparation. Five entries download an installer only; installers never run automatically.
- Local general chat without documents, bounded recent context and a separate document mode.
- Optional cloud chat using your own provider account and key.
- Offline document search, PDF merging, image preparation, OCR and project launchers.

## Before using it

Windows x64 is the supported target. Local AI needs separate supported GGUF weights and llama.cpp; OCR needs Tesseract and language files. The current model runtime uses CPU and initial HDD loading may take minutes. Model responses need review. Chat context is bounded and cleared on page reload. Third-party tools may require runtimes, accounts or licenses. This is an early preview, not a claim of complete compatibility.

Local validation: 61 backend tests, 18 localization checks, real Gemma conversation, real OCR and clean Windows ZIP startup. GitHub-hosted Windows CI passed backend, JavaScript, localization and source release checks. The real OCR integration is skipped in ordinary hosted CI and was checked separately in the local kit.

Report reproducible problems with the bug template, using test data and sanitized logs. See README, CONTRIBUTING, SECURITY and ROADMAP for details.

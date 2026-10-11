# Preparing a release

Maintainer notes. These instructions do not publish anything automatically.

1. Review the source diff, pinned catalog metadata and third-party notices. Update version strings, changelog and release notes together.
2. Run the documented tests on Windows. A real OCR/model check is separate from mocked CI. Record what was actually run.
3. Build the source ZIP with `python -X utf8 scripts/build_release.py`.
4. Build the Windows ZIP with `python -X utf8 scripts/build_windows.py --python-runtime PATH_TO_EMBEDDED_PYTHON --packages PATH_TO_MODULES`. Supply official runtime files and reviewed dependencies with license files.
5. Run `python -X utf8 scripts/verify_release.py`. Check both ZIPs and SHA-256 files; never zip a real workspace drive.
6. Extract the Windows ZIP into an empty folder. Start `START.cmd` with no external Python on PATH. Check setup, default English, Turkish switching, catalog loading and a clean shutdown. Real local model and OCR files are supplied separately.
7. Review the repository visibility and destination with the owner. Before the first commit, check the staged diff and tracked file list for local data and credentials.
8. Push the reviewed source to the chosen repository. Wait for CI; a local pass is not a GitHub-hosted CI pass.
9. Create a tag matching the reviewed version and a **pre-release** using `docs/RELEASE-v0.8.0.md` as the body. Attach the two ZIPs and their `.sha256` files. Verify the public download links after publication.

Do not mark a draft as published or claim downloads work before publication is verified. Enable GitHub private vulnerability reporting in repository settings if the owner chooses to provide that channel. No issue template or policy file enables it by itself.

The CI workflow runs tests and produces a source artifact; it does not publish releases, upload the real workspace, or require provider keys. Actions are pinned to commit SHAs, following [GitHub's secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use). Review update PRs instead of replacing pins with floating tags.

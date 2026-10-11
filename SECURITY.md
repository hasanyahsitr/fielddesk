# Security policy

## Release scope

FieldDesk 0.8 is a preview. Fixes are developed against the latest source; there is no long-term support or guaranteed response schedule. The local service is intended for loopback use on a trusted Windows computer.

## Reporting a vulnerability

Use the repository's **Security → Report a vulnerability** option if the maintainer has enabled private reporting. If that option is unavailable, open an issue asking for a private reporting channel without posting exploit details, credentials or personal files. This document does not imply that a private reporting channel has already been configured.

Include the affected version, reproduction steps using disposable test data, expected and actual results, and the security impact. Remove API keys, session tokens, personal paths and document excerpts from logs and screenshots. Do not test against another person's workspace or provider account.

## Relevant boundaries

- Mutations require the app's session token plus host/origin validation; the server binds to loopback.
- Cloud chat sends the message and bounded recent conversation to the selected provider. Document mode requires a matching, expiring excerpt preview before export.
- Session-only keys are the default. Optional Windows DPAPI storage depends on the Windows account and computer.
- Downloads use pinned metadata and integrity checks before preparation. Integrity hashes do not prove a third-party program is safe.
- Local document indexing excludes common secret files, but exclusion patterns do not guarantee that every secret is detected.

AI responses are untrusted output. The chat assistant cannot browse the web, control the computer or execute commands. Do not expose the service through a public tunnel or use a real workspace as a test fixture.

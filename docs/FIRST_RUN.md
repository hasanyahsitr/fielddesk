# Try FieldDesk in five minutes

[Türkçe](FIRST_RUN.tr.md) · [Back to README](../README.md)

Use a Windows x64 computer and sample documents. FieldDesk 0.8.0 is a preview. This walkthrough does not need an API key, an AI model or administrator access for the bundled app itself; your Windows policies may restrict execution. Slow downloads can take longer than five minutes.

## 1. Open a workspace

Download `FieldDesk-0.8.0-windows-x64.zip` from the [preview release](https://github.com/hasanyahsitr/fielddesk/releases/tag/v0.8.0). Extract the whole ZIP into a short path such as `C:\FieldDesk-Test`, then double-click `START.cmd`. Keep the `runtime` folder beside it. A separate Python installation is not needed.

In **Workspace setup**, choose a separate test workspace folder, run the check, then apply the folder preparation if offered. Setup creates missing folders; it does not install programs or download models. The UI is English by default; **Türkçe** is available in the top bar.

If Windows or an organization policy blocks a component, record the message and report it. Do not disable protection to complete this test. The preview is not code-signed.

## 2. Prepare one tool

Open **Apps → Get apps**, search for **Notepad++**, select it and choose **Download & prepare selected**. An internet connection is needed. Wait for **Ready to use**, then open it. The catalog checks the pinned size and SHA-256 before preparation. Installer-only packages are downloaded but not installed automatically.

## 3. Merge two sample PDFs

Open **Workflows → Merge PDFs**, add two small disposable PDFs and select **Preview result**. Check the order and page count, then choose **Confirm and start**. Open the output folder and inspect `birlestirilmis.pdf`. Outputs go under `12_ISLER/Ciktilar`; originals stay intact. Some PDF workflow summaries in this preview still use Turkish wording in the English UI.

## 4. Find a project note

Create `04_PROJELER/Sample/notes.txt` inside your workspace with this fictional content:

```text
Sample handover: review the two PDFs before Tuesday.
```

Open **Library → Update index**, wait for indexing to finish, search for `handover` and check that `notes.txt` appears. Local document search does not need an AI model. A file outside the indexed workspace folders will not appear automatically.

## Optional: chat later

The assistant supports general chat and a separate document mode. Local chat requires a compatible llama.cpp runtime and supported GGUF model; neither is included in the 23 MB download. OCR requires Tesseract and language data. Cloud chat requires your own provider access and key. Missing components are not a failed result for this basic walkthrough. See the [README](../README.md#local-ai).

## Share useful feedback

Use a [bug report](https://github.com/hasanyahsitr/fielddesk/issues/new?template=bug_report.yml) for a reproducible failure. For general feedback, use the [first-run feedback issue](https://github.com/hasanyahsitr/fielddesk/issues?q=is%3Aissue%20%22First-run%20feedback%22).

- Windows version and x64; source or Windows ZIP; internal or USB drive.
- Which steps worked, where you stopped and approximately how long it took.
- What you expected and what happened; include a screenshot using sample data if useful.
- Which task you would use again, or why you would not return.

English or Turkish is welcome. Keep keys, session tokens, personal file paths and real document excerpts out of reports. For vulnerabilities use [private reporting](https://github.com/hasanyahsitr/fielddesk/security/advisories/new).

"""Allowlist-only source release; never collect a real portable kit."""
from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = ['CONTRIBUTING.md', 'SECURITY.md', 'CHANGELOG.md', 'ROADMAP.md', 'THIRD_PARTY_NOTICES.md',
         'docs/RELEASE-v0.8.0.md', 'docs/RELEASING.md', 'docs/FIRST_RUN.md', 'docs/FIRST_RUN.tr.md', 'docs/DEMO.md', 'docs/demo.gif', 'scripts/verify_release.py',
         '.github/workflows/ci.yml', '.github/dependabot.yml', '.github/PULL_REQUEST_TEMPLATE.md',
         '.github/ISSUE_TEMPLATE/bug_report.yml', '.github/ISSUE_TEMPLATE/feature_request.yml', '.github/ISSUE_TEMPLATE/config.yml',
         'README.md', 'README.tr.md', 'LICENSE', '.gitignore', '.gitattributes', 'START.cmd', 'docs/preview.jpg',
         'app/server.py', 'app/engine.py', 'app/library.py', 'app/storage.py', 'app/features.py', 'app/workflows.py',
         'app/static/index.html', 'app/static/app.css', 'app/static/features.css', 'app/static/app.js', 'app/static/features.js', 'app/static/icon.svg',
         'requirements.txt', 'scripts/build_release.py', 'scripts/build_windows.py', 'tests/test_app.py', 'tests/test_i18n.js', 'tests/test_workflows.py',
         'app/documents.py','app/ocr.py','tests/test_documents.py', 'app/providers.py',
         'app/static/i18n.js', 'app/static/providers.js', 'app/static/providers.css', 'tests/test_providers.py',
         'app/packages.py', 'app/catalog.json', 'app/static/catalog.js', 'app/static/catalog.css', 'tests/test_packages.py', 'app/package_lifecycle.py']


def main():
    output = ROOT / 'dist'
    output.mkdir(exist_ok=True)
    archive = output / 'FieldDesk-0.8.0-source.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for relative in FILES:
            path = ROOT / relative
            if path.is_symlink() or not path.is_file():
                raise ValueError(f'Missing or unsafe source file: {relative}')
            z.write(path, 'FieldDesk-0.8.0/' + relative)
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / (archive.name + '.sha256')).write_text(checksum + '  ' + archive.name + '\n', encoding='utf-8')
    print(archive)
    print(checksum)


if __name__ == '__main__':
    main()

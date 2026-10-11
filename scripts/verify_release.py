"""Check prepared archives against the source allowlist, without running their code.

Requires a source ZIP. Checks the matching Windows ZIP too when it is present.
Never scans or collects the user's workspace drive.
"""
import hashlib
from pathlib import Path, PurePosixPath
import re
import zipfile

from build_release import FILES, ROOT


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(path, prefix, runtime=False):
    checksum = path.with_name(path.name + '.sha256')
    require(checksum.is_file(), 'Missing checksum: ' + path.name)
    recorded = checksum.read_text(encoding='utf-8').strip().split()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    require(recorded == [digest, path.name], 'Checksum mismatch: ' + path.name)
    expected = {prefix + relative for relative in FILES}
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), 'Duplicate archive entries: ' + path.name)
        require(archive.testzip() is None, 'Corrupt archive: ' + path.name)
        for name in names:
            parts = PurePosixPath(name).parts
            require(name.startswith(prefix) and '\\' not in name and '..' not in parts,
                    'Unsafe archive path: ' + name)
            relative = name[len(prefix):]
            require(name in expected or runtime and relative.startswith('runtime/'),
                    'File outside release allowlist: ' + name)
            require(not any(part in {'.atolye-data', '.atolye-local', 'Kayitlar',
                                    '01_TASINABILIR', '02_KURULUMLAR', '12_ISLER', '__pycache__'}
                            for part in parts), 'Workspace data in archive: ' + name)
            require(not relative.endswith(('.gguf', '.iso', '.sqlite', '.dpapi', '.log', '.pyc')),
                    'Unexpected data in archive: ' + name)
        require(expected.issubset(names), 'Required source files missing: ' + path.name)
        for relative in FILES:
            require(archive.read(prefix + relative) == (ROOT / relative).read_bytes(),
                    'Stale source in archive: ' + relative)
        if runtime:
            for relative in ('runtime/pythonw.exe', 'runtime/python.exe', 'runtime/LICENSE.txt'):
                require(prefix + relative in names, 'Missing runtime file: ' + relative)
            for package in ('pypdf', 'pillow', 'pypdfium2'):
                require(any('/' + package + '-' in name and '.dist-info/' in name
                            and ('license' in name.lower() or 'licences' in name.lower())
                            for name in names), 'Missing dependency license: ' + package)
    print(f'PASS {path.name}: {path.stat().st_size:,} bytes, {len(names)} entries, SHA-256 {digest}')


def main():
    require(len(FILES) == len(set(FILES)), 'Duplicate source allowlist entry.')
    # Detect common accidental publication inputs. This is not a complete secret scan.
    sensitive = re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}'
                           r'|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'
                           r'|sk-(?:proj-)?[A-Za-z0-9_-]{30,}')
    personal_path = re.compile(r'[A-Z]:[\\/]Users[\\/]', re.I)
    for relative in FILES:
        source = ROOT / relative
        require(source.is_file() and not source.is_symlink(), 'Missing/unsafe source: ' + relative)
        if source.suffix in ('.py', '.js', '.json', '.md', '.yml', '.yaml', '.cmd'):
            text = source.read_text(encoding='utf-8')
            require(not sensitive.search(text), 'Review credential-like content in: ' + relative)
            require(not personal_path.search(text), 'Review personal absolute path in: ' + relative)
    version = re.search(r"^VERSION = '([^']+)'", (ROOT / 'app/server.py').read_text(encoding='utf-8'), re.M)
    require(version is not None, 'Missing app version.')
    prefix = 'FieldDesk-' + version.group(1) + '/'
    source = ROOT / 'dist' / (prefix[:-1] + '-source.zip')
    require(source.is_file(), 'Build the source archive first.')
    verify(source, prefix)
    windows = ROOT / 'dist' / (prefix[:-1] + '-windows-x64.zip')
    if windows.is_file():
        verify(windows, prefix, runtime=True)
    else:
        print('Windows runtime archive not supplied; runtime verification skipped.')


if __name__ == '__main__':
    main()

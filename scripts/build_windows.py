"""Build a Windows x64 runtime ZIP from an existing official embedded Python.

No network download, real kit collection or executable recompilation occurs.
Third-party package dist-info license files are included alongside the modules.
"""
import argparse
import hashlib
from pathlib import Path
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_release import ROOT, FILES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--python-runtime', type=Path, required=True)
    parser.add_argument('--packages', type=Path, required=True)
    args = parser.parse_args()
    runtime, packages = args.python_runtime.resolve(), args.packages.resolve()
    if not (runtime/'pythonw.exe').is_file() or not (runtime/'LICENSE.txt').is_file():
        raise ValueError('An official embedded Python runtime with LICENSE.txt is required.')
    modules=('pypdf','PIL','pypdfium2','pypdfium2_raw','pypdfium2_cfg','pypdfium2_cli')
    for package in modules:
        if not (packages/package).is_dir():
            raise ValueError('Missing package: '+package)
    metadata = list(packages.glob('pypdf-*.dist-info')) + list(packages.glob('pillow-*.dist-info')) + list(packages.glob('pypdfium2-*.dist-info'))
    if len(metadata) != 3 or any(not list(p.rglob('*LICENSE*')) for p in metadata):
        raise ValueError('Exactly one version of each package and its license are required.')
    output = ROOT/'dist'
    output.mkdir(exist_ok=True)
    target = output/'FieldDesk-0.8.0-windows-x64.zip'
    prefix = 'FieldDesk-0.8.0/'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for relative in FILES:
            z.write(ROOT/relative, prefix+relative)
        for p in sorted(runtime.iterdir()):
            if p.is_file() and not p.is_symlink() and (p.suffix.lower() in ('.exe','.dll','.pyd','.zip','.cat') or p.name=='LICENSE.txt'):
                z.write(p, prefix+'runtime/'+p.name)
        pths = list(runtime.glob('python*._pth'))
        if len(pths) != 1:
            raise ValueError('Exactly one Python ._pth configuration is required.')
        stdlib = pths[0].stem + '.zip'
        if not (runtime/stdlib).is_file():
            raise ValueError('Embedded standard library ZIP missing.')
        z.writestr(prefix+'runtime/'+pths[0].name, stdlib+'\n.\nLib/site-packages\n#import site\n')
        for folder in [*(packages/m for m in modules), *metadata]:
            for p in sorted(folder.rglob('*')):
                if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix!='.pyc':
                    z.write(p, prefix+'runtime/Lib/site-packages/'+p.relative_to(packages).as_posix())
    checksum = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_name(target.name+'.sha256').write_text(checksum+'  '+target.name+'\n',encoding='utf-8')
    print(target)
    print(checksum)


if __name__ == '__main__':
    main()

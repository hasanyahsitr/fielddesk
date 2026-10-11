"""First-run checks and user-owned portable application registrations."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

from storage import safe_path, write_json, plain_child

FOLDERS = ('00_BASLANGIC/Kayitlar', '01_TASINABILIR', '02_KURULUMLAR', '03_YAZILIM/Sablonlar',
           '04_PROJELER', '05_YAPAY_ZEKA/Modeller', '06_TASARIM_MEDYA', '07_KURTARMA',
           '08_BILGI_BANKASI/Atolye', '09_KISISEL_KASA', '10_ISLETIM_SISTEMLERI',
           '12_ISLER/Girdiler', '12_ISLER/Ciktilar')


def dependencies(root):
    package_path = Path(root) / '03_YAZILIM/Python_Paketleri'
    if package_path.is_dir() and str(package_path) not in sys.path:
        sys.path.insert(0, str(package_path))
    result = {}
    for name, module in (('pdf', 'pypdf'), ('images', 'PIL')):
        try:
            __import__(module)
            if module == 'PIL':
                from PIL import Image
                Image.init()
            result[name] = {'ready': True, 'module': module}
        except (ImportError, OSError) as e:
            result[name] = {'ready': False, 'module': module, 'message': str(e)}
    from ocr import status
    result['ocr']=status(root)
    return result


def validate_root(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Çantanın klasörünü belirt.')
    path = Path(value.strip())
    if not path.is_absolute() or str(path).startswith('\\\\'):
        raise ValueError('Bu bilgisayarda tam bir klasör yolu seç.')
    path = path.resolve()
    if not path.is_dir() or path == Path(path.anchor):
        raise ValueError('Sürücü kökü yerine var olan bir çanta klasörü seç.')
    for relative in FOLDERS:
        safe_path(path, relative)
    return path


def setup_preview(root):
    root = validate_root(str(root))
    tools = [{'name': name, 'ready': (root/relative).is_file()} for name, relative in (
        ('VS Code', '01_TASINABILIR/VSCode/Code.exe'), ('Node.js', '01_TASINABILIR/Node/node.exe'),
        ('Git', '01_TASINABILIR/Git/cmd/git.exe'), ('Python Mini', '01_TASINABILIR/PythonMini/python.exe'),
        ('llama.cpp', '01_TASINABILIR/llama.cpp/llama-server.exe'),
        ('Tesseract OCR', '01_TASINABILIR/Tesseract/tesseract.exe'))]
    return {'root': str(root), 'folders': [{'path': rel, 'exists': (root / rel).is_dir()} for rel in FOLDERS],
            'dependencies': dependencies(root), 'writable': os.access(root, os.W_OK), 'tools': tools,
            'message': 'Eksik klasörler oluşturulur; mevcut dosyalar korunur. Program veya model indirilmez.'}


class CustomApps:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.file = safe_path(self.root, '00_BASLANGIC/Kayitlar/ozel-uygulamalar.json')

    def records(self):
        try:
            rows = json.loads(self.file.read_text(encoding='utf-8'))
            return rows if isinstance(rows, list) else []
        except (OSError, ValueError):
            return []

    def entries(self):
        result = []
        for row in self.records():
            try:
                p = safe_path(self.root, row['relative'])
                ready = p.is_file() and p.suffix.lower() == '.exe'
                result.append({'id': row['id'], 'name': row['name'], 'description': row['description'],
                               'category': row['category'], 'path': str(p), 'relative': row['relative'],
                               'ready': ready, 'type': 'app', 'custom': True})
            except (KeyError, TypeError, ValueError):
                continue
        return result

    def add(self, data):
        name = str(data.get('name', '')).strip()
        description = str(data.get('description', '')).strip()
        category = str(data.get('category', '')).strip() or 'Kendi araçlarım'
        if not 1 <= len(name) <= 60 or len(description) > 200 or len(category) > 30:
            raise ValueError('Ad 1–60, açıklama en fazla 200, kategori en fazla 30 karakter olmalı.')
        raw = str(data.get('relative', ''))
        p = safe_path(self.root, raw)
        if not p.is_file() or p.suffix.lower() != '.exe':
            raise ValueError('Çanta içindeki bir .exe dosyasını seç.')
        with p.open('rb') as stream:
            if stream.read(2) != b'MZ':
                raise ValueError('Seçilen dosya bir Windows uygulaması gibi görünmüyor.')
        relative = p.relative_to(self.root).as_posix()
        rows = self.records()
        if any(x.get('relative', '').casefold() == relative.casefold() for x in rows):
            raise ValueError('Bu uygulama zaten listede.')
        row = {'id': 'custom-' + uuid.uuid4().hex[:12], 'name': name, 'description': description,
               'category': category, 'relative': relative}
        rows.append(row)
        write_json(self.file, rows)
        return row

    def remove(self, id):
        rows = self.records()
        if not any(x.get('id') == id for x in rows):
            raise ValueError('Kayıt bulunamadı.')
        write_json(self.file, [x for x in rows if x.get('id') != id])
        return {'message': 'Menü kaydı kaldırıldı. Uygulama dosyası korundu.'}

    def launch(self, id):
        row = next((x for x in self.entries() if x['id'] == id), None)
        if not row or not row['ready']:
            raise ValueError('Uygulama dosyası bulunamadı.')
        path = safe_path(self.root, row['relative'])
        env = os.environ.copy()
        profile = safe_path(self.root, '00_BASLANGIC/Profil/KendiAraclarim/' + id)
        for key in ('APPDATA', 'LOCALAPPDATA'):
            p = profile / key
            p.mkdir(parents=True, exist_ok=True)
            env[key] = str(p)
        subprocess.Popen([str(path)], cwd=path.parent, env=env)
        return {'message': row['name'] + ' açıldı.'}


def browse(root, relative='', kind='files'):
    folder = safe_path(root, relative)
    if not folder.is_dir():
        raise ValueError('Klasör bulunamadı.')
    extensions = {'apps': {'.exe'}, 'pdf': {'.pdf'}, 'images': {'.jpg', '.jpeg', '.png', '.webp'},
                  'ocr': {'.pdf','.jpg','.jpeg','.png','.webp'}}
    allowed = extensions.get(kind, set())
    entries = []
    for p in sorted(folder.iterdir(), key=lambda p: (not p.is_dir(), p.name.casefold())):
        if p.name.startswith('.') or not plain_child(p):
            continue
        try:
            resolved = safe_path(root, p.relative_to(root))
            if p.is_dir() or p.suffix.lower() in allowed:
                entries.append({'name': p.name, 'path': p.relative_to(root).as_posix(), 'directory': p.is_dir(),
                                'bytes': 0 if p.is_dir() else p.stat().st_size})
        except (ValueError, OSError):
            continue
        if len(entries) >= 500:
            break
    current = folder.relative_to(root).as_posix()
    parent = folder.parent.relative_to(root).as_posix() if folder != root else None
    return {'path': '' if current == '.' else current, 'parent': parent, 'entries': entries}

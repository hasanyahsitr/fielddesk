"""Previewed local workflows. Output is always written to a fresh directory."""
from __future__ import annotations
import datetime
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import threading
import time
import uuid

from storage import safe_path, write_json
from features import dependencies
import ocr

MAX_FILE = 50 * 1024 * 1024
MAX_TOTAL = 150 * 1024 * 1024
IMAGE_EXT = {'.png', '.jpg', '.jpeg', '.webp'}


def fingerprint(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def batch_value(value):
    return str(value).replace('%', '%%')


def project_environment(root, project):
    root, project = Path(root), Path(project)
    paths = [root / p for p in ('01_TASINABILIR/Node', '01_TASINABILIR/Git/cmd', '01_TASINABILIR/uv',
             '01_TASINABILIR/ripgrep', '01_TASINABILIR/SQLite', '01_TASINABILIR/PowerShell', '01_TASINABILIR/dotnet')]
    python_root = root / '03_YAZILIM/Calisma_Ortamlari/Python'
    paths += sorted(python_root.glob('cpython-*/')) if python_root.is_dir() else []
    venv = project / '.venv/Scripts'
    if venv.is_dir() and venv.resolve().is_relative_to(root.resolve()):
        paths.insert(0, venv)
    paths = [str(p) for p in paths if p.is_dir()]
    return paths


class Workflows:
    def __init__(self, root, project_provider, editor_provider):
        self.root = Path(root).resolve()
        self.project_provider = project_provider
        self.editor_provider = editor_provider
        self.lock = threading.RLock()
        self.plans = {}
        self.job = None
        self.worker = None
        self.cancel = threading.Event()
        self.files = {}
        self.upload_bytes = 0
        self.upload_folder = '12_ISLER/Girdiler/' + uuid.uuid4().hex[:12]

    def register_upload(self, filename, stream, length):
        name = Path(filename.replace('\\', '/')).name
        if not name or len(name) > 150 or any(c in name for c in '<>:"|?*\r\n\x00') or name.endswith((' ', '.')):
            raise ValueError('Geçersiz dosya adı.')
        if Path(name).suffix.lower() not in IMAGE_EXT | {'.pdf'}:
            raise ValueError('PDF, JPG, PNG veya WebP dosyası seç.')
        if not 0 < length <= MAX_FILE:
            raise ValueError('Her dosya en fazla 50 MB olabilir.')
        with self.lock:
            if self.upload_bytes + length > MAX_TOTAL or len(self.files) >= 30:
                raise ValueError('Bu oturumda en fazla 30 dosya / 150 MB yükleyebilirsin. Çantadaki dosyaları seçebilirsin.')
            folder = safe_path(self.root, self.upload_folder)
            folder.mkdir(parents=True, exist_ok=True)
            target = safe_path(self.root, self.upload_folder + '/' + uuid.uuid4().hex[:8] + '-' + name)
            temp = target.with_suffix(target.suffix + '.part')
            try:
                remaining = length
                with temp.open('xb') as out:
                    while remaining:
                        block = stream.read(min(1024 * 1024, remaining))
                        if not block:
                            raise ValueError('Dosya aktarımı tamamlanmadı.')
                        out.write(block)
                        remaining -= len(block)
                temp.replace(target)
            except Exception:
                temp.unlink(missing_ok=True)
                raise
            key = target.relative_to(self.root).as_posix()
            self.files[key] = name
            self.upload_bytes += length
            return {'path': key, 'name': name, 'bytes': length}

    def source_files(self, values, kind):
        if not isinstance(values, list) or not 1 <= len(values) <= 30 or any(not isinstance(x, str) for x in values):
            raise ValueError('1–30 dosya seç.')
        if len(set(values)) != len(values):
            raise ValueError('Aynı dosyayı iki kez ekleme.')
        result, total = [], 0
        for relative in values:
            p = safe_path(self.root, relative)
            allowed = {'.pdf'} if kind == 'pdf' else IMAGE_EXT | {'.pdf'} if kind=='ocr' else IMAGE_EXT
            if not p.is_file() or p.suffix.lower() not in allowed:
                raise ValueError('Seçilen dosya bu iş akışına uygun değil.')
            size = p.stat().st_size
            total += size
            if not 0 < size <= MAX_FILE or total > MAX_TOTAL:
                raise ValueError('Dosya sınırı: dosya başına 50 MB, toplam 150 MB.')
            result.append({'path': p.relative_to(self.root).as_posix(),
                           'name': self.files.get(relative, p.name), 'bytes': size, 'sha256': fingerprint(p)})
        return result

    def preview(self, data):
        kind = data.get('kind')
        deps = dependencies(self.root)
        if kind not in ('pdf', 'images', 'project','ocr'):
            raise ValueError('Bilinmeyen iş akışı.')
        plan = {'kind': kind, 'created': time.time(), 'files': [], 'warnings': [], 'options': {}}
        if kind in ('pdf', 'images','ocr'):
            if not deps[kind]['ready']:
                raise ValueError('Gerekli paket bulunamadı: ' + deps[kind]['module'] + '. Hazırlık ekranını kontrol et.')
            plan['files'] = self.source_files(data.get('files'), kind)
        if kind=='ocr':
            pages=0
            for row in plan['files']:
                count,options=ocr.inspect(safe_path(self.root,row['path']),data.get('options',{}),deps['ocr']['languages'])
                row['pages']=count;pages+=count
            if pages>ocr.MAX_PAGES:raise ValueError('OCR için toplam en fazla 50 sayfa seç.')
            plan.update(title='Çevrimdışı metin okuma',summary=f'{pages} sayfa → metin + aranabilir PDF',pages=pages,options=options)
            plan['warnings']=['OCR hata yapabilir; isimleri, rakamları ve kritik bilgileri kaynakla karşılaştır.',
                              'Çıktı PDF sayfaları yeniden görüntülenir; bağlantılar, formlar ve özgün PDF yapısı korunmaz.',
                              'El yazısı ve karmaşık tablolar için doğruluk güvencesi verilmez. Sonuçları Bilgi merkezine ekleyebilirsin.']
        if kind == 'pdf':
            from pypdf import PdfReader
            pages = 0
            for row in plan['files']:
                with safe_path(self.root, row['path']).open('rb') as stream:
                    reader = PdfReader(stream)
                    if reader.is_encrypted:
                        raise ValueError(row['name'] + ': şifreli PDF bu sürümde birleştirilemez.')
                    row['pages'] = len(reader.pages)
                if not row['pages']:
                    raise ValueError('Boş PDF birleştirilemez.')
                pages += row['pages']
            if pages > 1000:
                raise ValueError('Tek işlemde en fazla 1000 sayfa birleştirilebilir.')
            plan.update(title='PDF birleştirme', summary=f'{len(plan["files"])} PDF → {pages} sayfalı tek PDF', pages=pages)
            plan['warnings'] = ['Sıra aşağıdaki dosya sırasıdır. Yer işaretleri ve etkileşimli formlar korunmayabilir.']
        if kind == 'images':
            from PIL import Image, ImageOps
            options = data.get('options', {})
            width, quality = int(options.get('width', 1920)), int(options.get('quality', 82))
            format = options.get('format', 'webp')
            if not 320 <= width <= 4096 or not 30 <= quality <= 95 or format not in ('webp', 'jpeg', 'png'):
                raise ValueError('Genişlik 320–4096, kalite 30–95 ve geçerli bir format seç.')
            plan['options'] = {'width': width, 'quality': quality, 'format': format}
            for row in plan['files']:
                with Image.open(safe_path(self.root, row['path'])) as image:
                    if getattr(image, 'n_frames', 1) > 1:
                        raise ValueError(row['name'] + ': hareketli görsel desteklenmiyor.')
                    if image.width * image.height > 40_000_000:
                        raise ValueError(row['name'] + ': görsel sınırı 40 megapiksel.')
                    image = ImageOps.exif_transpose(image)
                    ratio = min(1, width / image.width)
                    row.update(width=image.width, height=image.height, output_width=max(1, round(image.width * ratio)),
                               output_height=max(1, round(image.height * ratio)))
            plan.update(title='Web görselleri', summary=f'{len(plan["files"])} görsel → {format.upper()}, en fazla {width}px genişlik')
            plan['warnings'] = ['Küçük görseller büyütülmez. EXIF/konum bilgileri çıktıya aktarılmaz.']
            if format == 'jpeg':
                plan['warnings'].append('Şeffaf alanlar JPEG çıktısında beyaz olur.')
        if kind == 'project':
            project = next((p for p in self.project_provider() if p['id'] == data.get('project')), None)
            if not project:
                raise ValueError('Listeden bir proje seç.')
            path = safe_path(self.root, project['path'])
            editor = bool(data.get('editor', True))
            if editor and not self.editor_provider():
                raise ValueError('VS Code bulunamadı; yalnızca terminal seçeneğini kullanabilirsin.')
            scripts = []
            package = path / 'package.json'
            if package.is_file() and package.stat().st_size < 1_000_000:
                try:
                    parsed = json.loads(package.read_text(encoding='utf-8'))
                    scripts = list(parsed.get('scripts', {}))[:20]
                except (ValueError, AttributeError):
                    pass
            plan.update(title='Proje ortamı', summary=project['name'] + ' → hazır terminal' + (' ve VS Code' if editor else ''),
                        project=project, tools=project_environment(self.root, path), scripts=scripts,
                        options={'editor': editor}, node_modules=(path/'node_modules').is_dir())
            plan['warnings'] = ['Bağımlılık kurulumu ve proje kodu çalıştırılmaz. Terminal seçilen klasörde açılır.']
        with self.lock:
            self.plans = {k: v for k, v in self.plans.items() if time.time() - v['created'] < 900}
            if len(self.plans) >= 50:
                raise ValueError('Çok sayıda önizleme var. Birkaç dakika sonra tekrar dene.')
            id = secrets.token_urlsafe(24)
            plan['id'] = id
            self.plans[id] = plan
            return plan

    def current(self):
        with self.lock:
            return dict(self.job) if self.job else None

    def cancel_current(self):
        with self.lock:
            if not self.job or self.job['status']!='running' or self.job['kind']!='ocr':
                raise ValueError('İptal edilebilecek bir OCR işlemi yok.')
            self.cancel.set()
            return {'message':'İptal isteniyor; çalışan OCR sayfası durdurulacak.'}

    def start(self, id):
        with self.lock:
            if self.worker and self.worker.is_alive():
                raise ValueError('Bir iş akışı zaten çalışıyor.')
            plan = self.plans.get(id)
            if not plan or time.time() - plan['created'] >= 900:
                raise ValueError('Önizleme süresi doldu. Yeniden önizle.')
            del self.plans[id]
            self.cancel.clear()
            self.job = {'id': uuid.uuid4().hex[:12], 'kind': plan['kind'], 'title': plan['title'],
                        'status': 'running', 'done': 0, 'total': plan.get('pages',len(plan['files']) or 1) if plan['kind']=='ocr' else len(plan['files']) or 1, 'message': 'Girdiler kontrol ediliyor.'}
            self.worker = threading.Thread(target=self.run, args=(plan,), daemon=True)
            self.worker.start()
            return self.current()

    def run(self, plan):
        output = None
        try:
            for row in plan['files']:
                p = safe_path(self.root, row['path'])
                if not p.is_file() or p.stat().st_size != row['bytes'] or fingerprint(p) != row['sha256']:
                    raise ValueError('Bir kaynak dosya önizlemeden sonra değişti. Yeniden önizle.')
            relative = '12_ISLER/Ciktilar/' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + self.job['id']
            output = safe_path(self.root, relative)
            output.mkdir(parents=True, exist_ok=False)
            results = []
            if plan['kind']=='ocr':
                def progress(done,message):
                    with self.lock:self.job.update(done=done,message=message)
                paths,warnings,preview,pages=ocr.recognize(self.root,plan['files'],output,plan['options'],progress,self.cancel)
                plan['warnings']+=warnings
                for path in paths:
                    results.append({'name':path.name,'bytes':path.stat().st_size,'sha256':fingerprint(path),
                                    **({'pages':pages} if path.suffix=='.pdf' else {})})
                with self.lock:self.job.update(text_preview=preview,warnings=plan['warnings'])
            if plan['kind'] == 'pdf':
                from pypdf import PdfReader, PdfWriter
                writer = PdfWriter()
                for i, row in enumerate(plan['files']):
                    with safe_path(self.root, row['path']).open('rb') as stream:
                        reader = PdfReader(stream)
                        for page in reader.pages:
                            writer.add_page(page)
                    with self.lock:
                        self.job.update(done=i+1, message=f'{i+1}/{len(plan["files"])} PDF okundu.')
                target = output / 'birlestirilmis.pdf'
                with target.with_suffix('.part').open('xb') as stream:
                    writer.write(stream)
                writer.close()
                target.with_suffix('.part').replace(target)
                with target.open('rb') as stream:
                    if len(PdfReader(stream).pages) != plan['pages']:
                        raise ValueError('Çıktı sayfa sayısı beklenenle eşleşmiyor.')
                results.append({'name': target.name, 'bytes': target.stat().st_size, 'sha256': fingerprint(target), 'pages': plan['pages']})
            if plan['kind'] == 'images':
                from PIL import Image, ImageOps
                options = plan['options']
                for i, row in enumerate(plan['files']):
                    with Image.open(safe_path(self.root, row['path'])) as original:
                        image = ImageOps.exif_transpose(original)
                        image.thumbnail((row['output_width'], row['output_height']), Image.Resampling.LANCZOS)
                        if options['format'] == 'jpeg':
                            rgba = image.convert('RGBA')
                            image = Image.new('RGB', image.size, 'white')
                            image.paste(rgba, mask=rgba.getchannel('A'))
                        elif image.mode not in ('RGB', 'RGBA'):
                            image = image.convert('RGBA' if 'transparency' in image.info else 'RGB')
                        ext = {'jpeg': 'jpg', 'webp': 'webp', 'png': 'png'}[options['format']]
                        name = f'{i+1:02d}-' + Path(row['name']).stem[:100] + '.' + ext
                        target = output / name
                        temp = target.with_suffix('.part')
                        kwargs = {'quality': options['quality']} if ext != 'png' else {'optimize': True}
                        if image.info.get('icc_profile'):
                            kwargs['icc_profile'] = image.info['icc_profile']
                        image.save(temp, format={'jpg': 'JPEG', 'webp': 'WEBP', 'png': 'PNG'}[ext], **kwargs)
                        with Image.open(temp) as check:
                            check.load()
                            dimensions = check.size
                        temp.replace(target)
                        results.append({'name': name, 'bytes': target.stat().st_size, 'sha256': fingerprint(target),
                                        'width': dimensions[0], 'height': dimensions[1]})
                    with self.lock:
                        self.job.update(done=i+1, message=f'{i+1}/{len(plan["files"])} görsel hazırlandı.')
            if plan['kind'] == 'project':
                project = safe_path(self.root, plan['project']['path'])
                if not project.is_dir():
                    raise ValueError('Proje klasörü artık bulunamıyor.')
                launcher = output / 'proje-terminali.cmd'
                paths = project_environment(self.root, project)
                lines = ['@echo off', 'chcp 65001 >nul', 'setlocal DisableDelayedExpansion', 'cd /d "' + batch_value(project) + '"',
                         'set "PATH=' + batch_value(';'.join(paths)) + ';%PATH%"', 'set "PYTHONUTF8=1"',
                         'set "PYTHONPATH=' + ('' if (project/'.venv/Scripts').is_dir() else batch_value(self.root/'03_YAZILIM/Python_Paketleri')) + '"',
                         'set "UV_CACHE_DIR=' + batch_value(self.root/'03_YAZILIM/Onbellek/uv') + '"',
                         'set "UV_PYTHON_INSTALL_DIR=' + batch_value(self.root/'03_YAZILIM/Calisma_Ortamlari/Python') + '"',
                         'set "npm_config_cache=' + batch_value(self.root/'03_YAZILIM/Onbellek/npm') + '"',
                         'echo ATOLYE: Proje ortami hazir. Proje kodu calistirilmadi.', '"%COMSPEC%" /D /K']
                launcher.write_bytes(('\r\n'.join(lines)+'\r\n').encode('utf-8'))
                (output/'Hazirlik.md').write_text('# Proje ortamı\n\nKlasör: '+plan['project']['path']+'\n\nTanımlı npm komut adları: '+', '.join(plan['scripts'])+'\n\nBağımlılık kurulmadı, proje kodu çalıştırılmadı.\n',encoding='utf-8')
                if plan['options']['editor']:
                    editor = self.editor_provider()
                    if not editor:
                        raise ValueError('VS Code artık bulunamıyor.')
                    subprocess.Popen([str(editor), str(project)], cwd=editor.parent)
                os.startfile(str(launcher))
                results.append({'name': launcher.name, 'bytes': launcher.stat().st_size, 'sha256': fingerprint(launcher)})
            report = {'kind': plan['kind'], 'title': plan['title'], 'completed': True, 'inputs': plan['files'],
                      'options': plan['options'], 'outputs': results, 'warnings': plan['warnings']}
            write_json(output/'islem-raporu.json', report)
            with self.lock:
                self.job.update(status='complete', message='İşlem tamamlandı. Kaynak dosyalar korundu.', results=results,
                                output=relative, done=self.job['total'])
        except Exception as e:
            with self.lock:
                self.job.update(status='cancelled' if isinstance(e,ocr.Cancelled) else 'error', message=str(e), output=output.relative_to(self.root).as_posix() if output else None)
            if output:
                write_json(output/'islem-raporu.json', {'completed': False, 'error': str(e), 'kind': plan['kind']})

"""FieldDesk control center. Local-only, no web framework or cloud account required."""
from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser

# Embedded Python does not automatically add the script directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine
from library import Library, device_report
from storage import safe_path, write_json
from features import CustomApps, browse, dependencies, setup_preview, validate_root, FOLDERS
from workflows import Workflows
from providers import Providers, PRESETS
from packages import Packages

VERSION = '0.8.0'
STATIC = Path(__file__).parent / 'static'
LOCAL_CONFIG = Path(__file__).resolve().parents[1] / '.atolye-local.json'


def identifier(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()[:20]


class App:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.logs = self.root / '00_BASLANGIC/Kayitlar'
        self.logs.mkdir(parents=True, exist_ok=True)
        engine.ROOT = self.root
        self.library = Library(self.root)
        self.providers = Providers(self.root)
        self.package_manager = Packages(self.root)
        self.cloud_previews = {}
        self.token = secrets.token_urlsafe(32)
        self.port = 0
        self.guard = threading.RLock()
        self.job = None
        self.cancel = threading.Event()
        self.worker = None
        self.items = [x for x in engine.entries() if x['type'] not in ('ai', 'page')]
        self.custom = CustomApps(self.root)
        self.picker_lock = threading.Lock()
        self.workflows = Workflows(self.root, self.projects, lambda: engine.find_file('01_TASINABILIR/VSCode', 'Code.exe'))

    def entries(self):
        entries = self.items + self.custom.entries()
        for row in self.package_manager.entries():
            original = row['id'].removeprefix('package-')
            # Replace the shortcut, preserving all original program files.
            entries = [x for x in entries if x['id'] != original]
            entries.append(row)
        return entries

    def session_file(self):
        return {'port': self.port, 'pid': os.getpid(), 'url': f'http://127.0.0.1:{self.port}',
                'stop_token': self.token, 'root': str(self.root)}

    def setup_apply(self, data):
        root = validate_root(data.get('root', str(self.root)))
        with self.guard:
            if self.worker and self.worker.is_alive() or self.workflows.worker and self.workflows.worker.is_alive() or self.package_manager.busy() or self.library.progress.get('running'):
                raise ValueError('Önce devam eden işlemin tamamlanmasını bekle.')
            for relative in FOLDERS:
                safe_path(root, relative).mkdir(parents=True, exist_ok=True)
            if root != self.root:
                self.stop_model()
                self.root = root
                self.logs = safe_path(root, '00_BASLANGIC/Kayitlar')
                engine.ROOT = root
                self.library = Library(root)
                self.providers = Providers(root)
                self.package_manager = Packages(root)
                self.cloud_previews = {}
                self.custom = CustomApps(root)
                self.workflows = Workflows(root, self.projects, lambda: engine.find_file('01_TASINABILIR/VSCode', 'Code.exe'))
                self.job = None
            self.items = [x for x in engine.entries() if x['type'] not in ('ai', 'page')]
            write_json(self.logs/'hazirlik.json', {'completed': True, 'version': VERSION})
            config = {'root': str(root)}
            try:
                config['root_relative'] = os.path.relpath(root, LOCAL_CONFIG.parent)
            except ValueError:
                pass
            write_json(LOCAL_CONFIG, config)
            write_json(self.logs/'menu-oturumu.json', self.session_file())
        return {'message': 'Çalışma alanın hazır. Mevcut dosyalar korundu.', 'root': str(root)}

    def projects(self):
        base = self.root / '04_PROJELER'
        parents = [base / 'Bilgisayardan_Kopya', self.root / '03_YAZILIM/Sablonlar']
        parents += [base]
        result = []
        for parent in parents:
            if not parent.is_dir():
                continue
            for p in sorted(parent.iterdir()):
                if p.name.startswith('.') or p.name in ('Bilgisayardan_Kopya', 'Git-Metadata-Original') or not p.is_dir():
                    continue
                resolved = p.resolve()
                if not resolved.is_relative_to(self.root) or p.is_symlink() or os.path.isjunction(p):
                    continue
                relative = p.relative_to(self.root).as_posix()
                result.append({'id': identifier(relative), 'name': p.name, 'path': relative,
                               'kind': 'Şablon' if 'Sablonlar' in relative else 'Proje',
                               'code': bool((p / 'package.json').exists() or (p / 'pyproject.toml').exists())})
        return result

    def packages(self):
        rows = engine.json_file(self.root / '00_BASLANGIC/paketler.json', [])
        result = []
        for row in rows:
            relative = row.get('path', '')
            try:
                p = safe_path(self.root, relative)
                ready = bool(relative) and p.is_file()
            except (ValueError, OSError):
                ready = False
            # Never expose signed download URLs or arbitrary manifest fields to the UI.
            result.append({k: row.get(k, '') for k in ('id', 'name', 'category', 'version', 'verification', 'sha256', 'note')} | {
                'path': relative, 'ready': ready, 'bytes': row.get('bytes', 0),
                'status': 'Arşivde' if ready else 'Dosya bulunamadı'})
        return result

    def preferences(self):
        saved = engine.json_file(self.logs / 'arayuz-tercihler.json', {})
        language = saved.get('language', 'en') if isinstance(saved, dict) else 'en'
        return {'language': language if language in ('en', 'tr') else 'en'}

    def snapshot(self):
        packages = self.packages()
        backup = engine.json_file(self.logs / 'yedek-sonuc.json', {})
        favorites = engine.json_file(self.logs / 'app-tercihler.json', {}).get('favorites', [])
        owned = engine.RUNNING.get('ai')
        models = [{'id': k, 'name': v[0], 'ready': bool(engine.find_file('01_TASINABILIR/llama.cpp', 'llama-server.exe')) and
                   (self.root / '05_YAPAY_ZEKA/Modeller' / v[1]).is_file()} for k, v in engine.MODELS.items()]
        return {'version': VERSION, 'preferences': self.preferences(), 'entries': self.entries(), 'packages': packages, 'projects': self.projects(),
                'favorites': favorites, 'library': self.library.status(), 'device': device_report(self.root),
                'root': str(self.root), 'models': models, 'connections': self.providers.snapshot(),
                'model': engine.ACTIVE_MODEL if owned and owned.poll() is None else None,
                'backup': {'completed': bool(backup.get('completed')), 'date': backup.get('date')},
                'archive_gb': round(sum(p['bytes'] for p in packages if p['ready']) / 1e9, 1),
                'job': self.current_job(), 'workflow': self.workflows.current(), 'downloads': self.package_manager.current(),
                'setup': {'completed': bool(engine.json_file(self.logs/'hazirlik.json', {}).get('completed')),
                          'dependencies': dependencies(self.root)}}

    def current_job(self):
        with self.guard:
            return dict(self.job) if self.job else None

    def start_chat(self, data):
        question = str(data.get('question', '')).strip()
        provider = data.get('provider', 'local')
        model = data.get('model', 'gemma-e2b')
        if not question or len(question) > 2000:
            raise ValueError('1–2000 karakter uzunluğunda bir soru yaz.')
        if provider != 'local' and provider not in PRESETS:
            raise ValueError('Bilinmeyen sağlayıcı.')
        if provider == 'local' and model not in engine.MODELS:
            raise ValueError('Bilinmeyen model.')
        if provider != 'local':
            self.providers.config(provider, model)
        history = data.get('history', [])
        if not isinstance(history, list):
            raise ValueError('Hatalı sohbet geçmişi.')
        messages = [{'role': x['role'], 'content': str(x.get('content', ''))[:750]} for x in history[-4:]
                    if isinstance(x, dict) and x.get('role') in ('user', 'assistant')]
        with self.guard:
            if self.worker and self.worker.is_alive():
                raise ValueError('Önce devam eden yanıtı tamamla veya durdur.')
            sources = []
            if provider != 'local' and data.get('documents'):
                preview = self.cloud_previews.get(data.get('preview', ''))
                if not preview or preview['expires'] < time.time() or preview['question'] != question or preview['provider'] != provider or preview['model'] != model:
                    raise ValueError('Buluta belge göndermeden önce alıntıları önizleyip onayla.')
                sources = preview['sources']
                del self.cloud_previews[data['preview']]
            self.cancel = threading.Event()
            self.job = {'id': secrets.token_hex(8), 'status': 'loading', 'question': question,
                        'model': model, 'provider': provider, 'documents': bool(data.get('documents')), 'started': time.time(),
                        'message': 'Yerel model yükleniyor. HDD’den ilk açılış birkaç dakika sürebilir.' if provider == 'local' else 'Seçilen API servisine bağlanılıyor.'}
            target = self.run_chat if provider == 'local' else self.run_cloud
            self.worker = threading.Thread(target=target, args=(messages,) if provider == 'local' else (messages, sources), daemon=True)
            self.worker.start()
            return self.current_job()

    def cloud_preview(self, data):
        question = str(data.get('question', '')).strip()
        provider, model = data.get('provider'), data.get('model')
        if not question or len(question) > 2000:
            raise ValueError('1–2000 karakter uzunluğunda bir soru yaz.')
        config = self.providers.config(provider, model)
        found = self.library.search(question, 4)
        if not found:
            raise ValueError('Eşleşen belge bulunamadı; hiçbir belge gönderilmedi.')
        # No filenames or paths in outbound context. Frozen excerpts are reused exactly.
        sources = [{**x, 'excerpt': x['excerpt'][:800]} for x in found]
        with self.guard:
            self.cloud_previews = {k: v for k, v in self.cloud_previews.items() if v['expires'] > time.time()}
            if len(self.cloud_previews) >= 20:
                self.cloud_previews.clear()
            ident = secrets.token_hex(16)
            self.cloud_previews[ident] = {'expires': time.time()+300, 'question': question, 'provider': provider, 'model': model, 'sources': sources}
        return {'id': ident, 'sources': sources, 'destination': config['base'], 'question': question,
                'message': 'Soru ve aşağıdaki alıntılar gönderilecek. Dosya adları, yolları ve dosyanın tamamı gönderilmez. Beş dakika geçerli, tek kullanımlık onay.'}

    def run_cloud(self, history, sources):
        try:
            with self.guard:
                if self.cancel.is_set():
                    return
                job = dict(self.job)
                self.job.update(status='generating', message='Yanıt seçilen API servisinden bekleniyor.')
            response = self.providers.chat(job['provider'], job['model'], history, job['question'], sources)
            with self.guard:
                if not self.cancel.is_set():
                    self.job.update(status='complete', message='Yanıt hazır.' + (' Çıktı sınırına ulaşıldı; yanıt kesilmiş olabilir.' if response.get('truncated') else ''), **response)
        except Exception as error:
            # Provider errors are sanitized in the client; unknown exceptions never expose secrets.
            message = str(error) if isinstance(error, ValueError) else 'API yanıtı işlenemedi. Bağlantı ve model uyumunu kontrol et.'
            with self.guard:
                if not self.cancel.is_set():
                    self.job.update(status='error', message=message)

    def run_chat(self, history):
        try:
            with engine.AI_LOCK:
                with self.guard:
                    if self.cancel.is_set():
                        return
                    job = dict(self.job)
                    if job['documents'] and not self.library.search(job['question'], 1):
                        self.job.update(status='complete', answer='Bu soruyla eşleşen yerel belge bulunamadı. Daha belirgin bir konu adıyla ara.', sources=[], message='Belge bulunamadı; model başlatılmadı.')
                        return
                    engine.ensure_model(job['model'])
                for _ in range(600):
                    if self.cancel.is_set():
                        return
                    if engine.model_healthy():
                        break
                    child = engine.RUNNING.get('ai')
                    if child and child.poll() is not None:
                        raise ValueError('Model açılamadı. Yapay zekâ kaydını kontrol et.')
                    time.sleep(1)
                else:
                    raise ValueError('Model yükleme süresi aşıldı.')
                with self.guard:
                    if self.cancel.is_set():
                        return
                    self.job.update(status='generating', message='Yanıt bu bilgisayarda üretiliyor.')
                if job['documents']:
                    response = self.library.ask(job['question'], 8086, engine.MODEL_KEY)
                else:
                    body = {'messages': [{'role': 'system', 'content': 'You are FieldDesk, a helpful conversational assistant running on this computer. Have a natural conversation and use the provided recent conversation for follow-up questions. Reply in the language of the latest user message unless they request another language. General chat does not require documents. You cannot access files, browse the web, or run commands in this chat. Be clear and concise, and do not invent facts or claim actions you have not performed.'}] + history + [{'role': 'user', 'content': job['question']}],
                            'max_tokens': 512, 'temperature': 0.4, 'chat_template_kwargs': {'enable_thinking': False}}
                    req = urllib.request.Request('http://127.0.0.1:8086/v1/chat/completions',
                        data=json.dumps(body, ensure_ascii=False).encode(), headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + engine.MODEL_KEY})
                    with urllib.request.urlopen(req, timeout=240) as r:
                        choice = json.load(r)['choices'][0]
                    content = choice['message'].get('content')
                    if not isinstance(content, str) or not content.strip():
                        raise ValueError('Model boş yanıt döndürdü. Yeniden dene veya başka bir model seç.')
                    response = {'answer': content, 'sources': [], 'truncated': choice.get('finish_reason') == 'length'}
                with self.guard:
                    if not self.cancel.is_set():
                        self.job.update(status='complete', message='Yanıt hazır.' + (' Çıktı sınırına ulaşıldı; yanıt kesilmiş olabilir.' if response.get('truncated') else ''), **response)
        except Exception as e:
            with self.guard:
                if not self.cancel.is_set():
                    self.job.update(status='error', message=str(e))

    def stop_model(self):
        with self.guard:
            self.cancel.set()
            if self.job and self.job['status'] in ('loading', 'generating'):
                self.job.update(status='cancelled', message='Yanıt durduruldu.')
            child = engine.RUNNING.get('ai')
            if child and child.poll() is None:
                child.terminate()
            engine.ACTIVE_MODEL = None
        return {'message': 'Yanıt durduruldu; yerel model varsa kapatılıyor. Gönderilmiş API isteğinin sağlayıcıdaki işlemi ve ücreti geri alınamaz; bağlantı kapanana kadar beklemek gerekebilir.'}

    def action(self, route, data):
        if route == '/api/preferences':
            language = data.get('language')
            if language not in ('en', 'tr'):
                raise ValueError('Desteklenmeyen arayüz dili.')
            with self.guard:
                write_json(self.logs / 'arayuz-tercihler.json', {'language': language})
            return {'language': language}
        if route == '/api/catalog/updates':
            with self.guard:return self.package_manager.check_updates()
        if route == '/api/catalog/remove':
            with self.guard:return self.package_manager.remove_package(data.get('id'))
        if route == '/api/catalog/restore':
            with self.guard:return self.package_manager.restore_package(data.get('id'))
        if route == '/api/catalog/install':
            with self.guard:
                return self.package_manager.start(data.get('ids'))
        if route == '/api/catalog/cancel':
            return self.package_manager.cancel_current()
        if route.startswith('/api/providers/'):
            with self.guard:
                if self.worker and self.worker.is_alive():
                    raise ValueError('Önce devam eden yanıtın tamamlanmasını bekle.')
                self.cloud_previews.clear()
                if route == '/api/providers/save':
                    result = self.providers.save(data)
                    self.job = None
                    return result
                if route == '/api/providers/forget':
                    result = self.providers.forget(data.get('provider'))
                    self.job = None
                    return result
                if route == '/api/providers/model':
                    config = self.providers.config(data.get('provider'), data.get('model'))
                    return self.providers.save(dict(config, provider=data['provider']))
                if route == '/api/providers/models':
                    return self.providers.models(data.get('provider'))
                if route == '/api/providers/test':
                    config = self.providers.config(data.get('provider'), data.get('model'))
                    reply = self.providers.chat(data['provider'], config['model'], [], 'Yalnızca OK yaz.')
                    return {'message': 'Metin yanıtı alındı; bağlantı çalışıyor.', 'usage': reply['usage']}
        if route == '/api/chat/preview':
            return self.cloud_preview(data)
        if route == '/api/workflows/cancel':
            return self.workflows.cancel_current()
        if route == '/api/setup/folder':
            if not self.picker_lock.acquire(blocking=False):
                raise ValueError('Klasör seçme penceresi zaten açık.')
            try:
                script = """[Console]::OutputEncoding=[Text.UTF8Encoding]::new(); Add-Type -AssemblyName System.Windows.Forms; $picker=New-Object System.Windows.Forms.FolderBrowserDialog; $picker.Description='ATOLYE canta klasorunu sec'; $picker.SelectedPath=$env:ATOLYE_PICK_ROOT; $picker.ShowNewFolderButton=$true; if($picker.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK){@{path=$picker.SelectedPath}|ConvertTo-Json -Compress}else{@{path=''}|ConvertTo-Json -Compress}; $picker.Dispose()"""
                env = os.environ.copy()
                env['ATOLYE_PICK_ROOT'] = str(self.root)
                result = subprocess.run(['powershell.exe', '-NoProfile', '-STA', '-Command', script],
                    env=env, capture_output=True, encoding='utf-8', timeout=300, creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode:
                    raise ValueError('Klasör penceresi açılamadı. Klasör yolunu alana yazabilirsin.')
                return json.loads(result.stdout)
            finally:
                self.picker_lock.release()
        if route == '/api/setup/preview':
            return setup_preview(data.get('root', str(self.root)))
        if route == '/api/setup/apply':
            return self.setup_apply(data)
        if route == '/api/apps/add':
            with self.guard:
                row = self.custom.add(data)
            return {'message': 'Uygulama menüye eklendi.', 'app': row}
        if route == '/api/apps/remove':
            with self.guard:
                return self.custom.remove(data.get('id'))
        if route == '/api/workflows/preview':
            return self.workflows.preview(data)
        if route == '/api/workflows/run':
            return self.workflows.start(data.get('preview'))
        if route == '/api/workflows/open':
            job = self.workflows.current()
            if not job or job['id'] != data.get('id') or not job.get('output'):
                raise ValueError('İşlem çıktısı bulunamadı.')
            path = safe_path(self.root, job['output'])
            os.startfile(str(path))
            return {'message': 'Çıktı klasörü açıldı.'}
        if route == '/api/chat':
            return self.start_chat(data)
        if route == '/api/model/stop':
            return self.stop_model()
        if route == '/api/chat/clear':
            with self.guard:
                if self.worker and self.worker.is_alive():
                    raise ValueError('Önce devam eden yanıtı durdur.')
                self.job = None
                self.cloud_previews.clear()
            return {'message': 'Sohbet temizlendi.'}
        if route == '/api/favorites':
            favorites = data.get('favorites', [])
            if not isinstance(favorites, list) or any(not isinstance(x, str) for x in favorites):
                raise ValueError('Hatalı favori listesi.')
            valid = {x['id'] for x in self.entries()}
            favorites = sorted(set(favorites) & valid)
            path = self.logs / 'app-tercihler.json'
            temp = path.with_suffix('.tmp')
            temp.write_text(json.dumps({'favorites': favorites}), encoding='utf-8')
            temp.replace(path)
            return {'favorites': favorites}
        if route == '/api/open':
            if data.get('id') not in {x['id'] for x in self.entries()}:
                raise ValueError('Bilinmeyen araç.')
            if str(data.get('id')).startswith('custom-'):
                return self.custom.launch(data['id'])
            if str(data.get('id')).startswith('package-'):
                return self.package_manager.launch(data['id'])
            return {'message': engine.launch(data['id'])}
        if route == '/api/library/open':
            os.startfile(str(self.library.resolve_indexed(str(data.get('path', '')))))
            return {'message': 'Dosya kendi uygulamasında açıldı.'}
        if route == '/api/library/index':
            threading.Thread(target=self.library.index, daemon=True).start()
            return {'message': 'Dosya dizini güncelleniyor.'}
        if route == '/api/package/open':
            package = next((p for p in self.packages() if p['id'] == data.get('id')), None)
            if not package or not package['ready']:
                raise ValueError('Paket bulunamadı.')
            os.startfile(str(safe_path(self.root, package['path']).parent))
            return {'message': 'Paketin bulunduğu klasör açıldı.'}
        if route == '/api/project/open':
            project = next((p for p in self.projects() if p['id'] == data.get('id')), None)
            if not project:
                raise ValueError('Proje bulunamadı.')
            path = safe_path(self.root, project['path'])
            if data.get('editor'):
                code = engine.find_file('01_TASINABILIR/VSCode', 'Code.exe')
                if not code:
                    raise ValueError('Taşınabilir VS Code bulunamadı.')
                subprocess.Popen([str(code), str(path)], cwd=code.parent)
            else:
                os.startfile(str(path))
            return {'message': 'Proje açıldı.'}
        if route == '/api/backup':
            target = self.root / 'YEDEKLE.cmd'
            if not target.is_file():
                raise ValueError('Yedekleme başlatıcısı bulunamadı.')
            os.startfile(str(target))
            return {'message': 'Yedekleme penceresi açıldı. Tanımlı ikinci fiziksel disk gerekir; sonucu bu ekrandan yenileyebilirsin.'}
        raise LookupError('Bulunamadı')


class Handler(http.server.BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(15)

    def log_message(self, *args):
        pass

    @property
    def app(self):
        return self.server.app

    def send(self, data, code=200, content='application/json; charset=utf-8'):
        if not isinstance(data, bytes):
            data = (data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)).encode('utf-8')
        self.send_response(code)
        for key, value in {'Content-Type': content, 'Content-Length': str(len(data)), 'Cache-Control': 'no-store',
                           'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer',
                           'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"}.items():
            self.send_header(key, value)
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def authorized(self, mutate=False):
        origin = f'http://127.0.0.1:{self.app.port}'
        valid = self.headers.get('Host') == f'127.0.0.1:{self.app.port}'
        valid = valid and self.headers.get('Sec-Fetch-Site') != 'cross-site'
        valid = valid and self.headers.get('Origin', origin) == origin
        if mutate:
            valid = valid and secrets.compare_digest(self.headers.get('X-Atolye-Token', ''), self.app.token)
        if not valid:
            # Drain small rejected POSTs so closing the Windows socket does not
            # reset the connection before the client receives the 403 response.
            if self.command == 'POST':
                try:
                    length = int(self.headers.get('Content-Length', '0'))
                    if 0 < length <= 32768:
                        self.rfile.read(length)
                except (ValueError, OSError):
                    pass
            self.send({'message': 'Yetkisiz istek'}, 403)
        return valid

    def do_GET(self):
        if not self.authorized():
            return
        parsed = urllib.parse.urlparse(self.path)
        try:
            if parsed.path in ('/', '/library'):
                html = (STATIC / 'index.html').read_text(encoding='utf-8').replace('__TOKEN__', self.app.token)
                return self.send(html, content='text/html; charset=utf-8')
            assets = {'/i18n.js': 'text/javascript; charset=utf-8', '/app.css': 'text/css; charset=utf-8', '/features.css': 'text/css; charset=utf-8', '/providers.css': 'text/css; charset=utf-8', '/catalog.css': 'text/css; charset=utf-8', '/app.js': 'text/javascript; charset=utf-8', '/features.js': 'text/javascript; charset=utf-8', '/providers.js': 'text/javascript; charset=utf-8', '/catalog.js': 'text/javascript; charset=utf-8', '/icon.svg': 'image/svg+xml'}
            if parsed.path in assets:
                return self.send((STATIC / parsed.path[1:]).read_bytes(), content=assets[parsed.path])
            if parsed.path == '/api/state':
                return self.send(self.app.snapshot())
            if parsed.path == '/api/catalog':
                return self.send(self.app.package_manager.snapshot())
            if parsed.path == '/api/catalog/job':
                return self.send({'job': self.app.package_manager.current(),'updates':self.app.package_manager.update_status()})
            if parsed.path == '/api/job':
                return self.send({'job': self.app.current_job()})
            if parsed.path == '/api/workflows/job':
                return self.send({'job': self.app.workflows.current()})
            if parsed.path == '/api/browse':
                if not self.authorized(mutate=True):
                    return
                query = urllib.parse.parse_qs(parsed.query)
                return self.send(browse(self.app.root, query.get('path', [''])[0], query.get('kind', ['apps'])[0]))
            if parsed.path == '/api/library/search':
                q = urllib.parse.parse_qs(parsed.query).get('q', [''])[0][:500]
                return self.send({'results': self.app.library.search(q)})
            if parsed.path == '/api/library/status':
                return self.send(self.app.library.status())
            self.send({'message': 'Bulunamadı'}, 404)
        except Exception as e:
            self.send({'message': str(e)}, 400)

    def do_POST(self):
        if not self.authorized(mutate=True):
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if self.path == '/api/workflows/upload':
                self.connection.settimeout(120)
                filename = urllib.parse.unquote(self.headers.get('X-Atolye-Filename', ''))
                return self.send(self.app.workflows.register_upload(filename, self.rfile, length))
            if not 0 < length <= 32768:
                raise ValueError('Hatalı istek uzunluğu.')
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError('Bir JSON nesnesi gerekir.')
            if self.path == '/api/shutdown':
                if self.app.package_manager.busy():
                    raise ValueError('Paket indirmesi sürüyor; önce kuyruğu iptal et veya tamamlanmasını bekle.')
                if self.app.workflows.worker and self.app.workflows.worker.is_alive():
                    raise ValueError('İş akışı devam ediyor; tamamlandığında kapatabilirsin.')
                self.app.stop_model()
                self.send({'message': 'FieldDesk kapatılıyor. Açık programlarını kapattıktan sonra diski güvenle çıkar.'})
                threading.Thread(target=self.server.shutdown, daemon=True).start()
                return
            self.send(self.app.action(self.path, data))
        except LookupError as e:
            self.send({'message': str(e)}, 404)
        except Exception as e:
            self.send({'message': str(e)}, 400)


def discover_root():
    if os.environ.get('ATOLYE_ROOT'):
        return Path(os.environ['ATOLYE_ROOT'])
    config = engine.json_file(LOCAL_CONFIG, {})
    candidate = (LOCAL_CONFIG.parent / config['root_relative']) if config.get('root_relative') else Path(config.get('root', '.'))
    if config and candidate.is_dir():
        return candidate.resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / 'atolye-kimlik.json').is_file() or (candidate / '00_BASLANGIC/paketler.json').is_file():
            return candidate
    return Path(__file__).resolve().parents[1] / '.atolye-data'


def main():
    parser = argparse.ArgumentParser(description='FieldDesk — portable local workspace')
    parser.add_argument('--root', type=Path, default=discover_root(), help='ATOLYE çantasının kök klasörü')
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    # Reuse the existing instance for this kit; never start a second model owner.
    session_path = args.root / '00_BASLANGIC/Kayitlar/menu-oturumu.json'
    session = engine.json_file(session_path, {})
    try:
        port = int(session['port'])
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/state', timeout=2) as response:
            info = json.load(response)
            if info.get('version') == VERSION and Path(info.get('root', '')).resolve() == args.root.resolve():
                if not args.no_browser:
                    webbrowser.open(f'http://127.0.0.1:{port}')
                return
    except (OSError, ValueError, KeyError):
        pass
    app = App(args.root)
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.daemon_threads = True
    server.app = app
    app.port = server.server_port
    engine.PORT = app.port
    url = f'http://127.0.0.1:{app.port}'
    write_json(session_path, app.session_file())
    print(url, flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    finally:
        app.stop_model()
        server.server_close()


if __name__ == '__main__':
    main()

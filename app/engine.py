"""Loopback-only portable workshop launcher. Uses Python's standard library."""
import http.server, json, os, pathlib, secrets, subprocess, threading, time, urllib.request, urllib.parse, webbrowser, sys, socket, fnmatch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from library import Library,device_report
from storage import safe_path
ROOT=pathlib.Path(__file__).resolve().parents[2]
TOKEN=secrets.token_urlsafe(32)
MODEL_KEY=secrets.token_urlsafe(32)
PORT=0
RUNNING={}
MODELS={'ai':('Qwen3 4B','Qwen3-4B-Q4_K_M.gguf'),'gemma-e2b':('Gemma 4 E2B','gemma-4-E2B_q4_0-it.gguf'),'gemma-e4b':('Gemma 4 E4B','gemma-4-E4B_q4_0-it.gguf')}
AI_LOCK=threading.RLock()
ACTIVE_MODEL=None
LIBRARY=None
def json_file(path,default):
    try:return json.loads(path.read_text(encoding='utf-8'))
    except (OSError,ValueError):return default
def find_file(folder,name):
    base=ROOT/folder
    if base.exists():
        direct=list(base.glob(name))
        if direct:return min(direct,key=lambda p:len(str(p)))
        paths=list(base.rglob(name)) if '/' not in name else []
        if paths:return min(paths,key=lambda p:len(str(p)))
    receipts=json_file(ROOT/'00_BASLANGIC/Kayitlar/paket-merkezi.json',{})
    if isinstance(receipts,dict):
        for receipt in receipts.values():
            if not isinstance(receipt,dict) or receipt.get('legacy_folder')!=folder:continue
            try:
                path=safe_path(ROOT,receipt['entry'])
                pattern=name.replace('\\','/')
                if path.is_file() and (path.as_posix().casefold().endswith('/'+pattern.casefold()) if '/' in pattern else fnmatch.fnmatch(path.name.casefold(),pattern.casefold())):return path
            except (ValueError,KeyError,TypeError,OSError):pass
    return None
def entries():
    specs=[
      ('vscode','VS Code','Kod yaz, projelerini düzenle','Yazılım','01_TASINABILIR/VSCode','Code.exe'),
      ('notepad','Notepad++','Hızlı metin ve kod düzenleme','Günlük','01_TASINABILIR/NotepadPlusPlus','notepad++.exe'),
      ('sumatra','SumatraPDF','PDF ve e-kitap oku','Günlük','01_TASINABILIR/SumatraPDF','SumatraPDF*.exe'),
      ('winmerge','WinMerge','Dosyaları ve klasörleri karşılaştır','Günlük','01_TASINABILIR/WinMerge','WinMergeU.exe'),
      ('keepassxc','KeePassXC','Kendi parolanla bir parola kasası oluştur','Günlük','01_TASINABILIR/KeePassXC','KeePassXC.exe'),
      ('vlc','VLC','Video ve ses dosyalarını oynat','Medya','01_TASINABILIR/VLC','vlc.exe'),
      ('obs','OBS Studio','Ekran ve video kaydı','Medya','01_TASINABILIR/OBS','bin/64bit/obs64.exe'),
      ('krita','Krita','Çizim ve görsel düzenleme','Tasarım','01_TASINABILIR/Krita','bin/krita.exe'),
      ('blender','Blender','3B modelleme ve animasyon','Tasarım','01_TASINABILIR/Blender','blender.exe'),
      ('dbbrowser','DB Browser','SQLite veritabanlarını görsel olarak düzenle','Yazılım','01_TASINABILIR/DBBrowser','DB Browser for SQLite.exe'),
      ('libreoffice-app','LibreOffice','Belge, tablo ve sunum hazırla','Ofis','01_TASINABILIR/LibreOffice','program/soffice.exe'),
    ]
    result=[]
    for id,name,desc,cat,folder,exe in specs:
        path=find_file(folder,exe)
        result.append(dict(id=id,name=name,description=desc,category=cat,ready=bool(path),path=str(path) if path else None,type='app'))
    for id,name,desc,cat,rel in [
      ('projects','Projelerim','Bilgisayarından alınan proje kopyaları','Dosyalar','04_PROJELER'),
      ('design','Tasarım dosyaları','Marka, görsel ve medya dosyaları','Dosyalar','06_TASARIM_MEDYA'),
      ('templates','Başlangıç projeleri','Hazırlanmış web ve Python örnekleri','Yazılım','03_YAZILIM/Sablonlar'),
      ('installers','Kurulum arşivi','Orijinal kurulum ve dağıtım paketleri','Kurulum','02_KURULUMLAR'),
      ('rescue','Kurtarma araçları','Kurtarma ISO ve USB hazırlama paketi','Kurtarma','07_KURTARMA'),
      ('docs','Bilgi bankası','Çevrimdışı belgeler ve rehberler','Belgeler','08_BILGI_BANKASI'),
      ('python-docs','Python belgeleri','Python kılavuzunu çevrimdışı oku','Belgeler','08_BILGI_BANKASI/Python'),
      ('sqlite-docs','SQLite belgeleri','Veritabanı belgelerini çevrimdışı oku','Belgeler','08_BILGI_BANKASI/SQLite'),
    ]:
        path=ROOT/rel
        if id in ('python-docs','sqlite-docs'):
            candidates=list(path.glob('index.html')) if path.exists() else []
            if candidates:path=min(candidates,key=lambda p:len(str(p)))
        result.append(dict(id=id,name=name,description=desc,category=cat,ready=path.exists(),path=str(path),type='folder'))
    model=ROOT/'05_YAPAY_ZEKA/Modeller/Qwen3-4B-Q4_K_M.gguf'
    result.append(dict(id='ai',name='Çevrimdışı yapay zekâ',description='Qwen3 4B · internet ve API anahtarı gerekmez',category='Yapay zekâ',ready=bool(find_file('01_TASINABILIR/llama.cpp','llama-server.exe')) and model.exists(),type='ai'))
    for id in ('gemma-e2b','gemma-e4b'):
        name,filename=MODELS[id]
        result.append(dict(id=id,name=name,description='Google modeli · çevrimdışı yerel sohbet',category='Yapay zekâ',ready=(ROOT/'05_YAPAY_ZEKA/Modeller'/filename).exists(),type='ai'))
    result.append(dict(id='library',name='Bilgi merkezi',description='Dosyalarında ara, yerel asistana sor, bilgisayarı hazırla',category='Belgeler',ready=True,type='page'))
    result.append(dict(id='os-archive',name='İşletim sistemi arşivi',description='Windows ve Ubuntu medyaları',category='Kurulum',ready=(ROOT/'10_ISLETIM_SISTEMLERI').exists(),path=str(ROOT/'10_ISLETIM_SISTEMLERI'),type='folder'))
    result.append(dict(id='terminal',name='Geliştirme ortamı',description='Python, Node.js, Git ve diğer araçlar hazır',category='Yazılım',ready=(ROOT/'GELISTIRME.cmd').exists(),path=str(ROOT/'GELISTIRME.cmd'),type='terminal'))
    return result

def model_healthy():
    try:
        req=urllib.request.Request('http://127.0.0.1:8086/health',headers={'Authorization':'Bearer '+MODEL_KEY})
        with urllib.request.urlopen(req,timeout=1) as r:return r.status==200
    except Exception:return False

def ensure_model(id):
    global ACTIVE_MODEL
    if id not in MODELS:raise ValueError('Bilinmeyen model.')
    name,filename=MODELS[id];model=ROOT/'05_YAPAY_ZEKA/Modeller'/filename
    if not model.exists():raise ValueError('Model indirmesi henüz tamamlanmadı.')
    with AI_LOCK:
        child=RUNNING.get('ai')
        if ACTIVE_MODEL==id and child and child.poll() is None:return 8086
        if child and child.poll() is None:
            child.terminate()
            try:child.wait(timeout=15)
            except subprocess.TimeoutExpired:child.kill();child.wait()
        with socket.socket() as probe:
            if probe.connect_ex(('127.0.0.1',8086))==0:raise ValueError('8086 portu başka bir uygulama tarafından kullanılıyor. O uygulamayı kapatıp tekrar dene.')
        exe=find_file('01_TASINABILIR/llama.cpp','llama-server.exe');log=(ROOT/'00_BASLANGIC/Kayitlar/yapay-zeka.log').open('a',encoding='utf-8')
        RUNNING['ai']=subprocess.Popen([str(exe),'-m',str(model),'--host','127.0.0.1','--port','8086','-c','4096','--parallel','1','-t','4','-ngl','0','--jinja','--load-mode','none','--no-agent','--api-key',MODEL_KEY,'--cors-origins',f'http://127.0.0.1:{PORT}'],cwd=exe.parent,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW);ACTIVE_MODEL=id
        log.close()
    return 8086

def wait_model():
    for _ in range(600):
        if model_healthy():return
        child=RUNNING.get('ai')
        if child and child.poll() is not None:raise ValueError('Model açılamadı. Kayitlar/yapay-zeka.log dosyasını kontrol et.')
        time.sleep(1)
    raise ValueError('Model yükleme süresi aşıldı.')
def launch(id):
    entry=next((x for x in entries() if x['id']==id),None)
    if not entry or not entry['ready']:raise ValueError('Bu öğe henüz hazır değil.')
    if entry['type']=='page':webbrowser.open(f'http://127.0.0.1:{PORT}/library');return 'Bilgi merkezi açıldı.'
    env=os.environ.copy();profile=ROOT/'00_BASLANGIC/Profil'
    for key,folder in [('APPDATA','AppData'),('LOCALAPPDATA','LocalAppData')]:
        p=profile/folder;p.mkdir(parents=True,exist_ok=True);env[key]=str(p)
    if entry['type']=='ai':
        port=ensure_model(id)
        def wait_open():
            try:wait_model();webbrowser.open(f'http://127.0.0.1:{port}')
            except Exception:pass
        threading.Thread(target=wait_open,daemon=True).start()
        return 'Model hazırlanıyor. Hazır olduğunda sohbet sayfası açılacak.'
    path=pathlib.Path(entry['path']).resolve()
    if not path.is_relative_to(ROOT.resolve()):raise ValueError('Hedef çanta dışında.')
    if entry['type'] in ('folder','terminal'):os.startfile(str(path));return 'Açıldı.'
    args=[str(path)]
    if id=='vlc':
        p=profile/'VLC';p.mkdir(exist_ok=True);args+=['--config',str(p/'vlcrc'),'--no-media-library']
    if id=='libreoffice-app':args+=['-env:UserInstallation='+(profile/'LibreOffice').as_uri()]
    if id=='obs':args+=['--portable']
    subprocess.Popen(args,cwd=path.parent,env=env)
    return entry['name']+' açıldı.'

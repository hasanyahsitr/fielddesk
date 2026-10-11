"""Resumable cache paths, reversible managed-package removal, publisher version checks."""
from concurrent.futures import ThreadPoolExecutor
import copy
import datetime
import json
from pathlib import Path
import re
import threading
import time
import urllib.parse
import urllib.request
import uuid
from providers import HTTPS, NoRedirect
from storage import safe_path, write_json, plain_child


MANUAL={
 'vlc':'https://www.videolan.org/vlc/', 'krita':'https://krita.org/en/download/',
 'blender':'https://www.blender.org/download/', 'sqlite':'https://www.sqlite.org/download.html',
 'libreoffice':'https://www.libreoffice.org/download/download-libreoffice/',
 'python-installer':'https://www.python.org/downloads/windows/'}


def fetch_json(url):
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),HTTPS(),NoRedirect())
    request=urllib.request.Request(url,headers={'User-Agent':'ATOLYE/0.6 version check','Accept':'application/json'})
    with opener.open(request,timeout=12) as response:
        content=response.read(4*1024**2+1)
        if len(content)>4*1024**2:raise ValueError('Sürüm yanıtı boyut sınırını aştı.')
        return json.loads(content)


def version_key(value):
    if not isinstance(value,str) or len(value)>80 or not re.search(r'\d',value):raise ValueError('Sürüm bilgisi tanınmadı.')
    return tuple(int(x) for x in re.findall(r'\d+',value))


def check_publisher(row):
    ident=row['id'];url=row['url'];parsed=urllib.parse.urlsplit(url)
    result={'status':'manual','url':MANUAL.get(ident,url),'message':'Yayıncı sayfasından kontrol et; otomatik sürüm kontrolü yok.'}
    if ident in MANUAL:return result
    try:
        if parsed.hostname=='github.com' or ident=='sumatra':
            repo='/'.join(parsed.path.strip('/').split('/')[:2]) if ident!='sumatra' else 'sumatrapdfreader/sumatrapdf'
            result['url']='https://github.com/'+repo+'/releases'
            data=fetch_json('https://api.github.com/repos/'+repo+'/releases/latest')
            if data.get('draft') or data.get('prerelease'):raise ValueError('Kararlı sürüm bulunamadı.')
            latest=data['tag_name']
        elif ident=='vscode':
            result['url']='https://code.visualstudio.com/updates'
            latest=fetch_json('https://update.code.visualstudio.com/api/update/win32-x64-archive/stable/latest')['productVersion']
        elif ident=='node':
            result['url']='https://nodejs.org/en/download'
            latest=next(x['version'] for x in fetch_json('https://nodejs.org/dist/index.json') if x.get('lts'))
        elif ident=='dotnet':
            result['url']='https://dotnet.microsoft.com/download/dotnet'
            data=fetch_json('https://builds.dotnet.microsoft.com/dotnet/release-metadata/releases-index.json')
            candidates=[x['latest-sdk'] for x in data['releases-index'] if x.get('support-phase') in ('active','maintenance') and re.fullmatch(r'\d+\.\d+\.\d+',x.get('latest-sdk',''))]
            latest=max(candidates,key=version_key)
        else:return result
        comparison=(version_key(latest)>version_key(row['version']))-(version_key(latest)<version_key(row['version']))
        result.update(latest=latest,status='available' if comparison>0 else 'current' if comparison==0 else 'catalog_ahead',
            message='Yeni yayıncı sürümü var · katalog güncellemesi gerekiyor.' if comparison>0 else 'Katalog sürümü yayıncıyla eşleşiyor.' if comparison==0 else 'Yayıncının latest kanalı katalogdan daha eski; indirme değiştirilmedi.')
    except Exception:
        result.update(status='error',message='Kontrol edilemedi · internet veya yayıncı API kotası. Güncel olduğu varsayılmadı.')
    return result


class Lifecycle:
    def init_lifecycle(self):
        self.launched={};self.update_worker=None
        self.update_file=safe_path(self.root,'00_BASLANGIC/Kayitlar/paket-surumleri.json')
        try:self.updates=json.loads(self.update_file.read_text(encoding='utf-8'))
        except (OSError,ValueError):self.updates={}
        if not isinstance(self.updates,dict) or not isinstance(self.updates.get('results'),dict):self.updates={'status':'idle','results':{},'message':'Henüz sürüm kontrolü yapılmadı.'}
        if self.updates.get('status')=='running':self.updates['status']='idle'

    def busy(self):
        return bool(self.worker and self.worker.is_alive() or self.update_worker and self.update_worker.is_alive())

    def partial_path(self,row):
        name=Path(urllib.parse.urlsplit(row['url']).path).name
        relative='02_KURULUMLAR/PaketMerkezi/'+row['id']+'-'+row['sha256'][:12]+'-'+name+'.part'
        raw=self.root/relative;resolved=safe_path(self.root,relative)
        if raw!=resolved or not plain_child(raw):raise ValueError('Yarım indirme yolu bağlantı içeriyor.')
        return resolved

    def update_status(self):
        with self.lock:return copy.deepcopy(self.updates)

    def check_updates(self):
        with self.lock:
            if self.busy():raise ValueError('Önce devam eden paket işlemini bekle.')
            if time.time()-self.updates.get('checked_epoch',0)<600:return self.update_status()
            self.updates={'status':'running','results':{},'done':0,'total':len(self.catalog),'message':'Yayıncı sürümleri kontrol ediliyor…'}
            self.update_worker=threading.Thread(target=self.run_updates,daemon=True);self.update_worker.start()
            return self.update_status()

    def run_updates(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            for row,result in zip(self.catalog,pool.map(check_publisher,self.catalog)):
                with self.lock:self.updates['results'][row['id']]=result;self.updates['done']+=1
        with self.lock:
            manual=sum(x['status']=='manual' for x in self.updates['results'].values())
            errors=sum(x['status']=='error' for x in self.updates['results'].values())
            new=sum(x['status']=='available' for x in self.updates['results'].values())
            self.updates.update(status='complete',checked_epoch=time.time(),checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),message=f'{new} yeni sürüm · {manual} yayıncı sayfasından kontrol · {errors} kontrol hatası. Karşılaştırma katalog sürümünedir; otomatik güncelleme yapılmaz.')
            try:write_json(self.update_file,self.updates)
            except OSError:self.updates['message']+=' Sonuç diske kaydedilemedi.'

    def removed(self):
        base=safe_path(self.root,'00_BASLANGIC/KaldirilanPaketler')
        result=[]
        if base.is_dir():
            for folder in base.iterdir():
                if not folder.is_dir() or not plain_child(folder) or not re.fullmatch('[0-9a-f]{12}',folder.name):continue
                try:
                    data=json.loads((folder/'kayit.json').read_text(encoding='utf-8'))
                    if data.get('status')=='removed' and data['package'] in self.by_id:
                        result.append({'id':folder.name,'package':data['package'],'name':self.by_id[data['package']]['name'],'date':data['date']})
                except (OSError,ValueError,KeyError,TypeError):pass
        return sorted(result,key=lambda x:x['date'],reverse=True)

    def owned_target(self,ident,receipt):
        path=safe_path(self.root,receipt['entry'])
        sha=receipt.get('sha256','')
        if not re.fullmatch('[0-9a-f]{64}',sha):raise ValueError('Paket kaydı doğrulanamadı.')
        app_raw=self.root/'01_TASINABILIR/PaketMerkezi'/(ident+'-'+sha[:12]);cache_raw=self.root/'02_KURULUMLAR/PaketMerkezi'
        app=safe_path(self.root,app_raw);cache=safe_path(self.root,cache_raw)
        if app_raw!=app or cache_raw!=cache or path!=self.root/receipt['entry']:raise ValueError('Paket yolu bağlantı içeriyor; dosyalar korundu.')
        if path.is_relative_to(app):return app
        if path.parent==cache and path.name.startswith(ident+'-'+sha[:12]+'-'):return path
        # A v0.5 installer may reuse a pre-existing shared archive. Never move that original.
        if self.by_id[ident]['kind']=='installer' and self.by_id[ident].get('existing_archive') and path==safe_path(self.root,self.by_id[ident]['existing_archive']):return None
        raise ValueError('Yalnızca Paket merkezinin yönettiği dosyalar kaldırılabilir.')

    def remove_package(self,ident):
        with self.lock:
            if self.busy():raise ValueError('Önce devam eden paket işlemini bekle.')
            if ident not in self.by_id or ident not in self.receipts:raise ValueError('Yalnızca yönetilen bir paket kaldırılabilir.')
            running=self.launched.get('package-'+ident)
            if running and running.poll() is None:raise ValueError('Önce bu uygulamanın açık penceresini kapat.')
            receipt=copy.deepcopy(self.receipts[ident]);target=self.owned_target(ident,receipt)
            trash=safe_path(self.root,'00_BASLANGIC/KaldirilanPaketler/'+uuid.uuid4().hex[:12]);trash.mkdir(parents=True,exist_ok=False)
            moved=bool(target and target.exists())
            if moved and not plain_child(target):raise ValueError('Bağlantı yolu kaldırılmaz.')
            record={'package':ident,'receipt':receipt,'original':target.relative_to(self.root).as_posix() if target else None,'moved':moved,'date':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'removed'}
            write_json(trash/'kayit.json',record)
            try:
                if moved:target.rename(trash/'icerik')
                receipts=dict(self.receipts);receipts.pop(ident);write_json(self.receipt_file,receipts);self.receipts=receipts
            except OSError:
                if moved and (trash/'icerik').exists() and not target.exists():(trash/'icerik').rename(target)
                record['status']='rolled_back';write_json(trash/'kayit.json',record)
                raise ValueError('Paket kaldırılamadı; açık programı kapatıp yeniden dene.') from None
            return {'message':'Paket menüden kaldırıldı. Dosyalar geri almak için saklandı; disk alanı henüz boşaltılmadı.'}

    def restore_package(self,removal):
        if not isinstance(removal,str) or not re.fullmatch('[0-9a-f]{12}',removal):raise ValueError('Geri alma kaydı geçersiz.')
        with self.lock:
            if self.busy():raise ValueError('Önce devam eden paket işlemini bekle.')
            trash=safe_path(self.root,'00_BASLANGIC/KaldirilanPaketler/'+removal)
            try:record=json.loads((trash/'kayit.json').read_text(encoding='utf-8'))
            except (OSError,ValueError):raise ValueError('Geri alma kaydı bulunamadı.') from None
            ident=record.get('package')
            if record.get('status')!='removed' or ident not in self.by_id:raise ValueError('Geri alma kaydı geçersiz.')
            if self.locate(self.by_id[ident])[1]:raise ValueError('Bu paket zaten hazır; mevcut sürümün üzerine yazılmadı.')
            target=self.owned_target(ident,record['receipt']);payload=safe_path(trash,'icerik');moved=False
            if record['moved'] and payload.exists():
                if target is None or record['original']!=target.relative_to(self.root).as_posix() or target.exists() or not plain_child(payload):raise ValueError('Eski konum dolu veya değişmiş; dosyalar korundu.')
                target.parent.mkdir(parents=True,exist_ok=True);payload.rename(target);moved=True
            entry=safe_path(self.root,record['receipt']['entry'])
            valid=entry.is_file()
            if valid and self.by_id[ident]['kind']=='installer':
                valid=entry.stat().st_size==record['receipt'].get('bytes') and entry.stat().st_mtime_ns==record['receipt'].get('mtime_ns')
            if not valid:
                if moved:target.rename(payload)
                raise ValueError('Geri alınacak dosya bulunamadı veya değiştirilmiş; otomatik kullanılmadı.')
            receipts=dict(self.receipts,**{ident:record['receipt']})
            try:write_json(self.receipt_file,receipts)
            except OSError:
                if moved:target.rename(payload)
                raise ValueError('Kayıt yazılamadı; geri alma tamamlanmadı.') from None
            self.receipts=receipts;record['status']='restored';write_json(trash/'kayit.json',record)
            return {'message':'Paket geri alındı ve menüye eklendi.'}

"""Pinned publisher packages; download and prepare, never execute installers."""
from __future__ import annotations
import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
from providers import HTTPS
from storage import safe_path, write_json, plain_child
from package_lifecycle import Lifecycle

CATALOG = Path(__file__).with_name('catalog.json')


class Cancelled(Exception):pass


def check_url(url):
    p=urllib.parse.urlsplit(url)
    if p.scheme!='https' or not p.hostname or p.username or p.password or p.port not in (None,443):
        raise ValueError('Paket adresi yalnızca HTTPS olabilir.')
    return url


class Redirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        check_url(newurl)
        return super().redirect_request(req,fp,code,msg,headers,newurl)


def open_download(url,offset=0):
    check_url(url)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}), HTTPS(), Redirect())
    headers={'User-Agent':'ATOLYE/0.6 package downloader','Accept-Encoding':'identity'}
    if offset:headers['Range']='bytes='+str(offset)+'-'
    return opener.open(urllib.request.Request(url,headers=headers),timeout=30)


def zip_plan(archive):
    items=archive.infolist()
    if not items or len(items)>100_000:raise ValueError('Arşiv dosya sayısı sınırını aştı.')
    total=0;seen=set();result=[]
    for item in items:
        name=item.filename.replace('\\','/')
        path=PurePosixPath(name)
        parts=name.rstrip('/').split('/')
        if path.is_absolute() or any(p in ('','.', '..') or ':' in p or p.endswith(('.', ' ')) or any(ord(c)<32 for c in p) or re.fullmatch(r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?',p,re.I) for p in parts):
            raise ValueError('Arşiv güvenli olmayan dosya yolu içeriyor.')
        if any(c in name for c in '<>"|?*') or stat.S_ISLNK(item.external_attr>>16) or item.flag_bits&1:
            raise ValueError('Arşiv bağlantı, şifreli veya desteklenmeyen dosya içeriyor.')
        folded=path.as_posix().casefold()
        if folded in seen:raise ValueError('Arşivde çakışan dosya adları var.')
        seen.add(folded)
        total+=item.file_size
        if total>8*1024**3 or item.file_size>4*1024**3 or item.file_size>max(1,item.compress_size)*1000:
            raise ValueError('Arşiv açılmış boyut sınırını aştı.')
        result.append((item,path.as_posix()))
    return result,total


class Packages(Lifecycle):
    def __init__(self, root, catalog=None):
        self.root=Path(root).resolve()
        self.catalog=json.loads((Path(catalog) if catalog else CATALOG).read_text(encoding='utf-8'))['packages']
        self.by_id={x['id']:x for x in self.catalog}
        if len(self.by_id)!=len(self.catalog):raise ValueError('Çakışan katalog kimliği.')
        for x in self.catalog:
            if not re.fullmatch('[a-z0-9-]{1,50}',x['id']) or not re.fullmatch('[0-9a-f]{64}',x['sha256']) or not 0<x['bytes']<2*1024**3 or x['kind'] not in ('zip','exe','installer'):
                raise ValueError('Katalog kaydı geçersiz.')
            check_url(x['url'])
            safe_path(self.root,x['entry'])
            for key in ('existing_folder','existing_archive'):
                if x.get(key):safe_path(self.root,x[key])
        self.receipt_file=safe_path(self.root,'00_BASLANGIC/Kayitlar/paket-merkezi.json')
        self.lock=threading.RLock();self.worker=None;self.cancel=threading.Event();self.job=None
        try:self.receipts=json.loads(self.receipt_file.read_text(encoding='utf-8'))
        except (OSError,ValueError):self.receipts={}
        if not isinstance(self.receipts,dict):self.receipts={}
        self.init_lifecycle()

    def current(self):
        with self.lock:return copy.deepcopy(self.job)

    def locate(self,row):
        receipt=self.receipts.get(row['id'],{})
        if not isinstance(receipt,dict):receipt={}
        if receipt.get('sha256')==row['sha256']:
            try:
                path=safe_path(self.root,receipt['entry'])
                if path.is_file():
                    if row['kind']!='installer' or (path.stat().st_size==receipt.get('bytes') and path.stat().st_mtime_ns==receipt.get('mtime_ns')):
                        return path,True
            except (KeyError,TypeError,ValueError,OSError):pass
        folder=row.get('existing_folder')
        if folder and row['kind']!='installer':
            base=safe_path(self.root,folder)
            # Existing prepared kit files are preserved, not reported as this catalog version.
            if base.is_dir():
                direct=safe_path(base,row['entry'])
                if direct.is_file():return direct,False
                candidates=[p for p in base.rglob(Path(row['entry']).name) if p.is_file() and p.resolve().is_relative_to(self.root) and plain_child(p)]
                if candidates:return min(candidates,key=lambda p:len(str(p))),False
        return None,False

    def snapshot(self):
        with self.lock:
            rows=[]
            for row in self.catalog:
                path,managed=self.locate(row)
                partial=self.partial_path(row)
                partial_bytes=partial.stat().st_size if partial.is_file() else 0
                active=next((x for x in (self.job or {}).get('items',[]) if x['id']==row['id']),None)
                code='installer' if path and row['kind']=='installer' else 'ready' if path and managed else 'existing' if path else 'paused' if partial_bytes else 'available'
                if active and not path and active['state'] in ('queued','downloading','verifying','extracting','error'):code=active['state']
                labels={'installer':'Kurulum dosyası hazır','ready':'Kullanmaya hazır','existing':'Çantada mevcut · sürüm bilinmiyor','paused':'Yarım kaldı · devam edilebilir','available':'İndirilebilir','queued':'Sırada','downloading':'İndiriliyor','verifying':'Doğrulanıyor','extracting':'Hazırlanıyor','error':'İşlem tamamlanamadı'}
                rows.append({k:v for k,v in row.items() if k not in ('existing_archive','existing_folder','entry')}|{'ready':bool(path),'managed':managed,'state_code':code,'state':labels[code],'partial_bytes':partial_bytes,'message':active['message'] if active and code=='error' else '', 'update':self.updates.get('results',{}).get(row['id'])})
            return {'packages':rows,'job':self.current(),'updates':self.update_status(),'removed':self.removed(),'reviewed':'2026-10-11','platform':'Windows x64'}

    def entries(self):
        result=[]
        with self.lock:
            for row in self.catalog:
                if row['id'] not in self.receipts:continue
                path,managed=self.locate(row)
                if not path or not managed:continue
                folder=row['kind']=='installer' or row.get('cli')
                result.append({'id':'package-'+row['id'],'name':row['name'],'category':row['category'],
                    'description':row['description']+(' · Klasörü aç' if folder else ''),'ready':True,
                    'type':'folder' if folder else 'app','path':str(path.parent if folder else path),'package':True})
        return result

    def launch(self, ident):
        row=next((x for x in self.entries() if x['id']==ident),None)
        if not row:raise ValueError('Hazırlanmış paket bulunamadı.')
        path=safe_path(self.root,Path(row['path']).relative_to(self.root))
        if row['type']=='folder':os.startfile(str(path))
        else:
            env=os.environ.copy()
            for key in ('APPDATA','LOCALAPPDATA'):
                profile=safe_path(self.root,'00_BASLANGIC/Profil/PaketMerkezi/'+ident+'/'+key)
                profile.mkdir(parents=True,exist_ok=True);env[key]=str(profile)
            process=subprocess.Popen([str(path)],cwd=path.parent,env=env)
            self.launched[ident]=process
        return {'message':row['name']+' açıldı.'}

    def start(self, ids):
        if not isinstance(ids,list) or not 1<=len(ids)<=40 or any(not isinstance(x,str) or x not in self.by_id for x in ids):
            raise ValueError('Katalogdan en az bir paket seç.')
        ids=list(dict.fromkeys(ids))
        with self.lock:
            if self.busy():raise ValueError('Bir paket işlemi zaten çalışıyor.')
            self.cancel=threading.Event()
            self.job={'id':uuid.uuid4().hex[:12],'status':'running','message':'Seçilen paketler hazırlanıyor.','items':[{'id':ident,'name':self.by_id[ident]['name'],'state':'queued','bytes':0,'total':self.by_id[ident]['bytes'],'message':'Sırada'} for ident in ids],'done':0,'total':len(ids)}
            self.worker=threading.Thread(target=self.run,daemon=True);self.worker.start()
            return self.current()

    def cancel_current(self):
        self.cancel.set()
        with self.lock:
            if self.job and self.job['status']=='running':self.job['message']='İptal ediliyor. Bekleyen ağ okuması en fazla 30 saniye sürebilir.'
        return {'message':'İndirme kuyruğu iptal ediliyor.'}

    def check_cancel(self):
        if self.cancel.is_set():raise Cancelled()

    def update(self,item,**kwargs):
        with self.lock:item.update(kwargs)

    def sha(self,path):
        digest=hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda:stream.read(1024**2),b''):
                self.check_cancel();digest.update(chunk)
        return digest.hexdigest()

    def download(self,row,item):
        cache=safe_path(self.root,'02_KURULUMLAR/PaketMerkezi');cache.mkdir(parents=True,exist_ok=True)
        filename=Path(urllib.parse.urlsplit(row['url']).path).name
        if not re.fullmatch(r'[A-Za-z0-9._+ -]+',filename):raise ValueError('Paket dosya adı geçersiz.')
        target=safe_path(cache,row['id']+'-'+row['sha256'][:12]+'-'+filename)
        for candidate in (target,safe_path(self.root,row.get('existing_archive') or '02_KURULUMLAR/__none__')):
            if candidate.is_file() and candidate.stat().st_size==row['bytes']:
                self.update(item,state='verifying',message='Mevcut arşiv doğrulanıyor…')
                if self.sha(candidate)==row['sha256']:return candidate
                if candidate==target:raise ValueError('Önbellekteki arşiv değiştirilmiş; dosya korundu, otomatik kullanılmadı.')
        if target.exists():raise ValueError('Hedef arşiv zaten var; mevcut dosya korundu.')
        part=self.partial_path(row)
        if part.exists() and (not part.is_file() or not plain_child(part)):raise ValueError('Yarım indirme yolu güvenli değil.')
        count=part.stat().st_size if part.exists() else 0
        if count>row['bytes']:raise ValueError('Yarım dosya beklenenden büyük; otomatik kullanılmadı.')
        if shutil.disk_usage(cache).free<row['bytes']-count+100*1024**2:raise ValueError('İndirme için yeterli boş disk alanı yok.')
        if count==row['bytes']:
            if self.sha(part)==row['sha256']:part.rename(target);return target
            part.unlink();count=0
        digest=hashlib.sha256()
        if count:
            with part.open('rb') as prefix:
                for chunk in iter(lambda:prefix.read(1024**2),b''):self.check_cancel();digest.update(chunk)
        self.update(item,state='downloading',bytes=count,message='Kaldığı yerden indiriliyor…' if count else 'Resmî kaynaktan indiriliyor…')
        deadline=time.monotonic()+2700;discard=False
        try:
            response=open_download(row['url'],count) if count else open_download(row['url'])
            with response:
                if count and response.status==200:
                    count=0;digest=hashlib.sha256();self.update(item,bytes=0,message='Sunucu devam etmeyi desteklemiyor; yeniden indiriliyor…')
                elif count:
                    expected=f'bytes {count}-{row["bytes"]-1}/{row["bytes"]}'
                    if response.status!=206 or response.headers.get('Content-Range')!=expected:raise ValueError('Devam yanıtı doğrulanamadı; mevcut yarım dosya korundu.')
                elif response.status!=200:raise ValueError('İndirme sunucusu dosyayı vermedi.')
                length=response.headers.get('Content-Length')
                if length and int(length)!=row['bytes']-count:raise ValueError('Yayıncı dosyasının boyutu katalogla eşleşmiyor.')
                with part.open('ab' if count else 'wb') as stream:
                    while True:
                        self.check_cancel()
                        if time.monotonic()>deadline:raise ValueError('İndirme toplam süre sınırını aştı.')
                        chunk=response.read(1024**2)
                        self.check_cancel()
                        if not chunk:break
                        count+=len(chunk)
                        if count>row['bytes']:discard=True;raise ValueError('Dosya boyutu katalog sınırını aştı.')
                        stream.write(chunk);digest.update(chunk);self.update(item,bytes=count)
            self.check_cancel();self.update(item,state='verifying',message='SHA-256 doğrulanıyor…')
            if count!=row['bytes']:raise ValueError('İndirme eksik; yeniden seçerek kaldığı yerden devam edebilirsin.')
            if digest.hexdigest()!=row['sha256']:discard=True;raise ValueError('SHA-256 eşleşmedi; bozuk indirme silindi, paket hazırlanmadı.')
            if target.exists():raise ValueError('Arşiv hedefi değişti; dosyalar korundu.')
            part.rename(target)
            return target
        except urllib.error.HTTPError as error:
            error.close();raise ValueError('İndirme sunucusu HTTP '+str(error.code)+' hatası verdi. Daha sonra yeniden dene.') from None
        except (urllib.error.URLError,OSError):
            raise ValueError('İndirme kesildi. Yarım dosya korundu; yeniden seçerek devam edebilirsin.') from None
        finally:
            if part.exists() and (discard or part.stat().st_size==0) and part.resolve().is_relative_to(cache) and plain_child(part):part.unlink()

    def prepare(self,row,item):
        self.check_cancel()
        existing,_=self.locate(row)
        if existing:
            self.update(item,state='skipped',message='Zaten mevcut; tekrar indirilmedi.');return
        archive=self.download(row,item)
        self.check_cancel()
        if row['kind']=='installer':
            with archive.open('rb') as f:magic=f.read(8)
            if not (magic.startswith(b'MZ') or magic==bytes.fromhex('d0cf11e0a1b11ae1')):raise ValueError('Kurulum dosyası biçimi beklenenden farklı.')
            destination=archive
        else:
            base=safe_path(self.root,'01_TASINABILIR/PaketMerkezi');base.mkdir(parents=True,exist_ok=True)
            destination=safe_path(base,row['id']+'-'+row['sha256'][:12])
            if destination.exists():raise ValueError('Hedef klasör zaten var; üzerine yazılmadı.')
            staging=safe_path(base,'.hazirlama-'+self.job['id']+'-'+row['id'])
            staging.mkdir(exist_ok=False)
            try:
                self.update(item,state='extracting',message='Arşiv açılıyor ve menü hazırlanıyor…')
                if row['kind']=='zip':
                    with zipfile.ZipFile(archive) as z:
                        plan,total=zip_plan(z)
                        if os.name=='nt' and any(len(str(staging/relative))>=(248 if member.is_dir() else 260) for member,relative in plan):
                            raise ValueError('Çanta yolu Windows için çok uzun. D:\\ATOLYE gibi daha kısa bir klasör seç; doğrulanmış arşiv korundu.')
                        if shutil.disk_usage(base).free<total+100*1024**2:raise ValueError('Arşivi açmak için yeterli boş alan yok.')
                        for member,relative in plan:
                            self.check_cancel();output=safe_path(staging,relative)
                            if member.is_dir():output.mkdir(parents=True,exist_ok=True);continue
                            output.parent.mkdir(parents=True,exist_ok=True)
                            with z.open(member) as source,output.open('xb') as target:
                                while True:
                                    self.check_cancel();chunk=source.read(1024**2)
                                    if not chunk:break
                                    target.write(chunk)
                else:shutil.copyfile(archive,staging/row['entry'])
                candidates=[p for p in staging.rglob(Path(row['entry']).name) if p.is_file() and p.relative_to(staging).as_posix().casefold().endswith(row['entry'].casefold())]
                if len(candidates)!=1:raise ValueError('Arşivde beklenen uygulama bulunamadı veya adı belirsiz.')
                entry=candidates[0]
                with entry.open('rb') as f:
                    if f.read(2)!=b'MZ':raise ValueError('Beklenen Windows uygulaması bulunamadı.')
                if row['id'] in ('vscode','vscodium'):(entry.parent/'data').mkdir(exist_ok=True)
                if row['id']=='obs':(staging/'portable_mode.txt').touch()
                if row['id']=='localsend':(entry.parent/'portable.txt').touch()
                self.check_cancel();relative=entry.relative_to(staging)
                if destination.exists():raise ValueError('Hedef klasör değişti; üzerine yazılmadı.')
                staging.rename(destination);destination=destination/relative
            finally:
                if staging.exists() and staging.resolve().is_relative_to(base) and plain_child(staging):shutil.rmtree(staging)
        receipt={'version':row['version'],'sha256':row['sha256'],'entry':destination.relative_to(self.root).as_posix(),'bytes':destination.stat().st_size,'mtime_ns':destination.stat().st_mtime_ns,'legacy_folder':row.get('existing_folder','')}
        try:
            with self.lock:
                receipts=dict(self.receipts,**{row['id']:receipt});write_json(self.receipt_file,receipts);self.receipts=receipts
        except OSError:
            # Only our newly created directory is rolled back. Verified archives remain reusable.
            if row['kind']!='installer':
                created=safe_path(self.root,'01_TASINABILIR/PaketMerkezi/'+row['id']+'-'+row['sha256'][:12])
                if created.is_dir() and plain_child(created):shutil.rmtree(created)
            raise
        self.update(item,state='complete',bytes=row['bytes'],message='Kurulum dosyası indirildi; otomatik çalıştırılmadı.' if row['kind']=='installer' else 'Doğrulandı, hazırlandı ve menüye eklendi.')

    def run(self):
        for item in self.job['items']:
            try:self.prepare(self.by_id[item['id']],item)
            except Cancelled:
                self.update(item,state='cancelled',message='İptal edildi.')
                for pending in self.job['items']:
                    if pending['state']=='queued':self.update(pending,state='cancelled',message='İndirilmedi.')
                with self.lock:self.job.update(status='cancelled',message='Kuyruk iptal edildi. Tamamlanmış paketler korundu.')
                return
            except Exception as error:
                message=str(error) if isinstance(error,ValueError) else 'Paket hazırlanamadı. Mevcut dosyalar korundu.'
                self.update(item,state='error',message=message)
            with self.lock:self.job['done']+=1
        with self.lock:
            errors=sum(x['state']=='error' for x in self.job['items'])
            self.job.update(status='partial' if errors else 'complete',message=f'Kuyruk tamamlandı. {errors} paket hazırlanamadı.' if errors else 'Seçilen paketler hazır. Mevcut olanlar korundu.')
